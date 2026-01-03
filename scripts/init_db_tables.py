#!/usr/bin/env python
"""
Initialize database by creating all tables from models
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from db.base import Base
from core.config import settings
# Import all models to register them
from db import models

async def init_database():
    """Create all tables using SQLAlchemy metadata"""
    
    if not settings.DATABASE_URL:
        print("Error: DATABASE_URL not set in .env")
        sys.exit(1)
    
    print(f"Initializing database: {settings.DATABASE_URL[:60]}...")
    
    try:
        # Create async engine
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✓ All base tables created successfully!")
        print("\nTables created:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(init_database())
