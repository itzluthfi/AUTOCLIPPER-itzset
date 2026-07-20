import json
import logging
import re
from typing import Optional, List, Dict
from openai import AsyncOpenAI
from app.config import NOVITA_API_KEY, NOVITA_BASE_URL, NOVITA_MODEL

logger = logging.getLogger(__name__)

client = None
if NOVITA_API_KEY:
    client = AsyncOpenAI(
        api_key=NOVITA_API_KEY,
        base_url=NOVITA_BASE_URL,
        default_headers={
            "api-key": NOVITA_API_KEY,
            "X-API-Key": NOVITA_API_KEY,
            "Authorization": f"Bearer {NOVITA_API_KEY}"
        }
    )

def _extract_response_text(resp) -> str:
    """Ekstrak teks balasan LLM dari content atau reasoning/reasoning_content"""
    try:
        msg = resp.choices[0].message
        if msg.content:
            return msg.content.strip()
        reasoning = getattr(msg, "reasoning", None) or getattr(msg, "reasoning_content", None)
        if reasoning:
            return str(reasoning).strip()
        return str(msg).strip()
    except Exception as e:
        logger.error(f"Error extracting response text: {e}")
        return ""

async def detect_highlights(
    transcript: str,
    title: str = "",
    duration: int = 0,
    num_clips: int = 5,
    heatmap_data: Optional[list] = None,
    audio_peaks: Optional[list] = None
) -> list[dict]:
    """Deteksi momen viral (hingga num_clips, max 10) menggunakan LLM / Multi-modal heuristic"""
    num_clips = max(1, min(10, num_clips))

    if not client:
        return _fallback_heuristic(transcript, duration, num_clips)

    heatmap_context = ""
    if heatmap_data:
        heatmap_context = f"\nData Trafik Penonton (Most Replayed Peaks): {json.dumps(heatmap_data[:5])}"

    audio_context = ""
    if audio_peaks:
        audio_context = f"\nPeak Energi Suara (Vocal Loudness Peaks): {json.dumps(audio_peaks[:5])}"

    prompt = f"""Kamu adalah pakar editor video short viral (TikTok, YouTube Shorts, Reels).
Tugasmu: Pilih tepat {num_clips} momen paling menarik & paling tinggi nilai viralnya dari transcript video berikut.

Judul Video: {title}
Durasi Video: {duration} detik{heatmap_context}{audio_context}

Transcript Video:
{transcript[:4000]}

Syarat Hasil:
1. Pilih tepat {num_clips} klip pendek (durasi masing-masing klip 30-60 detik).
2. Klip tidak boleh saling tumpang tindih.
3. Berikan nilai "start" (detik), "end" (detik), dan "reason" (alasan kenapa klip ini viral).

Format Response WAJIB JSON array murni tanpa penjelasan teks atau markdown:
[
  {{"start": 10, "end": 55, "reason": "Hook pembuka yang mengejutkan tentang..."}},
  {{"start": 120, "end": 170, "reason": "Klimaks percakapan emosional..."}}
]"""

    try:
        resp = await client.chat.completions.create(
            model=NOVITA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
        )
        text = _extract_response_text(resp)
        text = text.replace("```json", "").replace("```", "").strip()
        
        # Ekstrak json array jika ada teks di sekitarnya
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            text = match.group(0)

        moments = json.loads(text)
        if isinstance(moments, list) and len(moments) > 0:
            return moments[:num_clips]
        return _fallback_heuristic(transcript, duration, num_clips)
    except Exception as e:
        logger.error(f"AI highlight detection failed: {e}")
        return _fallback_heuristic(transcript, duration, num_clips)

async def auto_detect_video_settings(title: str, description: str = "") -> dict:
    """Membaca metadata video untuk menyarankan mode tracking & preset otomatis via LLM"""
    default_preset = {
        "mode": "ai",
        "tracking": "face",
        "num_clips": 5,
        "reason": "Deteksi otomatis berdasarkan judul & kategori video."
    }
    if not client:
        return default_preset

    prompt = f"""Analisis metadata video YouTube berikut:
Judul: {title}
Deskripsi: {description[:300]}

Tentukan rekomendasi terbaik untuk pembuatan clip 9:16:
1. tracking: "speaker" jika video berupa podcast/wawancara 2 orang, "face" jika vlogger/pembicara tunggal, atau "center" jika pemandangan/gameplay.
2. num_clips: Jumlah klip ideal (3 - 8 klip).

Format WAJIB JSON murni:
{{"tracking": "speaker", "num_clips": 5, "reason": "Podcast 2 orang membutuhkan split-screen speaker tracking."}}"""

    try:
        resp = await client.chat.completions.create(
            model=NOVITA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300,
        )
        text = _extract_response_text(resp)
        text = text.replace("```json", "").replace("```", "").strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            res = json.loads(match.group(0))
            return {
                "mode": "ai",
                "tracking": res.get("tracking", "face"),
                "num_clips": max(1, min(10, int(res.get("num_clips", 5)))),
                "reason": res.get("reason", "Deteksi otomatis LLM")
            }
        return default_preset
    except Exception as e:
        logger.error(f"Auto detect settings failed: {e}")
        return default_preset

async def generate_title(transcript: str, video_title: str) -> str:
    """Buat judul menarik (hook title) untuk klip"""
    if not client:
        return f"Klip: {video_title[:60]}"

    prompt = f"""Buat 1 judul viral pendek (3-7 kata, maksimal 40 karakter) dalam Bahasa Indonesia untuk klip TikTok/Reels ini:
Judul Asli: {video_title}
Teks Percakapan: {transcript[:400]}

PENTING WAJIB:
1. HANYA BALAS DENGAN TEKS JUDUL VIRAL SAJA.
2. DILARANG MENULIS PEMIKIRAN, DILARANG MENULIS 'Hmm', 'User', 'Berikut', 'Tentu', atau Penjelasan.
3. CONTOH BALASAN VALID: Rahasia Sukses Usaha Muda"""

    try:
        resp = await client.chat.completions.create(
            model=NOVITA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50,
        )
        text = _extract_response_text(resp)
        text = text.replace('"', '').replace("'", "").strip()
        
        # Filter & bersihkan baris pemikiran/reasoning AI
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        clean_title = ""
        for line in reversed(lines):
            # Abai baris yang berisi instruksi ulang atau diawali kata kunci reasoning
            if re.match(r"^(hmm|user|berikut|tentu|judul|pilihan|jawab|rekomendasi|analisis)", line, re.IGNORECASE):
                continue
            if len(line) >= 4:
                clean_title = line
                break
        if not clean_title and lines:
            clean_title = lines[-1]
            
        clean_title = re.sub(r"^(hmm,?\s*|user\s+butuh\s*|berikut\s+judul\s*:?\s*)", "", clean_title, flags=re.IGNORECASE).strip()
        return clean_title[:60] or f"Klip: {video_title[:50]}"
    except Exception as e:
        logger.error(f"Generate title error: {e}")
        return f"Klip: {video_title[:50]}"

def _fallback_heuristic(transcript: str, duration: int = 0, num_clips: int = 5) -> list[dict]:
    """Heuristic: segmen berdasarkan kata kunci atau interval waktu video yang merata hingga num_clips (max 10)"""
    num_clips = max(1, min(10, num_clips))
    dur = duration if duration and duration > 30 else 300
    clip_len = 45

    keywords = ["best", "amazing", "wow", "important", "watch this", "wait for it",
                "let me show", "check this", "first", "finally", "kesimpulan", "penting",
                "menarik", "luar biasa", "kunci", "utama", "tips", "rahasia"]

    lines = [l.strip() for l in transcript.split("\n") if l.strip()]
    segments = []
    for i, line in enumerate(lines):
        score = 0
        for kw in keywords:
            if kw.lower() in line.lower():
                score += 2
        if len(line) > 50:
            score += 1
        if score > 0:
            segments.append({"index": i, "text": line[:100], "score": score})

    segments.sort(key=lambda x: x["score"], reverse=True)

    moments = []
    seen_starts = []
    for seg in segments:
        if len(moments) >= num_clips:
            break
        st = max(0, seg["index"] * 5)
        if not any(abs(st - s) < 15 for s in seen_starts):
            seen_starts.append(st)
            moments.append({
                "start": st,
                "end": min(dur, st + clip_len),
                "reason": f"Momen menarik: {seg['text'][:50]}..."
            })

    # Jika jumlah momen kurang dari num_clips, bagi durasi video secara merata menjadi num_clips segmen unik
    if len(moments) < num_clips:
        step = max(clip_len + 5, (dur - 20) // max(1, num_clips))
        for i in range(num_clips):
            if len(moments) >= num_clips:
                break
            st = 10 + i * step
            ed = min(dur - 5, st + clip_len)
            if not any(abs(st - s) < 15 for s in seen_starts):
                seen_starts.append(st)
                moments.append({
                    "start": st,
                    "end": ed,
                    "reason": f"Segmen Momen Highlight #{i + 1}"
                })

    return moments[:num_clips]
