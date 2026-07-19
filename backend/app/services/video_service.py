import os
import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Optional

from app.config import DOWNLOAD_DIR, CLIPS_DIR, TEMP_DIR

logger = logging.getLogger(__name__)

async def download_video(youtube_url: str, video_id: str) -> Optional[str]:
    """Download video dari YouTube, return path ke file"""
    output_path = os.path.join(DOWNLOAD_DIR, video_id)
    os.makedirs(output_path, exist_ok=True)

    cmd = [
        "yt-dlp",
        "-f", "best[height<=720]",
        "--write-subs", "--write-auto-subs",
        "--sub-langs", "en,id",
        "-o", os.path.join(output_path, "%(id)s.%(ext)s"),
        youtube_url
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error(f"yt-dlp failed: {stderr.decode()}")
            # Coba tanpa subtitle
            cmd = [
                "yt-dlp",
                "-f", "best[height<=720]",
                "-o", os.path.join(output_path, "%(id)s.%(ext)s"),
                youtube_url
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                logger.error(f"yt-dlp retry failed: {stderr.decode()}")
                return None
    except Exception as e:
        logger.error(f"yt-dlp error: {e}")
        return None

    # Cari file video
    for f in os.listdir(output_path):
        if f.endswith((".mp4", ".mkv", ".webm")) and video_id in f:
            return os.path.join(output_path, f)

    return None

async def extract_subtitles(video_path: str, output_dir: str) -> Optional[str]:
    """Ekstrak subtitle dari video. Return path ke file srt atau None."""
    # Cek file subtitle yang udah ada
    base = os.path.splitext(video_path)[0]
    for ext in [".srt", ".vtt", ".ass"]:
        sub_file = base + ext
        if os.path.exists(sub_file):
            return sub_file

    # Cari di direktori
    for f in os.listdir(os.path.dirname(video_path)):
        if f.endswith((".srt", ".vtt", ".ass")):
            return os.path.join(os.path.dirname(video_path), f)

    return None

async def transcribe_audio(video_path: str, output_dir: str) -> Optional[str]:
    """Transcribe audio pake Whisper. Return path ke file srt."""
    audio_path = os.path.join(output_dir, "audio.mp3")

    # Ekstrak audio
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "libmp3lame",
        "-ar", "16000", "-ac", "1",
        "-y", audio_path
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()

    if not os.path.exists(audio_path):
        return None

    # Pake whisper CLI
    output_srt = os.path.join(output_dir, "whisper_output.srt")
    cmd = [
        "whisper",
        audio_path,
        "--model", "tiny",
        "--language", "id",
        "--output_format", "srt",
        "--output_dir", output_dir,
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate(timeout=300)
    except:
        return None

    # Cari file srt hasil
    for f in os.listdir(output_dir):
        if f.endswith(".srt") and "whisper" in f:
            return os.path.join(output_dir, f)

    return None

async def parse_subtitle_to_text(subtitle_path: str) -> str:
    """Parse file SRT ke teks polos"""
    if not subtitle_path or not os.path.exists(subtitle_path):
        return ""

    with open(subtitle_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    lines = []
    for line in content.split("\n"):
        line = line.strip()
        if line and not line.isdigit() and "-->" not in line:
            lines.append(line)

    return " ".join(lines)

async def clip_video(
    video_path: str,
    output_path: str,
    start: float,
    end: float,
    tracking: str = "none",
    add_subtitle: bool = False,
    subtitle_path: Optional[str] = None,
    hook: bool = False
) -> bool:
    """Klip video + tracking + subtitle"""
    duration = end - start
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if tracking == "face":
        filter_complex = "[0:v]crop=ih*9/16:ih,scale=1080:1920[v]"
        map_cmd = ["-map", "[v]", "-map", "0:a"]
        vf_cmd = ["-vf", filter_complex]
    else:
        vf_cmd = ["-vf", "crop=ih*9/16:ih,scale=1080:1920"]
        map_cmd = []

    cmd = [
        "ffmpeg", "-ss", str(start), "-i", video_path,
        "-t", str(min(duration, 60)),
        *vf_cmd,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-y", output_path
    ]

    if add_subtitle and subtitle_path and os.path.exists(subtitle_path):
        cmd.insert(-1, "-vf")
        cmd.insert(-1, f"subtitles={subtitle_path}")

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error(f"ffmpeg failed: {stderr.decode()}")
            return False
        return os.path.exists(output_path)
    except Exception as e:
        logger.error(f"ffmpeg error: {e}")
        return False

async def get_video_info(youtube_url: str) -> dict:
    """Ambil metadata video dari YouTube"""
    cmd = [
        "yt-dlp", "--dump-json",
        "--no-download",
        youtube_url
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        import json
        info = json.loads(stdout)
        return {
            "id": info.get("id", ""),
            "title": info.get("title", ""),
            "description": info.get("description", ""),
            "duration": info.get("duration", 0),
            "category": info.get("categories", [None])[0] if info.get("categories") else None,
            "tags": info.get("tags", []),
            "thumbnail": info.get("thumbnail", ""),
        }
    except Exception as e:
        logger.error(f"yt-dlp info failed: {e}")
        return {"id": "", "title": "", "duration": 0}
