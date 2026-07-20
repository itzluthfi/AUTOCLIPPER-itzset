import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./autoclipper.db")
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC", "sqlite:///./autoclipper.db")

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Auth
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production-please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")

# LLM Router Integration (Router Endpoint)
NOVITA_API_KEY = os.getenv("NOVITA_API_KEY") or "sk-57c900f79ff8e38e-01seyn-7ecd75b9"
NOVITA_BASE_URL = os.getenv("NOVITA_BASE_URL") or "https://ai.sir-l.web.id/v1"
NOVITA_MODEL = os.getenv("NOVITA_MODEL") or "autoclipper"

# App URLs
APP_URL = os.getenv("APP_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8081")

# CORS: daftar origin tambahan dipisah koma, mis. "https://app.example.com,https://example.com"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

# Storage (default relatif agar jalan di dev; production set lewat .env)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.abspath("./data"))
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", os.path.join(UPLOAD_DIR, "downloads"))
CLIPS_DIR = os.getenv("CLIPS_DIR", os.path.join(UPLOAD_DIR, "clips"))
TEMP_DIR = os.getenv("TEMP_DIR", os.path.join(UPLOAD_DIR, "temp"))
COOKIES_DIR = os.getenv("COOKIES_DIR", os.path.join(UPLOAD_DIR, "cookies"))

# Limits
MAX_VIDEO_DURATION = int(os.getenv("MAX_VIDEO_DURATION", "1800"))  # 30 min
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "1"))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "524288000"))  # 500MB
MAX_ACTIVE_VIDEOS_PER_USER = int(os.getenv("MAX_ACTIVE_VIDEOS_PER_USER", "2"))

# Paket kredit — harga ditentukan server, client hanya mengirim package_id
CREDIT_PACKAGES = {
    "starter": {"credits": 10, "amount": 50000, "label": "Paket Pemula",
                "desc": "Cocok untuk mencoba fitur AI Auto-Clip"},
    "creator": {"credits": 30, "amount": 120000, "label": "Paket Kreator",
                "desc": "Pilihan terbaik untuk kreator konten aktif"},
    "pro": {"credits": 100, "amount": 350000, "label": "Paket Profesional",
            "desc": "Sangat hemat untuk agensi & tim editor"},
}
