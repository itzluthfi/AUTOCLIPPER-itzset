import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to sys.path so we can import app
sys.path.append(str(Path(__file__).parent))

from app.database import engine, Base, async_session
from app.models.models import User
from app.api.routes import hash_api_key

async def seed():
    # Make sure local directories exist
    for path in ["./data", "./data/downloads", "./data/clips", "./data/temp"]:
        Path(path).mkdir(parents=True, exist_ok=True)
        print(f"Directory ready: {path}")

    print("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print("Checking for default user...")
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == "admin@autoclipper.local"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("Creating default admin user...")
            raw_key = "autoclipper_local_dev_key_123"
            hashed_key = hash_api_key(raw_key)
            
            user = User(
                email="admin@autoclipper.local",
                name="Local Developer",
                role="admin",
                api_key=hashed_key,
                credits=999
            )
            session.add(user)
            await session.commit()
            print(f"\nDefault admin user created successfully!")
            print(f"Email: admin@autoclipper.local")
            print(f"API Key (Use this in the app): {raw_key}\n")
        else:
            print("Default admin user already exists.")

        # Seed system settings if not exists
        from app.models.models import SystemSetting
        for key, val in [
            ("payment_enabled", "false"),
            ("midtrans_client_key", ""),
            ("midtrans_server_key", ""),
            ("midtrans_is_production", "false")
        ]:
            s_res = await session.execute(select(SystemSetting).where(SystemSetting.key == key))
            if not s_res.scalar_one_or_none():
                session.add(SystemSetting(key=key, value=val))
        await session.commit()
        print("System settings seeded.")

if __name__ == "__main__":
    asyncio.run(seed())
