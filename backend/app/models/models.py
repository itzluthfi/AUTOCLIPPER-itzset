import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    google_id: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(sa.String(255), unique=True)
    name: Mapped[str] = mapped_column(sa.String(255))
    avatar_url: Mapped[str] = mapped_column(sa.Text, nullable=True)
    access_token: Mapped[str] = mapped_column(sa.Text, nullable=True)
    refresh_token: Mapped[str] = mapped_column(sa.Text, nullable=True)
    credits: Mapped[int] = mapped_column(sa.Integer, default=3)
    role: Mapped[str] = mapped_column(sa.String(50), default="free")
    api_key: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    cookie_path: Mapped[str] = mapped_column(sa.Text, nullable=True)
    tokens_json: Mapped[str] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow)

    videos = relationship("Video", back_populates="user")

class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"))
    youtube_url: Mapped[str] = mapped_column(sa.Text)
    youtube_id: Mapped[str] = mapped_column(sa.String(50))
    title: Mapped[str] = mapped_column(sa.String(500), nullable=True)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(sa.Integer, default=0)
    video_type: Mapped[str] = mapped_column(sa.String(50), default="general")
    status: Mapped[str] = mapped_column(sa.String(50), default="pending")
    file_path: Mapped[str] = mapped_column(sa.Text, nullable=True)
    error_message: Mapped[str] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="videos")
    clips = relationship("Clip", back_populates="video")

class Clip(Base):
    __tablename__ = "clips"

    id: Mapped[int] = mapped_column(primary_key=True)
    video_id: Mapped[int] = mapped_column(sa.ForeignKey("videos.id"))
    start_time: Mapped[float] = mapped_column(sa.Float)
    end_time: Mapped[float] = mapped_column(sa.Float)
    reason: Mapped[str] = mapped_column(sa.Text, nullable=True)
    method: Mapped[str] = mapped_column(sa.String(50), default="heuristic")
    tracking_type: Mapped[str] = mapped_column(sa.String(50), default="none")
    file_path: Mapped[str] = mapped_column(sa.Text, nullable=True)
    thumbnail_path: Mapped[str] = mapped_column(sa.Text, nullable=True)
    status: Mapped[str] = mapped_column(sa.String(50), default="pending")
    youtube_url: Mapped[str] = mapped_column(sa.Text, nullable=True)
    title: Mapped[str] = mapped_column(sa.String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow)

    video = relationship("Video", back_populates="clips")

class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column(sa.Integer)
    type: Mapped[str] = mapped_column(sa.String(50))  # bonus, usage, purchase
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow)
