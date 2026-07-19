import hashlib
import secrets
import os
import json
import logging
from datetime import datetime
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.models import User, Video, Clip, CreditTransaction
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
    process_video.delay(video.id, data.mode, data.tracking)
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
        } for c in video.clips],
    }

@router.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

# ─── Clip Endpoints ────────────────────────────────────────────

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
