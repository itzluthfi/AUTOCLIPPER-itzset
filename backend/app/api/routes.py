import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import RedirectResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.models import User, Video, Clip, CreditTransaction, SystemSetting, Order
from app.services.video_service import download_video, get_video_info
from app.services.ai_service import detect_highlights
from app.workers.tasks import process_video, run_process_video
from app.security import (
    hash_api_key, generate_api_key, hash_password, verify_password,
    password_needs_rehash, generate_oauth_state, verify_oauth_state,
    verify_midtrans_signature,
)
from app.schemas import (
    RegisterRequest, LoginRequest, SubmitURL, ClipEditRequest, CheckoutRequest,
    AdminSetCreditsRequest, AdminUpdateRoleRequest, AdminCreateUserRequest,
)
from app.config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI,
    APP_URL, FRONTEND_URL, COOKIES_DIR, MAX_VIDEO_DURATION,
    MAX_ACTIVE_VIDEOS_PER_USER, CREDIT_PACKAGES,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

# ─── Helpers ──────────────────────────────────────────────────

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        api_key = request.query_params.get("key") or request.query_params.get("api_key")
    if not api_key:
        raise HTTPException(401, "API key required")
    hashed = hash_api_key(api_key)
    result = await db.execute(select(User).where(User.api_key == hashed))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(401, "Invalid API key")
    return user

async def require_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Admin only")
    return user

# ─── Auth Endpoints ────────────────────────────────────────────

@router.post("/auth/register")
async def register_user(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    email_clean = data.email  # sudah dinormalisasi & divalidasi oleh schema

    res = await db.execute(select(User).where(User.email == email_clean))
    existing_user = res.scalar_one_or_none()
    if existing_user:
        raise HTTPException(400, "Email sudah terdaftar. Silakan login.")

    raw_api_key = generate_api_key()
    hashed_key = hash_api_key(raw_api_key)
    pwd_hash = hash_password(data.password)

    new_user = User(
        name=data.name.strip(),
        email=email_clean,
        role="user",
        password_hash=pwd_hash,
        api_key=hashed_key,
        credits=5
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {
        "status": "ok",
        "message": "Registrasi berhasil",
        "api_key": raw_api_key,
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role,
            "credits": new_user.credits
        }
    }

@router.post("/auth/login")
async def login_user(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.email == data.email))
    user = res.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(400, "Email atau password salah")

    # Upgrade hash lama (SHA256) ke bcrypt secara transparan saat login berhasil
    if password_needs_rehash(user.password_hash):
        user.password_hash = hash_password(data.password)

    raw_api_key = generate_api_key()
    user.api_key = hash_api_key(raw_api_key)
    await db.commit()
    
    return {
        "status": "ok",
        "message": "Login berhasil",
        "api_key": raw_api_key,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "credits": user.credits
        }
    }

# ─── Google OAuth ────────────────────────────────────────────────

@router.get("/auth/google/login")
async def google_login():
    client_id = GOOGLE_CLIENT_ID
    redirect_uri = GOOGLE_REDIRECT_URI or f"{APP_URL}/api/auth/google/callback"
    if not client_id or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(500, "Google OAuth not configured")
    state = generate_oauth_state()
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=https://www.googleapis.com/auth/youtube.upload"
        f"&access_type=offline"
        f"&state={state}"
        f"&prompt=consent"
    )
    return RedirectResponse(url=auth_url)

@router.get("/auth/google/callback")
async def google_callback(code: str, state: str = None, db: AsyncSession = Depends(get_db)):
    if not code:
        raise HTTPException(400, "Missing code")
    if not verify_oauth_state(state):
        raise HTTPException(400, "State OAuth tidak valid atau kedaluwarsa")
    client_id = GOOGLE_CLIENT_ID
    client_secret = GOOGLE_CLIENT_SECRET
    redirect_uri = GOOGLE_REDIRECT_URI or f"{APP_URL}/api/auth/google/callback"
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        })
        token_data = resp.json()
    if "error" in token_data:
        raise HTTPException(400, token_data.get("error_description", "OAuth failed"))

    # Ambil profil user dari Google, lalu buat/perbarui akun & kembalikan API key
    # ke frontend — sebelumnya endpoint ini cuma me-return token mentah sebagai JSON,
    # yang tidak bisa dipakai frontend untuk login (SSO tidak pernah benar-benar selesai).
    access_token = token_data.get("access_token")
    async with httpx.AsyncClient() as client:
        user_info_resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_info_resp.json()

    email = user_info.get("email")
    name = user_info.get("name", "Google User")
    if not email:
        raise HTTPException(400, "Gagal mendapatkan email dari Google")

    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()

    api_key_raw = generate_api_key()
    if not user:
        user = User(
            email=email,
            name=name,
            role="user",
            api_key=hash_api_key(api_key_raw),
            credits=5,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.api_key = hash_api_key(api_key_raw)
        await db.commit()

    return RedirectResponse(f"{FRONTEND_URL}/?api_key={api_key_raw}")

# ─── Video Endpoints ─────────────────────────────────────────

ACTIVE_STATUSES = ["pending", "downloading", "subtitling", "detecting",
                   "clipping", "tracking", "finalizing", "processing"]

def _dispatch_processing(video_id: int, youtube_url: str, user_id: int, mode: str, tracking: str, num_clips: int = 5, sub_lang: str = "id"):
    """Kirim task ke Celery/Redis; jika gagal, jalankan di thread background lokal."""
    try:
        import redis as redis_lib
        r = redis_lib.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), socket_timeout=1)
        r.ping()
        process_video.delay(video_id, youtube_url, user_id, mode, tracking, num_clips, sub_lang)
        logger.info(f"Queued video {video_id} in Celery/Redis.")
    except Exception:
        logger.info(f"Redis unavailable. Processing video {video_id} in local background thread.")
        import threading

        def run_local_task():
            try:
                run_process_video(video_id, youtube_url, user_id, mode, tracking, num_clips, sub_lang)
            except Exception as e:
                logger.error(f"Local video processing thread failed: {e}")

        threading.Thread(target=run_local_task, daemon=True).start()

@router.post("/videos/auto-preset")
async def auto_preset_video(
    data: SubmitURL,
    user: User = Depends(get_current_user),
):
    """Menggunakan LLM untuk membaca metadata video dan merekomendasikan mode tracking & jumlah klip"""
    from app.services.video_service import get_video_info
    from app.services.ai_service import auto_detect_video_settings

    try:
        info = await get_video_info(data.url, cookie_path=user.cookie_path)
        title = info.get("title", "")
        desc = info.get("description", "")
        preset = await auto_detect_video_settings(title, desc)
        return {
            "title": title,
            "thumbnail": info.get("thumbnail", ""),
            "duration": info.get("duration", 0),
            "preset": preset
        }
    except Exception as e:
        logger.error(f"Auto preset error: {e}")
        return {
            "title": "",
            "preset": {
                "mode": "ai",
                "tracking": "face",
                "num_clips": 5,
                "reason": "Default preset"
            }
        }

@router.post("/videos/submit")
async def submit_video(
    data: SubmitURL,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Rate limiting: batasi antrean video aktif per user
    active_res = await db.execute(
        select(func.count(Video.id)).where(
            Video.user_id == user.id,
            Video.status.in_(ACTIVE_STATUSES)
        )
    )
    active_count = active_res.scalar() or 0
    if active_count >= MAX_ACTIVE_VIDEOS_PER_USER:
        raise HTTPException(429, "Anda memiliki terlalu banyak antrean video yang sedang diproses. Harap tunggu hingga selesai.")

    try:
        info = await get_video_info(data.url, cookie_path=user.cookie_path)
    except Exception as e:
        raise HTTPException(400, f"Failed to get video info: {e}")

    duration = info.get("duration", 0) or 0
    if not info.get("id"):
        raise HTTPException(400, "URL video tidak valid atau tidak dapat diakses")
    if duration > MAX_VIDEO_DURATION:
        raise HTTPException(
            400,
            f"Durasi video {duration // 60} menit melebihi batas {MAX_VIDEO_DURATION // 60} menit."
        )

    # Role Access Control for AI Mode
    if data.mode == "ai":
        if user.role == "free":
            raise HTTPException(
                403,
                "Fitur AI Router hanya tersedia untuk pengguna Paket Paid / Premium. Silakan upgrade paket Anda ke Paid atau gunakan Mode Heuristik."
            )
        # Admin bebas mengolah video AI tanpa pemotongan kredit
        if user.role != "admin":
            result = await db.execute(
                update(User)
                .where(User.id == user.id, User.credits >= 1)
                .values(credits=User.credits - 1)
            )
            if result.rowcount == 0:
                raise HTTPException(402, "Kredit tidak cukup. Silakan isi ulang kredit Anda.")
            db.add(CreditTransaction(
                user_id=user.id, amount=-1, type="usage",
                description=f"Proses AI: {info.get('title', data.url)[:100]}",
            ))

    num_clips = getattr(data, "num_clips", 5) or 5

    video = Video(
        user_id=user.id,
        youtube_url=data.url,
        youtube_id=info.get("id", ""),
        title=info.get("title", ""),
        description=info.get("description", ""),
        duration_seconds=duration,
        video_type=info.get("type", "general"),
        status="pending",
        progress=0,
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)

    sub_lang = getattr(data, "sub_lang", "id") or "id"
    _dispatch_processing(video.id, video.youtube_url, user.id, data.mode, data.tracking, num_clips, sub_lang)

    return {"status": "queued", "video_id": video.id}

@router.get("/videos")
async def list_videos(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Video).where(Video.user_id == user.id).order_by(Video.created_at.desc())
    )
    videos = result.scalars().all()
    return [{
        "id": v.id,
        "title": v.title,
        "youtube_id": v.youtube_id,
        "duration": v.duration_seconds,
        "status": v.status,
        "clips_count": len(v.clips),
        "created_at": v.created_at.isoformat(),
    } for v in videos]

@router.get("/videos/{video_id}")
async def get_video(video_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Video).where(Video.id == video_id, Video.user_id == user.id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(404, "Video not found")

    return {
        "id": video.id,
        "title": video.title,
        "youtube_id": video.youtube_id,
        "duration_seconds": video.duration_seconds,
        "status": video.status,
        "progress": video.progress or 0,
        "current_step_log": getattr(video, "current_step_log", None),
        "error_message": video.error_message,
        "clips": [{
            "id": c.id,
            "start": c.start_time,
            "end": c.end_time,
            "title": c.title,
            "reason": c.reason,
            "method": c.method,
            "tracking": c.tracking_type,
            "status": c.status,
            "is_featured": c.is_featured,
            "youtube_url": c.youtube_url,
        } for c in video.clips],
    }

async def delete_video_files_and_db(video_id: int, db: AsyncSession, user_id: Optional[int] = None) -> bool:
    """Hapus video, klip terkait, dan file fisiknya dari storage disk."""
    query = select(Video).where(Video.id == video_id)
    if user_id is not None:
        query = query.where(Video.user_id == user_id)
    result = await db.execute(query)
    video = result.scalar_one_or_none()
    if not video:
        return False

    # 1. Hapus file-file klip & thumbnail
    for clip in (video.clips or []):
        if clip.file_path and os.path.exists(clip.file_path):
            try:
                os.remove(clip.file_path)
                logger.info(f"Deleted clip file: {clip.file_path}")
            except Exception as e:
                logger.error(f"Error deleting clip file {clip.file_path}: {e}")

        if clip.thumbnail_path and os.path.exists(clip.thumbnail_path):
            try:
                os.remove(clip.thumbnail_path)
                logger.info(f"Deleted clip thumbnail: {clip.thumbnail_path}")
            except Exception as e:
                logger.error(f"Error deleting thumbnail {clip.thumbnail_path}: {e}")

        await db.delete(clip)

    # 2. Hapus file video utama jika ada
    if video.file_path and os.path.exists(video.file_path):
        try:
            os.remove(video.file_path)
            logger.info(f"Deleted main video file: {video.file_path}")
        except Exception as e:
            logger.error(f"Error deleting video file {video.file_path}: {e}")

    # 3. Cari dan bersihkan file tambahan di DOWNLOAD_DIR, TEMP_DIR, CLIPS_DIR jika ada
    try:
        from app.config import DOWNLOAD_DIR, TEMP_DIR, CLIPS_DIR
        for d in [DOWNLOAD_DIR, TEMP_DIR, CLIPS_DIR]:
            if os.path.exists(d):
                for fname in os.listdir(d):
                    if f"_{video_id}_" in fname or fname.startswith(f"video_{video_id}") or fname.startswith(f"clip_{video_id}_") or fname.startswith(f"thumb_{video_id}_"):
                        fpath = os.path.join(d, fname)
                        if os.path.isfile(fpath):
                            try:
                                os.remove(fpath)
                            except Exception:
                                pass
    except Exception as e:
        logger.error(f"Error cleaning folder pattern for video {video_id}: {e}")

    # 4. Hapus record video dari DB
    await db.delete(video)
    await db.commit()
    return True

@router.delete("/videos/{video_id}")
async def delete_video(video_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Hapus video + file fisik dari storage disk (milik user sendiri atau admin)."""
    user_filter = None if user.role == "admin" else user.id
    success = await delete_video_files_and_db(video_id, db, user_id=user_filter)
    if not success:
        raise HTTPException(404, "Video tidak ditemukan atau Anda tidak memiliki akses")
    return {"status": "ok", "message": "Video dan file fisik berhasil dihapus dari storage"}

@router.delete("/admin/videos/{video_id}")
async def admin_delete_video(video_id: int, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    """Admin endpoint hapus video + file fisik dari storage disk."""
    success = await delete_video_files_and_db(video_id, db, user_id=None)
    if not success:
        raise HTTPException(404, "Video tidak ditemukan")
    return {"status": "ok", "message": "Video dan file fisik berhasil dihapus oleh admin"}

async def cleanup_expired_videos_task():
    """Latar belakang otomatis menghapus video & file fisik yang berusia > 24 jam."""
    while True:
        try:
            from app.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                cutoff = datetime.utcnow() - timedelta(hours=24)
                result = await db.execute(select(Video).where(Video.created_at < cutoff))
                expired_videos = result.scalars().all()
                if expired_videos:
                    logger.info(f"[Auto-Cleanup 24h] Menemukan {len(expired_videos)} video berusia > 24 jam. Memulai pembersihan disk storage...")
                    for v in expired_videos:
                        try:
                            await delete_video_files_and_db(v.id, db)
                            logger.info(f"[Auto-Cleanup 24h] Video #{v.id} '{v.title}' & file fisik berhasil dibersihkan dari disk.")
                        except Exception as e:
                            logger.error(f"[Auto-Cleanup 24h] Gagal menghapus video #{v.id}: {e}")
        except Exception as e:
            logger.error(f"[Auto-Cleanup Task Error]: {e}")

        # Jalankan setiap 1 jam sekali (3600 detik)
        await asyncio.sleep(3600)

@router.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

@router.get("/stats/public")
async def get_public_stats(db: AsyncSession = Depends(get_db)):
    """Angka agregat asli (bukan fiktif) untuk ditampilkan di landing page."""
    total_clips = (await db.execute(select(func.count(Clip.id)))).scalar() or 0
    total_videos = (
        await db.execute(select(func.count(Video.id)).where(Video.status == "completed"))
    ).scalar() or 0
    total_creators = (
        await db.execute(select(func.count(func.distinct(Video.user_id))))
    ).scalar() or 0
    return {
        "clips_created": total_clips,
        "videos_processed": total_videos,
        "creators": total_creators,
    }

@router.get("/clips/public/featured")
async def get_featured_clips(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Clip).where(Clip.is_featured == True, Clip.status == "ready")
    )
    clips = result.scalars().all()
    return [{
        "id": c.id,
        "title": c.title,
        "start": c.start_time,
        "end": c.end_time,
        "url": f"/api/clips/{c.id}/file/public",
    } for c in clips]

@router.get("/clips/{clip_id}/file/public")
async def get_public_clip_file(clip_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Clip).where(Clip.id == clip_id, Clip.is_featured == True)
    )
    clip = result.scalar_one_or_none()
    if not clip:
        raise HTTPException(404, "Clip not found or not public")
    if not clip.file_path or not os.path.exists(clip.file_path):
        raise HTTPException(404, "Clip file not ready")
    return FileResponse(clip.file_path, media_type="video/mp4")

# ─── Clip Endpoints ────────────────────────────────────────────

@router.get("/clips/{clip_id}")
async def get_clip(clip_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Clip).join(Video).where(Clip.id == clip_id, Video.user_id == user.id)
    )
    clip = result.scalar_one_or_none()
    if not clip:
        raise HTTPException(404, "Clip not found")
    return {
        "id": clip.id,
        "video_id": clip.video_id,
        "start": clip.start_time,
        "end": clip.end_time,
        "title": clip.title,
        "subtitle": clip.reason,
        "status": clip.status,
    }

@router.get("/clips/{clip_id}/file")
async def get_clip_file(
    clip_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Clip).join(Video).where(Clip.id == clip_id, Video.user_id == user.id)
    )
    clip = result.scalar_one_or_none()
    if not clip:
        raise HTTPException(404, "Clip not found")
    if not clip.file_path or not os.path.exists(clip.file_path):
        raise HTTPException(404, "Clip file not ready")
    return FileResponse(clip.file_path, media_type="video/mp4")

@router.get("/clips/{clip_id}/thumbnail")
async def get_clip_thumbnail(
    clip_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Clip).join(Video).where(Clip.id == clip_id, Video.user_id == user.id)
    )
    clip = result.scalar_one_or_none()
    if not clip:
        raise HTTPException(404, "Clip not found")
    if not clip.thumbnail_path or not os.path.exists(clip.thumbnail_path):
        raise HTTPException(404, "Thumbnail not ready")
    return FileResponse(clip.thumbnail_path, media_type="image/jpeg")

@router.get("/clips/{clip_id}/download")
async def download_clip(clip_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Clip).join(Video).where(Clip.id == clip_id, Video.user_id == user.id)
    )
    clip = result.scalar_one_or_none()
    if not clip:
        raise HTTPException(404, "Clip not found")
    if not clip.file_path or not os.path.exists(clip.file_path):
        raise HTTPException(404, "Clip file not ready")

    filename = f"clip_{clip_id}.mp4"
    return FileResponse(
        clip.file_path,
        media_type="video/mp4",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.put("/clips/{clip_id}/edit")
async def edit_clip(
    clip_id: int,
    data: ClipEditRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.role == "admin":
        # Admin boleh mengedit klip siapa pun (dipakai panel admin untuk featured)
        result = await db.execute(select(Clip).where(Clip.id == clip_id))
    else:
        result = await db.execute(
            select(Clip).join(Video).where(Clip.id == clip_id, Video.user_id == user.id)
        )
    clip = result.scalar_one_or_none()
    if not clip:
        raise HTTPException(404, "Clip not found")
    if data.title is not None:
        clip.title = data.title
    new_start = data.start if data.start is not None else clip.start_time
    new_end = data.end if data.end is not None else clip.end_time
    if new_end <= new_start:
        raise HTTPException(400, "Waktu selesai harus lebih besar dari waktu mulai")
    clip.start_time = new_start
    clip.end_time = new_end
    if data.subtitle is not None:
        clip.reason = data.subtitle
    # Hanya admin yang boleh menandai klip sebagai featured (tampil publik)
    if data.is_featured is not None:
        if user.role != "admin":
            raise HTTPException(403, "Hanya admin yang dapat mengubah status featured")
        clip.is_featured = data.is_featured
    await db.commit()
    return {"status": "ok"}

@router.post("/clips/{clip_id}/upload")
async def upload_clip(
    clip_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Clip).join(Video).where(Clip.id == clip_id, Video.user_id == user.id)
    )
    clip = result.scalar_one_or_none()
    if not clip:
        raise HTTPException(404, "Clip not found")
    if not clip.file_path or not os.path.exists(clip.file_path):
        raise HTTPException(404, "File klip belum siap")

    # Ambil token YouTube milik user (dari tokens_json / kolom token / file cookie)
    access_token, refresh_token = user.access_token, user.refresh_token
    tokens = {}
    if user.tokens_json:
        try:
            tokens = json.loads(user.tokens_json)
        except json.JSONDecodeError:
            tokens = {}
    elif user.cookie_path and os.path.exists(user.cookie_path):
        try:
            with open(user.cookie_path, "r", encoding="utf-8") as f:
                tokens = json.load(f)
        except (json.JSONDecodeError, OSError):
            tokens = {}
    access_token = tokens.get("access_token") or access_token or ""
    refresh_token = tokens.get("refresh_token") or refresh_token
    if not refresh_token:
        raise HTTPException(400, "Akun YouTube belum terhubung. Upload cookie/token Anda terlebih dahulu.")

    from app.services.youtube_service import upload_to_youtube
    import asyncio
    try:
        result = await asyncio.to_thread(
            upload_to_youtube, access_token, refresh_token,
            clip.file_path, clip.title or "Auto Clip",
        )
        clip.youtube_url = result["url"]
        clip.status = "uploaded"
        await db.commit()
        return {"status": "uploaded", "url": result["url"]}
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {e}")

# ─── Credits ────────────────────────────────────────────────────

@router.get("/credits")
async def get_credits(user: User = Depends(get_current_user)):
    return {"credits": user.credits}

@router.get("/credits/history")
async def get_credit_history(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CreditTransaction).where(CreditTransaction.user_id == user.id).order_by(CreditTransaction.created_at.desc()).limit(50)
    )
    return [{"amount": t.amount, "type": t.type, "description": t.description} for t in result.scalars().all()]

# ─── User Profile ──────────────────────────────────────────────

@router.get("/user/me")
async def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "credits": user.credits,
        "google_id": user.google_id,
        "has_cookie": bool(user.cookie_path),
        "avatar_url": user.avatar_url,
    }

@router.post("/user/api-key/rotate")
async def rotate_api_key(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_key = generate_api_key()
    user.api_key = hash_api_key(new_key)
    await db.commit()
    return {"api_key": new_key}

# ─── Cookie Endpoints ─────────────────────────────────────────

class CookiePasteRequest(BaseModel):
    cookie_text: str

def validate_and_save_cookie_text(text_content: str, filename_hint: str, target_user_id: int) -> str:
    text_clean = text_content.strip()
    if not text_clean:
        raise HTTPException(400, "Teks/file cookie tidak boleh kosong")
        
    is_json = False
    is_netscape = False
    
    # 1. Check JSON format (Object or Array)
    if text_clean.startswith("{") or text_clean.startswith("["):
        try:
            parsed = json.loads(text_clean)
            is_json = True
            # If JSON is an array of cookies (e.g. from EditThisCookie), convert to Netscape
            if isinstance(parsed, list):
                netscape_lines = ["# Netscape HTTP Cookie File", "# Converted from JSON Cookie Array"]
                for item in parsed:
                    if isinstance(item, dict) and "name" in item and "value" in item:
                        domain = item.get("domain", ".youtube.com")
                        path = item.get("path", "/")
                        secure = "TRUE" if item.get("secure", True) else "FALSE"
                        expires = str(int(item.get("expirationDate", 2147483647)))
                        name = item["name"]
                        val = item["value"]
                        netscape_lines.append(f"{domain}\tTRUE\t{path}\t{secure}\t{expires}\t{name}\t{val}")
                text_clean = "\n".join(netscape_lines)
                is_json = False
                is_netscape = True
        except Exception:
            pass
            
    # 2. Check Header String format ("key1=val1; key2=val2")
    if not is_json and not is_netscape:
        if "=" in text_clean and (";" in text_clean or "LOGIN_INFO=" in text_clean or "SID=" in text_clean):
            pairs = [p.strip() for p in text_clean.replace("\n", "").split(";") if "=" in p]
            if pairs:
                netscape_lines = ["# Netscape HTTP Cookie File", "# Converted from Header String"]
                for p in pairs:
                    kv = p.split("=", 1)
                    if len(kv) == 2:
                        k, v = kv[0].strip(), kv[1].strip()
                        if k and v:
                            netscape_lines.append(f".youtube.com\tTRUE\t/\tTRUE\t2147483647\t{k}\t{v}")
                if len(netscape_lines) > 2:
                    text_clean = "\n".join(netscape_lines)
                    is_netscape = True

    # 3. Check standard Netscape format
    if not is_json and not is_netscape:
        if "# Netscape" in text_clean or "youtube.com" in text_clean or "LOGIN_INFO" in text_clean or "SID" in text_clean or "\t" in text_clean or ".google.com" in text_clean:
            is_netscape = True
        elif filename_hint.endswith(".txt") or filename_hint.endswith(".cookie") or filename_hint.endswith(".cookies"):
            is_netscape = True

    if not is_json and not is_netscape:
        raise HTTPException(400, "Format cookie tidak dikenali. Gunakan Netscape (.txt), JSON, atau Header String")

    os.makedirs(COOKIES_DIR, exist_ok=True)
    ext = ".json" if is_json else ".txt"
    cookie_path = os.path.join(COOKIES_DIR, f"{target_user_id}.cookie{ext}")
    
    with open(cookie_path, "w", encoding="utf-8") as f:
        f.write(text_clean)
        
    return cookie_path

@router.post("/cookie/upload")
async def upload_cookie(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    cookie_path = validate_and_save_cookie_text(text, file.filename or "cookies.txt", user.id)
    user.cookie_path = cookie_path
    await db.commit()
    return {"status": "ok", "message": "Cookie berhasil disimpan"}

@router.post("/cookie/paste")
async def paste_cookie(
    data: CookiePasteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cookie_path = validate_and_save_cookie_text(data.cookie_text, "cookies.txt", user.id)
    user.cookie_path = cookie_path
    await db.commit()
    return {"status": "ok", "message": "Cookie berhasil disimpan"}

@router.get("/cookie/status")
async def cookie_status(user: User = Depends(get_current_user)):
    return {"has_cookie": bool(user.cookie_path), "cookie_path": user.cookie_path}

@router.post("/cookie/test")
async def test_cookie(user: User = Depends(get_current_user)):
    if not user.cookie_path or not os.path.exists(user.cookie_path):
        raise HTTPException(400, "Cookie belum di-upload. Harap atur cookie terlebih dahulu.")
    from app.services.video_service import test_youtube_cookie
    result = await test_youtube_cookie(user.cookie_path)
    return result

# ─── Admin Endpoints ─────────────────────────────────────────

@router.get("/admin/users")
async def admin_list_users(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [{
        "id": u.id,
        "email": u.email,
        "name": u.name,
        "role": u.role,
        "credits": u.credits,
        "has_cookie": bool(u.cookie_path),
        "google_id": u.google_id,
        "created_at": u.created_at.isoformat(),
    } for u in users]

@router.get("/admin/stats")
async def admin_stats(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    total_users = (await db.execute(select(func.count(User.id)))).scalar()
    total_videos = (await db.execute(select(func.count(Video.id)))).scalar()
    total_clips = (await db.execute(select(func.count(Clip.id)))).scalar()
    return {"total_users": total_users, "total_videos": total_videos, "total_clips": total_clips}

@router.put("/admin/users/{user_id}/credits")
async def admin_set_credits(user_id: int, data: AdminSetCreditsRequest, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "User not found")
    if data.credits is not None:
        u.credits = data.credits
    if data.role is not None:
        u.role = data.role
    await db.commit()
    return {"status": "ok"}

@router.patch("/admin/users/{user_id}")
async def admin_update_role(user_id: int, data: AdminUpdateRoleRequest, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "User not found")
    u.role = data.role
    await db.commit()
    return {"status": "ok", "id": u.id, "role": u.role}

@router.post("/admin/users/create")
async def admin_create_user(data: AdminCreateUserRequest, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")
    api_key_raw = generate_api_key()
    user = User(email=data.email, name=data.name, credits=data.credits, role=data.role, api_key=hash_api_key(api_key_raw))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role, "credits": user.credits, "api_key": api_key_raw}

@router.get("/admin/videos")
async def admin_list_videos(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Video).order_by(Video.created_at.desc()).limit(100)
    )
    videos = result.scalars().all()
    return [{
        "id": v.id, "title": v.title, "youtube_id": v.youtube_id, "user_id": v.user_id,
        "user_name": v.user.name if v.user else "N/A", "duration": v.duration_seconds,
        "status": v.status, "clips_count": len(v.clips), "error": v.error_message,
        "created_at": v.created_at.isoformat(),
    } for v in videos]

@router.get("/admin/videos/{video_id}")
async def admin_get_video(video_id: int, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    """Detail video + klip untuk video milik siapa pun — dipakai panel admin
    (endpoint /videos/{id} biasa dibatasi ke pemilik video saja)."""
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(404, "Video not found")
    return {
        "id": video.id,
        "title": video.title,
        "youtube_id": video.youtube_id,
        "user_id": video.user_id,
        "user_name": video.user.name if video.user else "N/A",
        "status": video.status,
        "clips": [{
            "id": c.id,
            "start": c.start_time,
            "end": c.end_time,
            "title": c.title,
            "reason": c.reason,
            "method": c.method,
            "tracking": c.tracking_type,
            "status": c.status,
            "is_featured": c.is_featured,
            "youtube_url": c.youtube_url,
        } for c in video.clips],
    }

@router.get("/admin/queue")
async def admin_queue(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Video)
        .where(Video.status.in_(["pending", "downloading", "subtitling", "detecting", "clipping", "tracking", "finalizing"]))
        .order_by(Video.created_at.asc())
    )
    queue = result.scalars().all()
    return [{
        "id": v.id, "title": v.title, "youtube_id": v.youtube_id, "user_id": v.user_id,
        "user_name": v.user.name if v.user else "N/A", "status": v.status, "duration": v.duration_seconds,
        "progress": v.progress or 0,
        "current_step_log": getattr(v, "current_step_log", None),
        "created_at": v.created_at.isoformat(),
        "queued_for": int((datetime.utcnow() - v.created_at).total_seconds()),
    } for v in queue]

@router.get("/admin/system")
async def admin_system(admin: User = Depends(require_admin)):
    import shutil
    disk = shutil.disk_usage(os.path.abspath(os.sep))
    stats = {
        "disk_total_gb": round(disk.total / (1024**3), 1),
        "disk_used_gb": round(disk.used / (1024**3), 1),
        "disk_free_gb": round(disk.free / (1024**3), 1),
        "disk_percent": disk.used / disk.total * 100,
        "cpu_percent": None,
        "memory_total_gb": None,
        "memory_used_gb": None,
        "memory_percent": None,
    }
    try:
        import psutil
        mem = psutil.virtual_memory()
        stats.update({
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "memory_total_gb": round(mem.total / (1024**3), 1),
            "memory_used_gb": round(mem.used / (1024**3), 1),
            "memory_percent": mem.percent,
        })
    except ImportError:
        pass  # psutil opsional — CPU/RAM tidak tersedia
    return stats

# ─── Admin Cookie Upload ────────────────────────────────────

@router.post("/admin/cookie/upload")
async def admin_cookie_upload(
    user_id: int,
    file: UploadFile = File(...),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "User tidak ditemukan")
        
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    cookie_path = validate_and_save_cookie_text(text, file.filename or "cookies.txt", user_id)
    u.cookie_path = cookie_path
    await db.commit()
    return {"status": "ok", "message": f"Cookie untuk user {u.name} berhasil disimpan"}

# ─── Admin Self-Clip (admin nyoba fitur) ─────────────────────

@router.post("/admin/clip/test")
async def admin_test_clip(
    data: SubmitURL,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin bisa langsung submit clip tanpa perlu cookie/credits (testing)"""
    try:
        info = await get_video_info(data.url)
    except Exception as e:
        raise HTTPException(400, f"Gagal ambil info video: {e}")
    video = Video(
        user_id=admin.id,
        youtube_url=data.url,
        youtube_id=info.get("id", ""),
        title=info.get("title", ""),
        description=info.get("description", ""),
        duration_seconds=info.get("duration", 0),
        video_type=info.get("type", "general"),
        status="pending",
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)
    _dispatch_processing(video.id, video.youtube_url, admin.id, data.mode, data.tracking)
    return {"status": "queued", "video_id": video.id, "note": "Admin test clip — cookie/credits bypassed"}

async def get_setting(key: str, default: str, db: AsyncSession) -> str:
    res = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
    setting = res.scalar_one_or_none()
    return setting.value if setting else default

# ─── Public Settings Endpoint ──────────────────────────────────
@router.get("/settings/public")
async def get_public_settings(db: AsyncSession = Depends(get_db)):
    pay_enabled = await get_setting("payment_enabled", "false", db)
    client_key = await get_setting("midtrans_client_key", "", db)
    return {
        "payment_enabled": pay_enabled == "true",
        "midtrans_client_key": client_key,
        "packages": [
            {"id": pid, **pkg} for pid, pkg in CREDIT_PACKAGES.items()
        ],
    }

# ─── Admin Settings Endpoints ──────────────────────────────────
@router.get("/admin/settings")
async def get_admin_settings(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(SystemSetting))
    settings = res.scalars().all()
    return {s.key: s.value for s in settings}

@router.put("/admin/settings")
async def update_admin_settings(data: dict, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    for k, v in data.items():
        res = await db.execute(select(SystemSetting).where(SystemSetting.key == k))
        setting = res.scalar_one_or_none()
        if setting:
            setting.value = str(v)
        else:
            db.add(SystemSetting(key=k, value=str(v)))
    await db.commit()
    return {"status": "ok"}

# ─── Payments / Checkout Endpoint ──────────────────────────────

@router.post("/payments/checkout")
async def create_checkout(data: CheckoutRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pay_enabled = await get_setting("payment_enabled", "false", db)
    if pay_enabled != "true":
        raise HTTPException(400, "Sistem pembayaran dinonaktifkan")

    # Harga & jumlah kredit HANYA dari definisi server — client cuma memilih paket
    package = CREDIT_PACKAGES.get(data.package_id)
    if not package:
        raise HTTPException(400, "Paket tidak dikenal")

    server_key = await get_setting("midtrans_server_key", "", db)
    is_prod = await get_setting("midtrans_is_production", "false", db)

    if not server_key:
        raise HTTPException(500, "Midtrans Server Key belum diatur oleh admin")

    import uuid
    import base64
    order_id = f"order-{uuid.uuid4()}"

    order = Order(
        id=order_id,
        user_id=user.id,
        credits=package["credits"],
        amount=package["amount"],
        status="pending"
    )
    db.add(order)
    await db.commit()

    snap_url = "https://app.sandbox.midtrans.com/snap/v1/transactions"
    if is_prod == "true":
        snap_url = "https://app.midtrans.com/snap/v1/transactions"

    auth_str = base64.b64encode(f"{server_key}:".encode()).decode()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_str}"
    }

    payload = {
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": int(package["amount"])
        },
        "credit_card": {
            "secure": True
        },
        "customer_details": {
            "first_name": user.name,
            "email": user.email
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(snap_url, json=payload, headers=headers, timeout=10.0)
            if resp.status_code != 201:
                raise Exception(resp.text)
            result = resp.json()
            return {
                "order_id": order_id,
                "token": result.get("token"),
                "redirect_url": result.get("redirect_url")
            }
        except Exception as e:
            order.status = "failed"
            await db.commit()
            raise HTTPException(500, f"Gagal membuat transaksi ke Midtrans: {e}")

# ─── Midtrans Notification Webhook ─────────────────────────────
@router.post("/payments/midtrans/webhook")
async def midtrans_webhook(data: dict, db: AsyncSession = Depends(get_db)):
    order_id = data.get("order_id")
    transaction_status = data.get("transaction_status")
    fraud_status = data.get("fraud_status")

    if not order_id:
        return {"status": "ignored", "reason": "No order_id"}

    # Verifikasi signature: sha512(order_id + status_code + gross_amount + server_key).
    # Tanpa ini siapa pun bisa memalsukan notifikasi settlement dan dapat kredit gratis.
    server_key = await get_setting("midtrans_server_key", "", db)
    if not verify_midtrans_signature(
        order_id=str(order_id),
        status_code=str(data.get("status_code", "")),
        gross_amount=str(data.get("gross_amount", "")),
        server_key=server_key,
        signature_key=str(data.get("signature_key", "")),
    ):
        logger.warning(f"Webhook Midtrans dengan signature tidak valid untuk order {order_id}")
        raise HTTPException(403, "Invalid signature")

    res = await db.execute(select(Order).where(Order.id == order_id))
    order = res.scalar_one_or_none()
    if not order:
        return {"status": "ignored", "reason": "Order not found"}

    # Pastikan nominal yang dibayar sesuai dengan order
    try:
        paid_amount = float(data.get("gross_amount", 0))
    except (TypeError, ValueError):
        paid_amount = 0
    if int(paid_amount) != int(order.amount):
        logger.warning(f"Webhook Midtrans: nominal {paid_amount} != order {order.amount} ({order_id})")
        return {"status": "ignored", "reason": "Amount mismatch"}

    if order.status == "pending":
        is_success = False
        if transaction_status in ["capture", "settlement"]:
            if transaction_status == "capture" and fraud_status == "challenge":
                pass
            else:
                is_success = True
                
        if is_success:
            order.status = "settlement"
            u_res = await db.execute(select(User).where(User.id == order.user_id))
            user = u_res.scalar_one_or_none()
            if user:
                user.credits += order.credits
                tx = CreditTransaction(
                    user_id=user.id,
                    amount=order.credits,
                    type="purchase",
                    description=f"Pembelian {order.credits} kredit via Midtrans ({order_id})"
                )
                db.add(tx)
        elif transaction_status in ["deny", "expire", "cancel"]:
            order.status = transaction_status
            
        await db.commit()
        return {"status": "ok", "new_status": order.status}
        
    return {"status": "ignored", "reason": f"Order already in status: {order.status}"}

# ─── App Google Login SSO ───────────────────────────────────────
@router.get("/auth/google/app/login")
async def google_app_login():
    client_id = GOOGLE_CLIENT_ID
    if not client_id:
        raise HTTPException(500, "Google Client ID belum diatur")
    # Pakai redirect_uri yang sama dengan flow /auth/google/callback (bukan /app/callback
    # terpisah) — sebelumnya dua redirect_uri berbeda dipakai padahal biasanya hanya satu
    # yang terdaftar di Google Cloud Console, menyebabkan error "redirect_uri_mismatch".
    redirect_uri = GOOGLE_REDIRECT_URI or f"{APP_URL}/api/auth/google/callback"
    state = generate_oauth_state()

    url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        "&scope=openid email profile"
        "&access_type=offline"
        f"&state={state}"
        "&prompt=consent"
    )
    return RedirectResponse(url)

@router.get("/auth/google/app/callback")
async def google_app_callback(code: str, state: str = None, db: AsyncSession = Depends(get_db)):
    if not code:
        raise HTTPException(400, "Code missing")
    if not verify_oauth_state(state):
        raise HTTPException(400, "State OAuth tidak valid atau kedaluwarsa")
    client_id = GOOGLE_CLIENT_ID
    client_secret = GOOGLE_CLIENT_SECRET
    # Pakai redirect_uri yang sama dengan flow /auth/google/callback (bukan /app/callback
    # terpisah) — sebelumnya dua redirect_uri berbeda dipakai padahal biasanya hanya satu
    # yang terdaftar di Google Cloud Console, menyebabkan error "redirect_uri_mismatch".
    redirect_uri = GOOGLE_REDIRECT_URI or f"{APP_URL}/api/auth/google/callback"
    
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        })
        token_data = resp.json()
        if "error" in token_data:
            raise HTTPException(400, token_data.get("error_description", "Token exchange failed"))
            
        access_token = token_data.get("access_token")
        
        user_info_resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_info_resp.json()
        
    email = user_info.get("email")
    name = user_info.get("name", "Google User")
    if not email:
        raise HTTPException(400, "Gagal mendapatkan email dari Google")
        
    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()
    
    api_key_raw = generate_api_key()
    if not user:
        user = User(
            email=email,
            name=name,
            role="user",
            api_key=hash_api_key(api_key_raw),
            credits=5
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.api_key = hash_api_key(api_key_raw)
        await db.commit()

    return RedirectResponse(f"{FRONTEND_URL}/?api_key={api_key_raw}")
