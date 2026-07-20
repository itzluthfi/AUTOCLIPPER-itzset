import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import DATABASE_URL

logger = logging.getLogger(__name__)

connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_async_engine(DATABASE_URL, connect_args=connect_args, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        yield session

async def init_db():
    global engine, async_session
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.warning(f"Failed to connect to primary DB ({DATABASE_URL}): {e}. Falling back to local SQLite.")
        sqlite_url = "sqlite+aiosqlite:///./autoclipper.db"
        engine = create_async_engine(sqlite_url, connect_args={"check_same_thread": False}, echo=False)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # Mini-migration
    from sqlalchemy import text
    for ddl in [
        "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)",
        "ALTER TABLE videos ADD COLUMN progress INTEGER DEFAULT 0",
        "ALTER TABLE videos ADD COLUMN current_step_log VARCHAR(500)",
    ]:
        try:
            async with engine.begin() as conn:
                await conn.execute(text(ddl))
        except Exception:
            pass
