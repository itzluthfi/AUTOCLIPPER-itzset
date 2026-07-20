import os
import shutil
import asyncio
import logging
from celery import Celery
from sqlalchemy.pool import NullPool

from app.config import REDIS_URL, DOWNLOAD_DIR, CLIPS_DIR, NOVITA_API_KEY, DATABASE_URL

logger = logging.getLogger(__name__)

celery_app = Celery(
    "autoclipper",
    broker=REDIS_URL,
    backend=REDIS_URL,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)

celery_app.conf.update(
    task_track_started=True,
    task_time_limit=1200,
    task_soft_time_limit=1080,
    worker_max_tasks_per_child=5,
    worker_concurrency=1,
)


def _make_session_factory():
    """Engine baru per task-run agar aman dipakai di event loop yang berbeda-beda
    (Celery worker maupun thread fallback lokal)."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    connect_args = {}
    if DATABASE_URL.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    engine = create_async_engine(DATABASE_URL, connect_args=connect_args, poolclass=NullPool)
    return engine, async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _clamp_moments(moments: list, duration: int) -> list:
    """Validasi hasil AI/heuristik: pastikan rentang masuk akal dan di dalam durasi video."""
    cleaned = []
    for m in moments:
        try:
            start = max(0.0, float(m.get("start", 0)))
            end = float(m.get("end", start + 45))
        except (TypeError, ValueError):
            continue
        if duration and duration > 0:
            start = min(start, max(0, duration - 15))
            end = min(end, duration)
        if end - start < 10:
            end = start + 30
            if duration and duration > 0:
                end = min(end, duration)
        if end - start < 5:
            continue
        end = min(end, start + 90)
        cleaned.append({"start": start, "end": end, "reason": str(m.get("reason", ""))[:500]})
    return cleaned[:5]


async def _process_video_async(video_id: int, youtube_url: str, user_id: int,
                               mode: str = "heuristic", tracking: str = "auto",
                               num_clips: int = 5, sub_lang: str = "id"):
    from sqlalchemy import select
    from app.models.models import Video, Clip, User, CreditTransaction
    from app.services.video_service import (
        download_video, extract_subtitles, transcribe_audio,
        parse_subtitle_to_text, clip_video, get_video_info, detect_audio_peaks,
    )
    from app.services.ai_service import detect_highlights, generate_title, _fallback_heuristic

    engine, session_factory = _make_session_factory()
    download_dir = os.path.join(DOWNLOAD_DIR, str(video_id))
    num_clips = max(1, min(10, num_clips))

    async def set_state(status: str = None, progress: int = None, step_log: str = None, error: str = None):
        async with session_factory() as session:
            result = await session.execute(select(Video).where(Video.id == video_id))
            video = result.scalar_one_or_none()
            if not video:
                return
            if status is not None:
                video.status = status
            if progress is not None:
                video.progress = progress
            if step_log is not None:
                video.current_step_log = step_log
            if error is not None:
                video.error_message = error[:2000]
            await session.commit()

    try:
        # 0. Ambil cookie pengguna lebih dulu (dipakai untuk metadata & download —
        # video privat/age-restricted butuh cookie sejak pengambilan info juga).
        user_cookie_path = None
        async with session_factory() as session:
            res = await session.execute(select(User).where(User.id == user_id))
            usr = res.scalar_one_or_none()
            if usr and usr.cookie_path and os.path.exists(usr.cookie_path):
                user_cookie_path = usr.cookie_path

        # 1. Info video
        await set_state(status="downloading", progress=5, step_log="[1/5] Inisialisasi antrean video & mengambil metadata YouTube...")
        info = await get_video_info(youtube_url, cookie_path=user_cookie_path)
        async with session_factory() as session:
            result = await session.execute(select(Video).where(Video.id == video_id))
            video = result.scalar_one_or_none()
            if video:
                video.youtube_id = info.get("id", video.youtube_id)
                video.title = info.get("title", video.title)
                video.description = info.get("description", video.description)
                video.duration_seconds = info.get("duration", video.duration_seconds) or 0
                video.status = "downloading"
                video.progress = 10
                video.current_step_log = "[1/5] Metadata YouTube terverifikasi & memulai unduhan..."
                await session.commit()

        await set_state(status="downloading", progress=15, step_log="[2/5] Mengunduh stream video 1080p & file subtitle...")
        video_path = await download_video(youtube_url, str(video_id), cookie_path=user_cookie_path, sub_lang=sub_lang)
        if not video_path:
            raise Exception("Gagal mengunduh video dari YouTube")

        await set_state(status="subtitling", progress=25, step_log="[3/5] Mengurai percakapan subtitle & memindai audio peak volume...")

        # 3. Subtitle / transcript & audio peak detection
        sub_path = await extract_subtitles(video_path, download_dir, sub_lang=sub_lang)
        if not sub_path:
            sub_path = await transcribe_audio(video_path, download_dir)
        transcript = await parse_subtitle_to_text(sub_path or "")
        
        audio_peaks = await detect_audio_peaks(video_path)

        await set_state(status="detecting", progress=45, step_log="[4/5] Menganalisis momen viral via Router LLM (DeepSeek) & Traffic Heatmap...")

        # 4. Deteksi highlight — Multi-modal (Text + Traffic Heatmap + Audio Peaks)
        use_ai = (mode == "ai") and bool(NOVITA_API_KEY)
        duration = info.get("duration", 0) or 0
        heatmap_data = info.get("heatmap", [])

        if use_ai and transcript:
            moments = await detect_highlights(
                transcript=transcript,
                title=info.get("title", ""),
                duration=duration,
                num_clips=num_clips,
                heatmap_data=heatmap_data,
                audio_peaks=audio_peaks
            )
        else:
            moments = _fallback_heuristic(transcript, duration, num_clips)
            
        moments = _clamp_moments(moments, duration)
        if not moments:
            moments = _clamp_moments(
                [{"start": 10, "end": 60, "reason": "Pembukaan video"}], duration
            ) or [{"start": 0, "end": min(45, duration or 45), "reason": "Pembukaan video"}]

        # 5. Clipping & Dynamic Framing
        await set_state(status="clipping", progress=60)
        os.makedirs(CLIPS_DIR, exist_ok=True)
        clip_results = []
        
        for i, moment in enumerate(moments):
            progress_step = min(90, 60 + int((i / max(1, len(moments))) * 30))
            
            await set_state(
                status="clipping",
                progress=progress_step,
                step_log=f"[5/5] Analisis Wajah & Motion OpenCV klip {i+1}/{len(moments)}, subtitle & Hook Intro TTS..."
            )
            
            # Generasi judul viral bersih per klip
            moment_text = transcript[int(moment["start"] * 5): int(moment["end"] * 5)] if transcript else ""
            clean_clip_title = await generate_title(moment_text, info.get("title", ""))

            clip_path = os.path.join(CLIPS_DIR, f"clip_{video_id}_{i}.mp4")
            success = await clip_video(
                video_path=video_path,
                output_path=clip_path,
                start=moment["start"],
                end=moment["end"],
                tracking=tracking,
                add_subtitle=bool(sub_path),
                subtitle_path=sub_path,
                title=clean_clip_title,
                sub_lang=sub_lang
            )
            if not success:
                logger.error(f"Clip {i} video {video_id} gagal dibuat")
                continue

            thumb_path = os.path.join(CLIPS_DIR, f"thumb_{video_id}_{i}.jpg")
            try:
                from app.services.video_service import get_ffmpeg_cmd, _run_cmd_sync
                cmd_thumb = [
                    get_ffmpeg_cmd(), "-y",
                    "-ss", str(moment["start"] + 2),
                    "-i", video_path,
                    "-vframes", "1",
                    "-q:v", "2",
                    thumb_path
                ]
                await asyncio.to_thread(_run_cmd_sync, cmd_thumb)
            except Exception as e:
                logger.error(f"Failed to generate thumbnail: {e}")

            clip_results.append({
                "path": clip_path,
                "thumbnail_path": thumb_path,
                "start": moment["start"],
                "end": moment["end"],
                "title": clean_clip_title,
                "reason": moment.get("reason", ""),
            })

        if not clip_results:
            raise Exception("Tidak ada klip yang berhasil dibuat")

        # 6. Simpan DB
        await set_state(status="finalizing", progress=95)
        async with session_factory() as session:
            for c in clip_results:
                clip = Clip(
                    video_id=video_id,
                    title=c["title"],
                    file_path=c["path"],
                    thumbnail_path=c["thumbnail_path"],
                    start_time=c["start"],
                    end_time=c["end"],
                    reason=c["reason"],
                    method=mode,
                    tracking_type=tracking,
                    status="ready",
                )
                session.add(clip)

            result = await session.execute(select(Video).where(Video.id == video_id))
            video = result.scalar_one_or_none()
            if video:
                video.status = "completed"
                video.progress = 100
            await session.commit()

    except Exception as e:
        logger.exception(f"Process video {video_id} failed: {e}")
        await set_state(status="failed", error=str(e))
        # Refund kredit jika gagal
        if mode == "ai":
            try:
                async with session_factory() as session:
                    res = await session.execute(select(User).where(User.id == user_id))
                    usr = res.scalar_one_or_none()
                    if usr:
                        usr.credits += 1
                        session.add(CreditTransaction(
                            user_id=user_id,
                            amount=1,
                            type="refund",
                            description=f"Refund kredit karena gagal memproses video {video_id}",
                        ))
                        await session.commit()
            except Exception:
                logger.exception("Gagal refund kredit")
        raise
    finally:
        try:
            if os.path.isdir(download_dir):
                shutil.rmtree(download_dir, ignore_errors=True)
        except Exception:
            logger.exception("Gagal cleanup download dir")
        await engine.dispose()


def run_process_video(video_id: int, youtube_url: str, user_id: int,
                      mode: str = "heuristic", tracking: str = "auto",
                      num_clips: int = 5, sub_lang: str = "id"):
    """Entry point sinkron — dipakai Celery task maupun thread fallback lokal."""
    return asyncio.run(_process_video_async(video_id, youtube_url, user_id, mode, tracking, num_clips, sub_lang))


@celery_app.task(name="process_video")
def process_video(video_id: int, youtube_url: str, user_id: int,
                  mode: str = "heuristic", tracking: str = "auto",
                  num_clips: int = 5, sub_lang: str = "id"):
    """Proses video: download → subtitle → deteksi highlight → clip → simpan → cleanup."""
    return run_process_video(video_id, youtube_url, user_id, mode, tracking, num_clips, sub_lang)
