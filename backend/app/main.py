import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import APP_URL, FRONTEND_URL, CORS_ORIGINS
from app.database import init_db
from app.api.routes import router as api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    await init_db()
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="AutoClipper API",
    description="YouTube Auto-Clip App",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — hanya origin yang dikenal (dev lokal + APP_URL/FRONTEND_URL + CORS_ORIGINS dari env)
_allowed_origins = {
    "http://localhost:8081",
    "http://localhost:19006",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8081",
    "http://127.0.0.1:8000",
    APP_URL,
    FRONTEND_URL,
    *CORS_ORIGINS,
}
_allowed_origins.discard("")

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(_allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router)

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
