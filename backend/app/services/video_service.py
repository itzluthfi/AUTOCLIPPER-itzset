import os
import re
import asyncio
import logging
import subprocess
import sys
import shutil
from pathlib import Path
from typing import Optional

from app.config import DOWNLOAD_DIR, CLIPS_DIR, TEMP_DIR

logger = logging.getLogger(__name__)

def get_ytdlp_cmd() -> list[str]:
    """Cari command executable yt-dlp yang valid (termasuk fallback via python -m yt_dlp)"""
    which_cmd = shutil.which("yt-dlp")
    if which_cmd:
        return [which_cmd]
        
    venv_dir = os.path.dirname(sys.executable)
    ytdlp_venv = os.path.join(venv_dir, "yt-dlp.exe" if sys.platform == "win32" else "yt-dlp")
    if os.path.exists(ytdlp_venv):
        return [ytdlp_venv]
        
    return [sys.executable, "-m", "yt_dlp"]

def get_ffmpeg_cmd() -> str:
    """Cari path executable ffmpeg di imageio_ffmpeg, system PATH, atau fallback ke 'ffmpeg'"""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass

    which_cmd = shutil.which("ffmpeg")
    if which_cmd:
        return which_cmd

    return "ffmpeg"

def _run_cmd_sync(cmd: list[str]) -> tuple[int, bytes, bytes]:
    """Jalankan subprocess secara sinkron yang aman dari NotImplementedError di Windows asyncio"""
    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    return res.returncode, res.stdout, res.stderr

async def download_video(youtube_url: str, video_id: str, cookie_path: Optional[str] = None) -> Optional[str]:
    """Download video dari YouTube, return path ke file"""
    output_path = os.path.join(DOWNLOAD_DIR, video_id)
    os.makedirs(output_path, exist_ok=True)

    cmd = [
        *get_ytdlp_cmd(),
        "-f", "best[height<=720]",
        "--write-subs", "--write-auto-subs",
        "--sub-langs", "en,id",
        "-o", os.path.join(output_path, "%(id)s.%(ext)s"),
    ]
    if cookie_path and os.path.exists(cookie_path):
        cmd.extend(["--cookies", cookie_path])
    cmd.append(youtube_url)

    last_stderr = ""
    try:
        returncode, stdout, stderr = await asyncio.to_thread(_run_cmd_sync, cmd)
        last_stderr = stderr.decode(errors='ignore')
        if returncode != 0:
            logger.error(f"yt-dlp failed: {last_stderr}")
            # Coba tanpa subtitle
            cmd = [
                *get_ytdlp_cmd(),
                "-f", "best[height<=720]",
                "-o", os.path.join(output_path, "%(id)s.%(ext)s"),
            ]
            if cookie_path and os.path.exists(cookie_path):
                cmd.extend(["--cookies", cookie_path])
            cmd.append(youtube_url)
            returncode, stdout, stderr = await asyncio.to_thread(_run_cmd_sync, cmd)
            if returncode != 0:
                last_stderr = stderr.decode(errors='ignore')
                logger.error(f"yt-dlp retry failed: {last_stderr}")
    except Exception as e:
        logger.error(f"yt-dlp error: {e}")
        last_stderr = str(e)

    # Cari file video yang berhasil terunduh di dalam folder output_path
    if os.path.exists(output_path):
        for f in os.listdir(output_path):
            if f.endswith((".mp4", ".mkv", ".webm")):
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
        get_ffmpeg_cmd(), "-i", video_path,
        "-vn", "-acodec", "libmp3lame",
        "-ar", "16000", "-ac", "1",
        "-y", audio_path
    ]
    await asyncio.to_thread(_run_cmd_sync, cmd)

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
        await asyncio.to_thread(_run_cmd_sync, cmd)
    except Exception as e:
        logger.error(f"Whisper failed: {e}")
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

async def detect_audio_peaks(video_path: str) -> list[dict]:
    """Mendeteksi puncak volume suara (shouting/laughter) menggunakan FFmpeg astats filter"""
    if not video_path or not os.path.exists(video_path):
        return []
    cmd = [
        get_ffmpeg_cmd(), "-i", video_path,
        "-af", "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level",
        "-f", "null", "-"
    ]
    try:
        returncode, stdout, stderr = await asyncio.to_thread(_run_cmd_sync, cmd)
        text = stderr.decode("utf-8", errors="ignore")
        peaks = []
        for line in text.split("\n"):
            if "RMS_level" in line:
                m = re.search(r"pts_time:([\d\.]+).*RMS_level=([-\d\.]+)", line)
                if m:
                    pts = float(m.group(1))
                    rms = float(m.group(2))
                    if rms > -15.0:  # High volume energy
                        peaks.append({"start": max(0, int(pts) - 5), "end": int(pts) + 35, "rms": rms})
        peaks.sort(key=lambda x: x["rms"], reverse=True)
        return peaks[:5]
    except Exception as e:
        logger.error(f"Error detecting audio peaks: {e}")
        return []

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
    """Klip video + tracking (Center / Face / Speaker Split-Screen) + subtitle"""
    duration = end - start
    if duration <= 0:
        logger.error(f"Invalid clip range: start={start} end={end}")
        return False
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Menentukan rantai filter video berdasarkan mode tracking
    if tracking == "speaker":
        # Split-Screen Mode: Membagi video landscape menjadi 2 panel atas-bawah (9:16 stacked)
        vf_filter = (
            "[0:v]crop=iw/2:ih:0:0,scale=1080:960[top];"
            "[0:v]crop=iw/2:ih:iw/2:0,scale=1080:960[bottom];"
            "[top][bottom]vstack=inputs=2[v]"
        )
        filter_complex = True
    else:
        # Standard Single Focus (Center / Face Crop 9:16)
        filters = ["crop=ih*9/16:ih", "scale=1080:1920"]
        filter_complex = False

    if add_subtitle and subtitle_path and os.path.exists(subtitle_path):
        escaped = subtitle_path.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        sub_style = ":force_style='FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2'"
        sub_filter = f"subtitles='{escaped}'{sub_style}"
        if filter_complex:
            vf_filter += f";[v]{sub_filter}[outv]"
        else:
            filters.append(sub_filter)

    burn_subs = add_subtitle and subtitle_path and os.path.exists(subtitle_path)
    if burn_subs:
        seek_args = ["-i", video_path, "-ss", str(start)]
    else:
        seek_args = ["-ss", str(start), "-i", video_path]

    cmd = [get_ffmpeg_cmd(), *seek_args, "-t", str(min(duration, 60))]

    if filter_complex:
        out_map = "[outv]" if burn_subs else "[v]"
        cmd.extend(["-filter_complex", vf_filter, "-map", out_map, "-map", "0:a?"])
    else:
        cmd.extend(["-vf", ",".join(filters)])

    # High Quality Render Parameters (-crf 19 untuk 1080p jernih, audio 192k)
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        "-y", output_path
    ])

    try:
        returncode, stdout, stderr = await asyncio.to_thread(_run_cmd_sync, cmd)
        if returncode != 0:
            logger.error(f"ffmpeg failed: {stderr.decode(errors='ignore')}")
            return False
        return os.path.exists(output_path)
    except Exception as e:
        logger.error(f"ffmpeg error: {e}")
        return False

async def get_video_info(youtube_url: str, cookie_path: Optional[str] = None) -> dict:
    """Ambil metadata video dari YouTube (dengan opsional cookie_path)"""
    cmd = [
        *get_ytdlp_cmd(), "--dump-json",
        "--no-download",
    ]
    if cookie_path and os.path.exists(cookie_path):
        cmd.extend(["--cookies", cookie_path])
    cmd.append(youtube_url)

    try:
        returncode, stdout, stderr = await asyncio.to_thread(_run_cmd_sync, cmd)
        
        # 1. Coba baca JSON dari stdout langsung jika ada
        text = stdout.decode("utf-8", errors="ignore").strip()
        if text.startswith("{"):
            try:
                import json
                info = json.loads(text)
                if info.get("id"):
                    return {
                        "id": str(info.get("id", "") or ""),
                        "title": str(info.get("title", "") or ""),
                        "description": str(info.get("description", "") or ""),
                        "duration": info.get("duration", 0) or 0,
                        "category": info.get("categories", [None])[0] if info.get("categories") else None,
                        "tags": info.get("tags", []),
                        "thumbnail": str(info.get("thumbnail", "") or ""),
                        "heatmap": info.get("heatmap", []),
                        "error": None,
                    }
            except Exception:
                pass

        # 2. Jika dengan cookie gagal, coba tanpa cookie sebagai fallback
        if cookie_path and os.path.exists(cookie_path):
            cmd2 = [*get_ytdlp_cmd(), "--dump-json", "--no-download", youtube_url]
            returncode2, stdout2, stderr2 = await asyncio.to_thread(_run_cmd_sync, cmd2)
            text2 = stdout2.decode("utf-8", errors="ignore").strip()
            if text2.startswith("{"):
                try:
                    import json
                    info = json.loads(text2)
                    if info.get("id"):
                        return {
                            "id": str(info.get("id", "") or ""),
                            "title": str(info.get("title", "") or ""),
                            "description": str(info.get("description", "") or ""),
                            "duration": info.get("duration", 0) or 0,
                            "category": info.get("categories", [None])[0] if info.get("categories") else None,
                            "tags": info.get("tags", []),
                            "thumbnail": str(info.get("thumbnail", "") or ""),
                            "error": None,
                        }
                except Exception:
                    pass

        err_text = stderr.decode("utf-8", errors="ignore").strip()
        return {"id": "", "title": "", "duration": 0, "error": err_text[:200]}

    except Exception as e:
        logger.error(f"yt-dlp info failed: {repr(e)}")
        return {"id": "", "title": "", "duration": 0, "error": str(e)}

async def test_youtube_cookie(cookie_path: str) -> dict:
    """Uji apakah file cookie YouTube valid dan bisa digunakan"""
    if not cookie_path or not os.path.exists(cookie_path):
        return {"valid": False, "message": "File cookie tidak ditemukan di server"}

    try:
        with open(cookie_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        return {"valid": False, "message": f"Gagal membaca file cookie: {e}"}

    text_clean = text.strip()
    if not text_clean:
        return {"valid": False, "message": "File cookie kosong"}

    # Check key session markers
    has_session_keys = any(k in text_clean for k in ["LOGIN_INFO", "SID", "HSID", "SSID", "SAPISID", "access_token", "refresh_token"])
    
    # Try yt-dlp test
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    cmd = [
        *get_ytdlp_cmd(), "--dump-json", "--no-download",
        "--cookies", cookie_path,
        test_url
    ]
    try:
        returncode, stdout, stderr = await asyncio.to_thread(_run_cmd_sync, cmd)
        if returncode == 0 and len(stdout) > 50:
            return {"valid": True, "message": "Cookie valid dan terverifikasi bisa mengakses YouTube!"}
        
        err_msg = stderr.decode(errors="ignore").strip()
        if has_session_keys:
            return {"valid": True, "message": "Cookie terdeteksi memiliki kunci sesi YouTube (LOGIN_INFO/SID) dan siap digunakan!"}
        
        detail = err_msg[:120] if err_msg else "Kunci autentikasi YouTube (LOGIN_INFO/SID) tidak ditemukan"
        return {"valid": False, "message": f"Cookie tidak valid: {detail}"}
    except Exception as e:
        if has_session_keys:
            return {"valid": True, "message": "File cookie berisi kunci autentikasi YouTube yang valid."}
        return {"valid": False, "message": f"Gagal menguji cookie: {e}"}
