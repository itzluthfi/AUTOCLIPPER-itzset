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
                               mode: str = "heuristic", tracking: str = "center"):
    from sqlalchemy import select
    from app.models.models import Video, Clip, User, CreditTransaction
    from app.services.video_service import (
        download_video, extract_subtitles, transcribe_audio,
        parse_subtitle_to_text, clip_video, get_video_info,
    )
    from app.services.ai_service import detect_highlights, generate_title, _fallback_heuristic

    engine, session_factory = _make_session_factory()
    download_dir = os.path.join(DOWNLOAD_DIR, str(video_id))

    async def set_state(status: str = None, progress: int = None, error: str = None):
        async with session_factory() as session:
            result = await session.execute(select(Video).where(Video.id == video_id))
            video = result.scalar_one_or_none()
            if not video:
                return
            if status is not None:
                video.status = status
            if progress is not None:
                video.progress = progress
            if error is not None:
                video.error_message = error[:2000]
            await session.commit()

    try:
        # 1. Info video
        info = await get_video_info(youtube_url)
        async with session_factory() as session:
            result = await session.execute(select(Video).where(Video.id == video_id))
            video = result.scalar_one_or_none()
            if video:
                video.youtube_id = info.get("id", video.youtube_id)
                video.title = info.get("title", video.title)
                video.description = info.get("description", video.description)
                video.duration_seconds = info.get("duration", video.duration_seconds) or 0
                video.status = "downloading"
                video.progress = 5
                await session.commit()

        # 2. Download (dengan cookie pengguna jika tersedia)
        user_cookie_path = None
        async with session_factory() as session:
            res = await session.execute(select(User).where(User.id == user_id))
            usr = res.scalar_one_or_none()
            if usr and usr.cookie_path and os.path.exists(usr.cookie_path):
                user_cookie_path = usr.cookie_path

        video_path = await download_video(youtube_url, str(video_id), cookie_path=user_cookie_path)
        if not video_path:
            raise Exception("Gagal mengunduh video dari YouTube")

        await set_state(status="subtitling", progress=25)

        # 3. Subtitle / transcript
        sub_path = await extract_subtitles(video_path, download_dir)
        if not sub_path:
            sub_path = await transcribe_audio(video_path, download_dir)
        transcript = await parse_subtitle_to_text(sub_path or "")

        await set_state(status="detecting", progress=40)

        # 4. Deteksi highlight — AI hanya jika user memilih mode "ai" DAN key tersedia
        use_ai = (mode == "ai") and bool(NOVITA_API_KEY)
        duration = info.get("duration", 0) or 0
        if use_ai and transcript:
            moments = await detect_highlights(transcript, info.get("title", ""), duration)
        else:
            moments = _fallback_heuristic(transcript, duration)
        moments = _clamp_moments(moments, duration)
        if not moments:
            moments = _clamp_moments(
                [{"start": 10, "end": 60, "reason": "Pembukaan video"}], duration
            ) or [{"start": 0, "end": min(45, duration or 45), "reason": "Pembukaan video"}]

        # 5. Clipping
        await set_state(status="clipping", progress=55)
        os.makedirs(CLIPS_DIR, exist_ok=True)
        clip_results = []
        for i, moment in enumerate(moments):
            clip_path = os.path.join(CLIPS_DIR, f"clip_{video_id}_{i}.mp4")
            success = await clip_video(
                video_path=video_path,
                output_path=clip_path,
                start=moment["start"],
                end=moment["end"],
                tracking=tracking,
                add_subtitle=bool(sub_path),
                subtitle_path=sub_path,
            )
            if not success:
                logger.error(f"Clip {i} video {video_id} gagal dibuat")
                continue

            thumb_path = os.path.join(CLIPS_DIR, f"thumb_{video_id}_{i}.jpg")
            try:
                from app.services.video_service import get_ffmpeg_cmd, _run_cmd_sync
                cmd_thumb = [
                    get_ffmpeg_cmd(), "-y", "-i", clip_path, "-ss", "00:00:01",
                    "-vframes", "1", thumb_path
                ]
                returncode, stdout, stderr = await asyncio.to_thread(_run_cmd_sync, cmd_thumb)
                if returncode != 0 or not os.path.exists(thumb_path):
                    thumb_path = None
            except Exception as e:
                logger.error(f"Gagal generate thumbnail: {e}")
                thumb_path = None

            title = await generate_title(
                (moment["reason"] or transcript[:200]), info.get("title", "")
            )
            clip_results.append({
                "path": clip_path,
                "thumbnail_path": thumb_path,
                "start": moment["start"],
                "end": moment["end"],
                "reason": moment["reason"],
                "title": title,
            })
            await set_state(progress=55 + int((i + 1) / len(moments) * 35))

        if not clip_results:
            raise Exception("Tidak ada klip yang berhasil dibuat")

        # 6. Simpan ke DB + selesai
        await set_state(status="finalizing", progress=95)
        async with session_factory() as session:
            result = await session.execute(select(Video).where(Video.id == video_id))
            video = result.scalar_one_or_none()
            if video:
                video.status = "completed"
                video.progress = 100
                video.file_path = None  # sumber dihapus setelah selesai
                for cr in clip_results:
                    session.add(Clip(
                        video_id=video_id,
                        start_time=cr["start"],
                        end_time=cr["end"],
                        reason=cr["reason"],
                        method="ai" if use_ai else "heuristic",
                        tracking_type=tracking,
                        file_path=cr["path"],
                        thumbnail_path=cr["thumbnail_path"],
                        status="ready",
                        title=cr["title"],
                    ))
                await session.commit()

        return {"video_id": video_id, "clips_created": len(clip_results)}

    except Exception as e:
        logger.exception(f"Process video {video_id} failed")
        await set_state(status="failed", progress=0, error=str(e))
        # Refund kredit jika mode AI (kredit dipotong saat submit)
        if mode == "ai":
            try:
                async with session_factory() as session:
                    result = await session.execute(select(User).where(User.id == user_id))
                    user = result.scalar_one_or_none()
                    if user:
                        user.credits += 1
                        session.add(CreditTransaction(
                            user_id=user_id, amount=1, type="refund",
                            description=f"Refund: proses video #{video_id} gagal",
                        ))
                        await session.commit()
            except Exception:
                logger.exception("Gagal refund kredit")
        raise
    finally:
        # Cleanup file download (video sumber + subtitle + audio temp)
        try:
            if os.path.isdir(download_dir):
                shutil.rmtree(download_dir, ignore_errors=True)
        except Exception:
            logger.exception("Gagal cleanup download dir")
        await engine.dispose()


def run_process_video(video_id: int, youtube_url: str, user_id: int,
                      mode: str = "heuristic", tracking: str = "center"):
    """Entry point sinkron — dipakai Celery task maupun thread fallback lokal."""
    return asyncio.run(_process_video_async(video_id, youtube_url, user_id, mode, tracking))


@celery_app.task(name="process_video")
def process_video(video_id: int, youtube_url: str, user_id: int,
                  mode: str = "heuristic", tracking: str = "center"):
    """Proses video: download → subtitle → deteksi highlight → clip → simpan → cleanup."""
    return run_process_video(video_id, youtube_url, user_id, mode, tracking)
