import asyncio
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from db.session import AsyncSessionLocal

async def add_role_column():
    print("Adding role column to users table...")
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'USER'"))
            await session.commit()
            print("✅ Column 'role' added successfully.")
        except Exception as e:
            print(f"⚠️ Error adding column (might already exist): {e}")

if __name__ == "__main__":
    asyncio.run(add_role_column())
