import os
import json
import asyncio
import logging
from celery import Celery
from app.config import REDIS_URL, DOWNLOAD_DIR, CLIPS_DIR, TEMP_DIR, NOVITA_API_KEY

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
    task_time_limit=600,
    task_soft_time_limit=540,
    worker_max_tasks_per_child=5,
    worker_concurrency=1,
)

@celery_app.task(bind=True, name="process_video")
def process_video(self, video_id: int, youtube_url: str, user_id: int):
    """Process video: download → detect → clip → cleanup"""
    from app.database import async_session
    from app.models.models import Video, Clip
    from app.services.video_service import (
        download_video, extract_subtitles, transcribe_audio,
        parse_subtitle_to_text, clip_video, get_video_info
    )
    from app.services.ai_service import detect_highlights, generate_title

    self.update_state(state="PROGRESS", meta={"step": "download", "progress": 0})

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # 1. Get info
        info = loop.run_until_complete(get_video_info(youtube_url))
        video_id_yt = info.get("id", "")

        # 2. Update DB
        async def update_video_info():
            async with async_session() as session:
                from sqlalchemy import select
                result = await session.execute(select(Video).where(Video.id == video_id))
                video = result.scalar_one_or_none()
                if video:
                    video.youtube_id = video_id_yt
                    video.title = info.get("title", "")
                    video.description = info.get("description", "")
                    video.duration_seconds = info.get("duration", 0)
                    video.status = "downloading"
                    await session.commit()

        loop.run_until_complete(update_video_info())

        # 3. Download
        video_path = loop.run_until_complete(download_video(youtube_url, str(video_id)))
        if not video_path:
            raise Exception("Download failed")

        self.update_state(state="PROGRESS", meta={"step": "subtitle", "progress": 20})

        # 4. Extract subtitle
        sub_dir = os.path.join(DOWNLOAD_DIR, str(video_id))
        sub_path = loop.run_until_complete(extract_subtitles(video_path, sub_dir))
        if not sub_path:
            sub_path = loop.run_until_complete(transcribe_audio(video_path, sub_dir))

        # 5. Parse subtitle
        transcript = loop.run_until_complete(parse_subtitle_to_text(sub_path or ""))

        self.update_state(state="PROGRESS", meta={"step": "detect", "progress": 40})

        # 6. Detect highlights
        if NOVITA_API_KEY:
            moments = loop.run_until_complete(
                detect_highlights(transcript, info.get("title", ""), info.get("duration", 0))
            )
        else:
            from app.services.ai_service import _fallback_heuristic
            moments = _fallback_heuristic(transcript)

        # 7. Clip each moment
        self.update_state(state="PROGRESS", meta={"step": "clipping", "progress": 60})

        clip_paths = []
        for i, moment in enumerate(moments[:5]):
            start = moment.get("start", 10)
            end = moment.get("end", start + 45)
            reason = moment.get("reason", "")

            clip_filename = f"clip_{video_id}_{i}.mp4"
            clip_path = os.path.join(CLIPS_DIR, clip_filename)

            success = loop.run_until_complete(
                clip_video(
                    video_path=video_path,
                    output_path=clip_path,
                    start=start,
                    end=end,
                    tracking="face" if i == 0 else "none",
                    add_subtitle=bool(sub_path),
                    subtitle_path=sub_path,
                )
            )

            if success:
                clip_paths.append({
                    "path": clip_path,
                    "start": start,
                    "end": end,
                    "reason": reason,
                })

            self.update_state(
                state="PROGRESS",
                meta={"step": "clipping", "progress": 60 + (i + 1) * 7}
            )

        # 8. Save clips to DB
        async def save_clips():
            async with async_session() as session:
                from sqlalchemy import select
                result = await session.execute(select(Video).where(Video.id == video_id))
                video = result.scalar_one_or_none()
                if not video:
                    return

                video.status = "completed"
                video.file_path = video_path

                for cp in clip_paths:
                    clip_title = loop.run_until_complete(
                        generate_title(transcript[:200], info.get("title", ""))
                    )
                    clip = Clip(
                        video_id=video_id,
                        start_time=cp["start"],
                        end_time=cp["end"],
                        reason=cp["reason"],
                        method="ai" if NOVITA_API_KEY else "heuristic",
                        tracking_type="face" if cp == clip_paths[0] else "none",
                        file_path=cp["path"],
                        status="ready",
                        title=clip_title,
                    )
                    session.add(clip)

                # Kurangi credits
                from sqlalchemy import select as sel
                u_result = await session.execute(sel(User).where(User.id == user_id))
                user = u_result.scalar_one_or_none()
                if user:
                    user.credits = max(0, user.credits - 1)

                await session.commit()

        from app.models.models import User
        loop.run_until_complete(save_clips())

        self.update_state(state="PROGRESS", meta={"step": "done", "progress": 100})

        return {
            "video_id": video_id,
            "clips_created": len(clip_paths),
            "moments": moments,
        }

    except Exception as e:
        logger.error(f"Process video failed: {e}")

        async def mark_failed():
            async with async_session() as session:
                from sqlalchemy import select
                result = await session.execute(select(Video).where(Video.id == video_id))
                video = result.scalar_one_or_none()
                if video:
                    video.status = "failed"
                    video.error_message = str(e)
                    await session.commit()

        loop.run_until_complete(mark_failed())

        raise
    finally:
        loop.close()
