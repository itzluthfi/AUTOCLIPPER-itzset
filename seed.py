import asyncio
import sys
import os

# Put backend path in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, async_session, Base
from app.models.models import User, SystemSetting
from app.security import hash_api_key, hash_password
from sqlalchemy import select

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print("Checking for default admin user...")
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == "admin@autoclipper.com"))
        user = result.scalar_one_or_none()
        
        raw_key = "ac_admin_secret_key_123"
        hashed_key = hash_api_key(raw_key)
        pwd_hash = hash_password("AdminPass123!")

        if not user:
            print("Creating default admin user...")
            user = User(
                email="admin@autoclipper.com",
                password_hash=pwd_hash,
                name="Administrator",
                role="admin",
                api_key=hashed_key,
                credits=999
            )
            session.add(user)
            await session.commit()
            print("\nDefault Admin created successfully!")
        else:
            user.role = "admin"
            user.password_hash = pwd_hash
            user.api_key = hashed_key
            user.credits = 999
            await session.commit()
            print("Default Admin updated successfully.")

        print(f"\nAKUN ADMIN AUTOCLIPPER:")
        print(f"   Email    : admin@autoclipper.com")
        print(f"   Password : AdminPass123!")
        print(f"   API Key  : {raw_key}\n")

if __name__ == "__main__":
    asyncio.run(seed())
