import hashlib
import secrets
import os
import json
import logging
from datetime import datetime
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
from app.workers.tasks import process_video

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

# ─── Helpers ──────────────────────────────────────────────────

def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

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

# ─── Auth Models & Endpoints ────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

def hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(f"autoclipper_salt_{password}".encode()).hexdigest()

@router.post("/auth/register")
async def register_user(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if not data.email or not data.password or not data.name:
        raise HTTPException(400, "Nama, email, dan password wajib diisi")
        
    email_clean = data.email.strip().lower()
    
    res = await db.execute(select(User).where(User.email == email_clean))
    existing_user = res.scalar_one_or_none()
    if existing_user:
        raise HTTPException(400, "Email sudah terdaftar. Silakan login.")
        
    import secrets
    raw_api_key = f"ac_{secrets.token_hex(16)}"
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
    if not data.email or not data.password:
        raise HTTPException(400, "Email dan password wajib diisi")
        
    email_clean = data.email.strip().lower()
    pwd_hash = hash_password(data.password)
    
    res = await db.execute(select(User).where(User.email == email_clean))
    user = res.scalar_one_or_none()
    
    if not user or user.password_hash != pwd_hash:
        raise HTTPException(400, "Email atau password salah")
        
    import secrets
    raw_api_key = f"ac_{secrets.token_hex(16)}"
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
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "https://autoclipper.sir-l.web.id/api/auth/google/callback")
    if not client_id or not client_secret:
        raise HTTPException(500, "Google OAuth not configured")
    state = secrets.token_urlsafe(32)
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
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
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
    return {"status": "ok", "tokens": token_data}

# ─── Video Endpoints ─────────────────────────────────────────

class SubmitURL(BaseModel):
    url: str
    mode: str = "heuristic"
    tracking: str = "center"

@router.post("/videos/submit")
async def submit_video(
    data: SubmitURL,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.credits < 1 and data.mode == "ai":
        raise HTTPException(402, "Insufficient credits")
        
    # Rate limiting: Maksimal 2 antrean video aktif per user
    active_res = await db.execute(
        select(func.count(Video.id)).where(
            Video.user_id == user.id,
            Video.status.in_(["pending", "downloading", "processing"])
        )
    )
    active_count = active_res.scalar() or 0
    if active_count >= 2:
        raise HTTPException(429, "Anda memiliki terlalu banyak antrean video yang sedang diproses. Harap tunggu hingga selesai.")
        
    try:
        info = await get_video_info(data.url)
    except Exception as e:
        raise HTTPException(400, f"Failed to get video info: {e}")
    video = Video(
        user_id=user.id,
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
    # Auto-detect if Redis is available, otherwise run in a local background thread
    try:
        import redis
        r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), socket_timeout=1)
        r.ping()
        # Redis is available, queue via Celery
        process_video.delay(video.id, video.youtube_url, user.id)
        logger.info(f"Queued video {video.id} processing task in Celery/Redis.")
    except Exception:
        # Redis is down or not configured, run in local background thread
        logger.info(f"Redis is unavailable. Running video {video.id} processing in a local background thread.")
        import threading
        class MockTask:
            def update_state(self, state=None, meta=None):
                pass
        
        def run_local_task():
            try:
                process_video(MockTask(), video.id, video.youtube_url, user.id)
            except Exception as e:
                logger.error(f"Local video processing thread failed: {e}")
                
        threading.Thread(target=run_local_task, daemon=True).start()

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
        } for c in video.clips],
    }

@router.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

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
    return {"url": f"/api/clips/{clip_id}/file", "mime": "video/mp4"}

@router.put("/clips/{clip_id}/edit")
async def edit_clip(
    clip_id: int,
    data: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Clip).join(Video).where(Clip.id == clip_id, Video.user_id == user.id)
    )
    clip = result.scalar_one_or_none()
    if not clip:
        raise HTTPException(404, "Clip not found")
    if "title" in data:
        clip.title = data["title"]
    if "start" in data:
        clip.start_time = float(data["start"])
    if "end" in data:
        clip.end_time = float(data["end"])
    if "subtitle" in data:
        clip.reason = data.get("subtitle", clip.reason)
    if "is_featured" in data:
        clip.is_featured = bool(data["is_featured"])
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
    from app.services.youtube_service import upload_to_youtube
    try:
        url = await upload_to_youtube(clip.file_path, clip.title or "Auto Clip")
        clip.youtube_url = url
        clip.status = "uploaded"
        await db.commit()
        return {"status": "uploaded", "url": url}
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
    new_key = "ac_" + secrets.token_hex(16)
    user.api_key = hash_api_key(new_key)
    await db.commit()
    return {"api_key": new_key}

# ─── Cookie Endpoints ─────────────────────────────────────────

@router.post("/cookie/upload")
async def upload_cookie(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type != "application/json":
        raise HTTPException(400, "Hanya file JSON yang diperbolehkan")
    content = await file.read()
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(400, "JSON tidak valid")
    if "refresh_token" not in payload:
        raise HTTPException(400, "Missing refresh_token di file cookie")
    cookie_dir = "/var/www/autoclipper.sir-l.web.id/data/cookies"
    os.makedirs(cookie_dir, exist_ok=True)
    cookie_path = f"{cookie_dir}/{user.id}.cookie.json"
    with open(cookie_path, "wb") as f:
        f.write(content)
    user.cookie_path = cookie_path
    await db.commit()
    return {"status": "ok", "message": "Cookie berhasil disimpan"}

@router.get("/cookie/status")
async def cookie_status(user: User = Depends(get_current_user)):
    return {"has_cookie": bool(user.cookie_path), "cookie_path": user.cookie_path}

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
async def admin_set_credits(user_id: int, data: dict, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "User not found")
    u.credits = data.get("credits", u.credits)
    u.role = data.get("role", u.role)
    await db.commit()
    return {"status": "ok"}

@router.patch("/admin/users/{user_id}")
async def admin_update_role(user_id: int, data: dict, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "User not found")
    user_role = data.get("role", u.role)
    if user_role not in ["admin", "paid", "free"]:
        raise HTTPException(400, "Role must be admin, paid, or free")
    u.role = user_role
    await db.commit()
    return {"status": "ok", "id": u.id, "role": u.role}

@router.post("/admin/users/create")
async def admin_create_user(data: dict, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    email = data.get("email", "")
    name = data.get("name", "User")
    credits = data.get("credits", 3)
    role = data.get("role", "free")
    if not email:
        raise HTTPException(400, "Email required")
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")
    api_key_raw = "ac_" + secrets.token_hex(16)
    user = User(email=email, name=name, credits=credits, role=role, api_key=hash_api_key(api_key_raw))
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
        "created_at": v.created_at.isoformat(),
        "queued_for": int((datetime.utcnow() - v.created_at).total_seconds()),
    } for v in queue]

@router.get("/admin/system")
async def admin_system(admin: User = Depends(require_admin)):
    import shutil, psutil
    disk = shutil.disk_usage("/")
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1)
    return {
        "cpu_percent": cpu,
        "memory_total_gb": round(mem.total / (1024**3), 1),
        "memory_used_gb": round(mem.used / (1024**3), 1),
        "memory_percent": mem.percent,
        "disk_total_gb": round(disk.total / (1024**3), 1),
        "disk_used_gb": round(disk.used / (1024**3), 1),
        "disk_free_gb": round(disk.free / (1024**3), 1),
        "disk_percent": disk.used / disk.total * 100,
    }

# ─── Admin Cookie Upload ────────────────────────────────────

@router.post("/admin/cookie/upload")
async def admin_cookie_upload(
    user_id: int,
    file: UploadFile = File(...),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type != "application/json":
        raise HTTPException(400, "Hanya file JSON yang diperbolehkan")
    content = await file.read()
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(400, "JSON tidak valid")
    if "refresh_token" not in payload:
        raise HTTPException(400, "Missing refresh_token di file cookie")
    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "User tidak ditemukan")
    cookie_dir = "/var/www/autoclipper.sir-l.web.id/data/cookies"
    os.makedirs(cookie_dir, exist_ok=True)
    cookie_path = f"{cookie_dir}/{user_id}.cookie.json"
    with open(cookie_path, "wb") as f:
        f.write(content)
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
    process_video.delay(video.id, data.mode, data.tracking)
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
class CheckoutRequest(BaseModel):
    credits: int
    amount: float

@router.post("/payments/checkout")
async def create_checkout(data: CheckoutRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pay_enabled = await get_setting("payment_enabled", "false", db)
    if pay_enabled != "true":
        raise HTTPException(400, "Sistem pembayaran dinonaktifkan")
        
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
        credits=data.credits,
        amount=data.amount,
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
            "gross_amount": int(data.amount)
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
        
    res = await db.execute(select(Order).where(Order.id == order_id))
    order = res.scalar_one_or_none()
    if not order:
        return {"status": "ignored", "reason": "Order not found"}
        
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
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    if not client_id:
        raise HTTPException(500, "Google Client ID belum diatur")
    redirect_uri = "http://localhost:8000/api/auth/google/app/callback"
    
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        "&scope=openid email profile"
        "&access_type=offline"
        "&prompt=consent"
    )
    return RedirectResponse(url)

@router.get("/auth/google/app/callback")
async def google_app_callback(code: str, db: AsyncSession = Depends(get_db)):
    if not code:
        raise HTTPException(400, "Code missing")
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = "http://localhost:8000/api/auth/google/app/callback"
    
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
    
    api_key_raw = ""
    if not user:
        import secrets
        api_key_raw = f"ac_{secrets.token_hex(16)}"
        hashed_key = hash_api_key(api_key_raw)
        user = User(
            email=email,
            name=name,
            role="user",
            api_key=hashed_key,
            credits=5
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        import secrets
        api_key_raw = f"ac_{secrets.token_hex(16)}"
        user.api_key = hash_api_key(api_key_raw)
        await db.commit()
        
    return RedirectResponse(f"http://localhost:8081/?api_key={api_key_raw}")
