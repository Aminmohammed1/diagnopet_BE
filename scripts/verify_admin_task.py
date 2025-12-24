import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from db.session import AsyncSessionLocal
from db.models.user import User
from core.config import settings
from core.security import verify_password

from db.init_db import init_db

async def verify_admin_creation():
    print("Verifying Admin Creation...")
    async with AsyncSessionLocal() as session:
        # Run init_db to simulate startup
        print("Running init_db...")
        await init_db(session)
        
        # Check if admin exists
        result = await session.execute(select(User).filter(User.email == settings.ADMIN_EMAIL))
        user = result.scalars().first()
        
        if not user:
            print("❌ Admin user not found!")
            return
        
        print(f"✅ Admin user found: {user.email}")
        
        # Check role
        if user.role != "ADMIN":
            print(f"❌ Incorrect role: {user.role}")
        else:
            print(f"✅ Role is correct: {user.role}")
            
        # Check superuser status
        if not user.is_superuser:
            print("❌ Not a superuser")
        else:
            print("✅ Is superuser")

        # Verify password (optional, if we knew the plain text, but here we just check existence)
        # We can't easily check password hash without the plain text from env, which we have.
        if settings.ADMIN_PASSWORD:
             if verify_password(settings.ADMIN_PASSWORD, user.hashed_password):
                 print("✅ Password verification successful")
             else:
                 print("❌ Password verification failed")

if __name__ == "__main__":
    asyncio.run(verify_admin_creation())
