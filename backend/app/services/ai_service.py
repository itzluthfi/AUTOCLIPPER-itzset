import json
import logging
from openai import AsyncOpenAI
from app.config import NOVITA_API_KEY, NOVITA_BASE_URL, NOVITA_MODEL

logger = logging.getLogger(__name__)

client = None
if NOVITA_API_KEY:
    client = AsyncOpenAI(
        api_key=NOVITA_API_KEY,
        base_url=NOVITA_BASE_URL,
    )

async def detect_highlights(transcript: str, title: str = "", duration: int = 0) -> list[dict]:
    if not client:
        return _fallback_heuristic(transcript, duration)

    prompt = f"""Kamu adalah asisten yang membantu memilih momen penting dari transcript video YouTube untuk dibuat video short (30-60 detik).

Judul video: {title}
Durasi video: {duration} detik

Transcript:
{transcript}

Pilih 3-5 momen paling menarik untuk dijadikan YouTube Shorts.
Setiap momen harus 30-60 detik.
Berikan timestamp mulai, timestamp selesai, dan alasan kenapa momen itu menarik.

Format JSON array saja, tanpa markdown:
[
  {{"start": <detik>, "end": <detik>, "reason": "alasan"}}
]"""

    try:
        resp = await client.chat.completions.create(
            model=NOVITA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
        )
        text = resp.choices[0].message.content.strip()
        # Bersihin markdown code block
        text = text.replace("```json", "").replace("```", "").strip()
        moments = json.loads(text)
        if isinstance(moments, list) and len(moments) > 0:
            return moments
        return _fallback_heuristic(transcript, duration)
    except Exception as e:
        logger.error(f"AI highlight detection failed: {e}")
        return _fallback_heuristic(transcript, duration)

async def generate_title(transcript: str, video_title: str) -> str:
    if not client:
        return f"Klip dari: {video_title[:100]}"

    prompt = f"""Buat judul menarik untuk YouTube Short dari video ini.
Video asli: {video_title}
Isi klip: {transcript[:500]}

Buat 1 judul pendek (max 60 karakter) dalam bahasa Indonesia:"""

    try:
        resp = await client.chat.completions.create(
            model=NOVITA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100,
        )
        return resp.choices[0].message.content.strip()[:100]
    except:
        return f"Klip dari: {video_title[:100]}"

def _fallback_heuristic(transcript: str, duration: int = 0) -> list[dict]:
    """Heuristic: segmen berdasarkan kata kunci atau interval waktu video"""
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
    for seg in segments[:5]:
        moments.append({
            "start": max(0, seg["index"] * 5),
            "end": min(seg["index"] * 5 + 45, seg["index"] * 5 + 60),
            "reason": f"Momen menarik: {seg['text'][:50]}..."
        })

    # Jika momen kurang dari 3, buat variasi interval otomatis berdasarkan durasi video
    if len(moments) < 3:
        dur = max(duration, 180)
        interval = max(45, dur // 4)
        moments = [
            {"start": 5, "end": min(dur, 50), "reason": "Highlights Pembukaan Video"},
            {"start": min(dur - 60, interval), "end": min(dur - 15, interval + 45), "reason": "Highlights Momen Kunci Video"},
            {"start": min(dur - 50, interval * 2), "end": min(dur - 5, interval * 2 + 45), "reason": "Highlights Momen Klimaks Video"},
        ]

    return moments[:5]
