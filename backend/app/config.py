import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://autoclipper:autoclipper123@localhost:54321/autoclipper")
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC", "postgresql+psycopg2://autoclipper:autoclipper123@localhost:54321/autoclipper")

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Auth
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production-please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://autoclipper.sir-l.web.id/auth/callback")

# Novita AI
NOVITA_API_KEY = os.getenv("NOVITA_API_KEY", "")
NOVITA_BASE_URL = os.getenv("NOVITA_BASE_URL", "https://ai.sir-l.web.id/v1")
NOVITA_MODEL = os.getenv("NOVITA_MODEL", "anomaly/DeepSeek-V4-Flash-0709")

# App
APP_URL = os.getenv("APP_URL", "https://autoclipper.sir-l.web.id")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/var/www/autoclipper.sir-l.web.id/data")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/var/www/autoclipper.sir-l.web.id/data/downloads")
CLIPS_DIR = os.getenv("CLIPS_DIR", "/var/www/autoclipper.sir-l.web.id/data/clips")
TEMP_DIR = os.getenv("TEMP_DIR", "/var/www/autoclipper.sir-l.web.id/data/temp")

# Limits
MAX_VIDEO_DURATION = int(os.getenv("MAX_VIDEO_DURATION", "1800"))  # 30 min
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "1"))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "524288000"))  # 500MB
