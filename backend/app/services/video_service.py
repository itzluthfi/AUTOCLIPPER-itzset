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

async def download_video(youtube_url: str, video_id: str, cookie_path: Optional[str] = None, sub_lang: str = "id") -> Optional[str]:
    """Download video dari YouTube, return path ke file.

    Menggunakan smart fallback chain 5-tahap untuk mengatasi:
    - Android client tidak support cookies (skip ketika cookie diberikan)
    - YouTube SABR experiment (format hilang di beberapa client)
    - n-challenge JS solver hilang (beberapa client punya workaround)
    - Age-restricted & private video (butuh cookie + client yang benar)
    """
    output_path = os.path.join(DOWNLOAD_DIR, video_id)
    os.makedirs(output_path, exist_ok=True)
    langs_pref = "id,id-orig,en,auto" if sub_lang == "id" else "en,en-orig,id,auto"
    has_cookie = bool(cookie_path and os.path.exists(cookie_path))

    def _base_cmd(client_args: str, fmt: str, with_subs: bool = True) -> list:
        """Bangun command yt-dlp dengan parameter tertentu."""
        c = [
            *get_ytdlp_cmd(),
            "--no-playlist",
            "--extractor-args", f"youtube:player_client={client_args}",
            "-f", fmt,
            "-o", os.path.join(output_path, "%(id)s.%(ext)s"),
        ]
        if with_subs:
            c += ["--write-subs", "--write-auto-subs", "--sub-langs", langs_pref]
        if has_cookie:
            c += ["--cookies", cookie_path]
        c.append(youtube_url)
        return c

    # 5-tahap fallback chain, berhenti saat salah satu berhasil
    # Catatan: android tidak support cookies, jadi jika ada cookie, skip android di tahap 1
    strategies = [
        # Tahap 1: Strategi terbaik — android (tanpa cookie) + web + tv, dengan subtitle
        ("android,web,tv", "bv*[height<=720]+ba/b[height<=720]/b/best", True),
        # Tahap 2: web+tv saja (aman dengan cookie), dengan subtitle
        ("web,tv", "bv*[height<=720]+ba/b[height<=720]/b/best", True),
        # Tahap 3: web saja + format paling fleksibel, tanpa subtitle
        ("web", "b[height<=720]/b/best", False),
        # Tahap 4: mweb (YouTube versi mobile web) — kadang lolos SABR
        ("mweb,web", "b/best", False),
        # Tahap 5: Last resort — biarkan yt-dlp pilih client sendiri
        ("all", "b/best", False),
    ]

    last_stderr = ""
    for idx, (client, fmt, with_subs) in enumerate(strategies):
        # Jika ada cookie, skip strategi yang pakai android (tidak kompatibel)
        if has_cookie and "android" in client and not any(c in client for c in ["web", "tv"]):
            logger.info(f"[download] Strategi {idx+1} skip (android+cookie inkompatibel)")
            continue

        cmd = _base_cmd(client, fmt, with_subs)
        logger.info(f"[download] Mencoba strategi {idx+1}/5 — client={client}, fmt={fmt}, subs={with_subs}")
        try:
            returncode, stdout, stderr = await asyncio.to_thread(_run_cmd_sync, cmd)
            last_stderr = stderr.decode(errors="ignore")
            if returncode == 0:
                logger.info(f"[download] Berhasil dengan strategi {idx+1}")
                break
            else:
                logger.warning(f"[download] Strategi {idx+1} gagal (code={returncode}): {last_stderr[-300:]}")
        except Exception as e:
            logger.error(f"[download] Strategi {idx+1} exception: {e}")
            last_stderr = str(e)

    # Cari file video yang berhasil terunduh
    if os.path.exists(output_path):
        for f in sorted(os.listdir(output_path)):
            if f.endswith((".mp4", ".mkv", ".webm")):
                return os.path.join(output_path, f)

    logger.error(f"[download] Semua strategi gagal. Stderr terakhir: {last_stderr[-500:]}")
    return None

async def extract_subtitles(video_path: str, output_dir: str, sub_lang: str = "id") -> Optional[str]:
    """Ekstrak subtitle dari video. Return path ke file srt/vtt atau None."""
    folder = os.path.dirname(video_path)
    if not os.path.exists(folder):
        return None

    files = os.listdir(folder)
    # 1. Cari file subtitle yang sesuai bahasa (mis. .id.vtt, .id.srt, .id-orig.vtt)
    pref_tag = f".{sub_lang}."
    for f in files:
        if f.endswith((".vtt", ".srt", ".ass")) and (pref_tag in f.lower() or f"{sub_lang}-orig" in f.lower()):
            return os.path.join(folder, f)

    # 2. Fallback ke sembarang file subtitle yang ada
    for f in files:
        if f.endswith((".vtt", ".srt", ".ass")):
            return os.path.join(folder, f)

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

def generate_tts_audio(text: str, output_path: str, lang: str = "id") -> bool:
    """Buat file audio MP3 dari teks judul hook menggunakan gTTS"""
    try:
        from gtts import gTTS
        clean_text = text.replace('"', '').replace("'", "").replace(":", "").strip()
        if not clean_text:
            return False
        tts = gTTS(text=clean_text[:120], lang=lang if lang in ["id", "en"] else "id")
        tts.save(output_path)
        return os.path.exists(output_path)
    except Exception as e:
        logger.error(f"TTS generation error: {e}")
        return False

def analyze_clip_framing(video_path: str, start: float, end: float) -> str:
    """
    Analisis visual cerdas (OpenCV):
    - Sampel frame pada rentang klip [start, end].
    - Hitung jumlah wajah & pergerakan (motion difference).
    - Return mode terbaik: 'speaker' (split screen 2+ orang), 'face' (1 orang face track), 'center' (sports/gaming/produk).
    """
    if not video_path or not os.path.exists(video_path):
        return "face"

    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return "face"

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        start_frame = int(start * fps)
        end_frame = int(end * fps)
        sample_step = max(1, (end_frame - start_frame) // 8)

        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(cascade_path) if os.path.exists(cascade_path) else None

        max_faces_seen = 0
        motion_score = 0
        prev_gray = None
        sampled_count = 0

        for f_idx in range(start_frame, end_frame, sample_step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
            ret, frame = cap.read()
            if not ret or frame is None:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sampled_count += 1

            if face_cascade:
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=4, minSize=(60, 60))
                max_faces_seen = max(max_faces_seen, len(faces))

            if prev_gray is not None:
                diff = cv2.absdiff(gray, prev_gray)
                _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                motion_score += cv2.countNonZero(thresh)

            prev_gray = gray

        cap.release()

        # Logika Keputusan Framing Cerdas (Intelligent Mix Combo)
        if max_faces_seen >= 2:
            logger.info(f"OpenCV Framing [{start:.1f}s-{end:.1f}s]: 2+ Wajah terdeteksi -> Mode Split Screen")
            return "speaker"
        elif max_faces_seen == 1:
            logger.info(f"OpenCV Framing [{start:.1f}s-{end:.1f}s]: 1 Wajah terdeteksi -> Mode Face Track")
            return "face"
        elif motion_score > 500000 and sampled_count > 0:
            logger.info(f"OpenCV Framing [{start:.1f}s-{end:.1f}s]: Pergerakan tinggi / Non-Wajah -> Mode Motion Focus")
            return "center"
        else:
            return "face"
    except Exception as e:
        logger.error(f"Error analyzing clip framing: {e}")
        return "face"

SUBTITLE_STYLE_PRESETS = {
    "tiktok_yellow": "FontName=Arial,FontSize=24,PrimaryColour=&H0000FFFF,SecondaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=3,Outline=3,Bold=1,MarginV=50,Alignment=2",
    "clean_caption": "FontName=Trebuchet MS,FontSize=20,PrimaryColour=&H00FFFFFF,SecondaryColour=&H0000FFFF,OutlineColour=&H00000000,BackColour=&HCC000000,BorderStyle=4,Outline=0,Bold=1,MarginV=40,Alignment=2",
    "neon_cyber": "FontName=Impact,FontSize=26,PrimaryColour=&H00FFFF00,SecondaryColour=&H0000FFFF,OutlineColour=&H00FF00FF,BackColour=&H00000000,BorderStyle=1,Outline=2,Bold=1,MarginV=55,Alignment=2",
    "minimal_movie": "FontName=Helvetica,FontSize=18,PrimaryColour=&H00FFFFFF,SecondaryColour=&H0000FFFF,OutlineColour=&H00000000,BackColour=&H00000000,BorderStyle=1,Outline=1,Bold=0,MarginV=25,Alignment=2",
}

def convert_srt_to_word_highlight_ass(
    srt_path: str,
    ass_path: str,
    sub_style_key: str = "tiktok_yellow",
    sub_anim: str = "word_pop"
) -> str:
    """Mengubah SRT/VTT menjadi file ASS dengan Real-Time Word Highlighting Karaoke (\\kf)"""
    if not srt_path or not os.path.exists(srt_path):
        return srt_path

    style_str = SUBTITLE_STYLE_PRESETS.get(sub_style_key, SUBTITLE_STYLE_PRESETS["tiktok_yellow"])

    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,24,&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,3,3,0,2,20,20,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    try:
        with open(srt_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        import re
        blocks = re.split(r"\n\s*\n", content.strip())
        dialogue_lines = []

        for block in blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            time_line = None
            text_lines = []
            for line in lines:
                if "-->" in line:
                    time_line = line
                elif not line.isdigit() and time_line:
                    text_lines.append(line)

            if not time_line or not text_lines:
                continue

            parts = time_line.split("-->")
            start_str = parts[0].strip().replace(",", ".")
            end_str = parts[1].strip().split()[0].replace(",", ".")

            def _to_sec(ts):
                t_parts = ts.split(":")
                if len(t_parts) == 3:
                    return int(t_parts[0])*3600 + int(t_parts[1])*60 + float(t_parts[2])
                return 0.0

            s_sec = _to_sec(start_str)
            e_sec = _to_sec(end_str)
            dur_sec = max(0.4, e_sec - s_sec)

            raw_text = " ".join(text_lines)
            words = raw_text.split()
            if not words:
                continue

            if sub_anim == "word_pop":
                chunk_size = 3
                for c in range(0, len(words), chunk_size):
                    chunk_words = words[c:c+chunk_size]
                    chunk_dur = (len(chunk_words) / len(words)) * dur_sec
                    c_start = s_sec + (c / len(words)) * dur_sec
                    c_end = c_start + chunk_dur
                    word_cs = int((chunk_dur / max(1, len(chunk_words))) * 100)

                    c_start_fmt = f"{int(c_start//3600)}:{int((c_start%3600)//60):02d}:{c_start%60:05.2f}"
                    c_end_fmt = f"{int(c_end//3600)}:{int((c_end%3600)//60):02d}:{c_end%60:05.2f}"

                    kf_text = "".join([f"{{\\kf{word_cs}}}{w} " for w in chunk_words]).strip()
                    dialogue_lines.append(f"Dialogue: 0,{c_start_fmt},{c_end_fmt},Default,,0,0,0,,{kf_text}")
            else:
                s_fmt = f"{int(s_sec//3600)}:{int((s_sec%3600)//60):02d}:{s_sec%60:05.2f}"
                e_fmt = f"{int(e_sec//3600)}:{int((e_sec%3600)//60):02d}:{e_sec%60:05.2f}"
                dialogue_lines.append(f"Dialogue: 0,{s_fmt},{e_fmt},Default,,0,0,0,,{raw_text}")

        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass_header + "\n".join(dialogue_lines))

        return ass_path if os.path.exists(ass_path) else srt_path
    except Exception as e:
        logger.error(f"Error converting SRT to ASS karaoke: {e}")
        return srt_path

async def clip_video(
    video_path: str,
    output_path: str,
    start: float,
    end: float,
    segments: Optional[list[dict]] = None,
    tracking: str = "none",
    video_template: str = "9:16_crop",
    sub_style: str = "tiktok_yellow",
    sub_anim: str = "word_pop",
    add_subtitle: bool = False,
    subtitle_path: Optional[str] = None,
    title: Optional[str] = None,
    sub_lang: str = "id"
) -> bool:
    """Klip video + Multi-Aspect Ratio (9:16 Crop, 9:16 Blur Background, 16:9 Landscape) + Tracking + Subtitle + Hook Title Overlay"""
    duration = end - start
    if duration <= 0:
        logger.error(f"Invalid clip range: start={start} end={end}")
        return False
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Jika mode tracking 'auto' atau 'mix', lakukan analisis OpenCV dinamis per-klip
    effective_tracking = tracking
    if tracking in ["auto", "mix"]:
        effective_tracking = analyze_clip_framing(video_path, start, end)

    # Buat audio TTS Voiceover hook jika title disediakan
    tts_audio_path = None
    if title:
        candidate_tts_path = os.path.join(os.path.dirname(output_path), f"tts_{os.path.basename(output_path)}.mp3")
        if generate_tts_audio(title, candidate_tts_path, lang=sub_lang):
            tts_audio_path = candidate_tts_path

    burn_subs = bool(add_subtitle and subtitle_path and os.path.exists(subtitle_path))
    has_voiceover = bool(tts_audio_path)
    is_speaker_split = effective_tracking == "speaker"
    filter_complex = True

    video_chain: list[str] = []

    # 0. Multi-Segment Trimming & Concat (Gabungkan beberapa poin momen terhubung menjadi 1 klip padat)
    has_multi_segments = bool(segments and len(segments) >= 2)
    if has_multi_segments:
        seg_v_filters = []
        for idx, seg in enumerate(segments):
            s_t = seg["start"]
            e_t = seg["end"]
            seg_v_filters.append(f"[0:v]trim=start={s_t}:end={e_t},setpts=PTS-STARTPTS[vseg{idx}]")
            seg_v_filters.append(f"[0:a]atrim=start={s_t}:end={e_t},asetpts=PTS-STARTPTS[aseg{idx}]")

        num_s = len(segments)
        v_inputs = "".join([f"[vseg{i}]" for i in range(num_s)])
        a_inputs = "".join([f"[aseg{i}]" for i in range(num_s)])
        seg_v_filters.append(f"{v_inputs}{a_inputs}concat=n={num_s}:v=1:a=1[vraw][araw]")

        video_chain.extend(seg_v_filters)
        source_v_label = "vraw"
        source_a_label = "araw"
    else:
        source_v_label = "0:v"
        source_a_label = "0:a"
    
    # 1. Tahap Freeze Frame / Pause di awal video jika ada Hook Title & TTS
    if has_voiceover:
        video_chain.append(f"[{source_v_label}]tpad=start_duration=2.5:start_mode=clone[vfrozen]")
        current_label = "vfrozen"
    else:
        current_label = source_v_label

    # 2. Tahap Framing & Video Template
    if video_template in ["16:9", "16:9_landscape"]:
        # Full Landscape Horizontal (Original 16:9 tanpa crop)
        video_chain.append(f"[{current_label}]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[vframe]")
        current_label = "vframe"
    elif video_template == "9:16_blur":
        # Video Landscape Utuh di Tengah Frame Vertikal 9:16 + Blurred Background
        video_chain.append(
            f"[{current_label}]split[vbg][vfg];"
            f"[vbg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:10[vblur];"
            f"[vfg]scale=1080:607:force_original_aspect_ratio=decrease[vmain];"
            f"[vblur][vmain]overlay=(W-w)/2:(H-h)/2[vframe]"
        )
        current_label = "vframe"
    elif video_template == "9:16_card":
        # Floating Glassmorphism Card di atas Background Gelap
        video_chain.append(
            f"[{current_label}]split[vbg][vfg];"
            f"[vbg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:10,drawbox=color=black@0.4:t=fill[vblur];"
            f"[vfg]scale=1000:562:force_original_aspect_ratio=decrease,pad=1000:562:(ow-iw)/2:(oh-ih)/2[vmain];"
            f"[vblur][vmain]overlay=(W-w)/2:(H-h)/2[vframe]"
        )
        current_label = "vframe"
    elif video_template == "9:16_podcast" or is_speaker_split:
        if is_speaker_split:
            # Dideteksi 2+ Wajah / Pembicara -> Podcast Split-Screen 2 Panel (Atas & Bawah 960px)
            video_chain.append(
                f"[{current_label}]crop=iw/2:ih:0:0,scale=1080:960[vtop];"
                f"[{current_label}]crop=iw/2:ih:iw/2:0,scale=1080:960[vbot];"
                f"[vtop][vbot]vstack=inputs=2[vframe]"
            )
            current_label = "vframe"
        else:
            # Dideteksi 1 Pembicara Saja -> Otomatis Switch ke 1-Speaker Face Track Vertikal Full Height (1080x1920)
            video_chain.append(f"[{current_label}]crop=ih*9/16:ih,scale=1080:1920[vframe]")
            current_label = "vframe"
    else:
        # Default: 9:16 Crop Vertikal (Smart Face Track 9:16)
        video_chain.append(f"[{current_label}]crop=ih*9/16:ih,scale=1080:1920[vframe]")
        current_label = "vframe"

    stage = 0
    def _chain_filter(filter_str: str):
        nonlocal stage, current_label
        stage += 1
        next_label = f"v{stage}"
        video_chain.append(f"[{current_label}]{filter_str}[{next_label}]")
        current_label = next_label

    # 3. Subtitle Preset (TikTok Yellow, Clean Box, Neon Cyber, Minimal) + Real-time Karaoke Highlight (\kf)
    if burn_subs:
        ass_sub_path = os.path.join(os.path.dirname(output_path), f"subs_{os.path.basename(output_path)}.ass")
        final_sub_path = convert_srt_to_word_highlight_ass(subtitle_path, ass_sub_path, sub_style, sub_anim)
        escaped_sub = final_sub_path.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        sub_filter = f"subtitles='{escaped_sub}'"
        _chain_filter(sub_filter)

    # 4. Title Card Text Overlay selama pause awal (detik 0 - 2.8)
    if title:
        safe_title = title.replace("'", "").replace(":", " ").replace("\\", "")[:45]
        title_overlay = f"drawtext=text='{safe_title}':x=(w-text_w)/2:y=h*0.16:fontsize=44:fontcolor=yellow:box=1:boxcolor=black@0.8:boxborderw=12:enable='between(t,0,2.8)'"
        _chain_filter(title_overlay)

    video_out_label = current_label

    # ── Rantai filter audio: Pause audio asli 2.5s selama TTS voiceover membaca judul ──
    audio_chain: list[str] = []
    audio_out_label = None
    if has_voiceover:
        # Tunda audio asli video selama 2.5 detik (2500ms) agar pas dengan pause frame
        audio_chain.append(f"[{source_a_label}]adelay=2500|2500[a_delayed]")
        audio_chain.append("[1:a]volume=1.8[avoice]")
        audio_chain.append("[a_delayed][avoice]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[aout]")
        audio_out_label = "aout"

    if has_multi_segments:
        seek_args = ["-i", video_path]
    elif burn_subs:
        seek_args = ["-i", video_path, "-ss", str(start)]
    else:
        seek_args = ["-ss", str(start), "-i", video_path]

    cmd = [get_ffmpeg_cmd(), *seek_args]
    if has_voiceover:
        cmd.extend(["-i", tts_audio_path])
    if not has_multi_segments:
        cmd.extend(["-t", str(min(duration + (2.5 if has_voiceover else 0), 65))])

    full_graph = ";".join(video_chain + audio_chain)
    cmd.extend(["-filter_complex", full_graph, "-map", f"[{video_out_label}]"])
    if audio_out_label:
        cmd.extend(["-map", f"[{audio_out_label}]"])
    else:
        cmd.extend(["-map", f"{source_a_label}?"])

    # High Quality Render Parameters (-crf 19 untuk 1080p jernih, audio 192k)
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-y", output_path
    ])

    try:
        returncode, stdout, stderr = await asyncio.to_thread(_run_cmd_sync, cmd)
        if tts_audio_path and os.path.exists(tts_audio_path):
            try:
                os.remove(tts_audio_path)
            except OSError:
                pass
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
        "--extractor-args", "youtube:player_client=android,web,tv",
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
