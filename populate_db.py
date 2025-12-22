import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings
from db.base import Base
from db.models.test_category import TestCategory
from db.models.test import Test
from db.models.test_tag import TestTag

from sqlalchemy import text

# Ensure we are using the correct database URL
print(f"Using DATABASE_URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'INVALID_URL_FORMAT'}")

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if data exists
        existing_categories = await session.execute(
            text("SELECT count(*) FROM test_categories")
        )
        if existing_categories.scalar() > 0:
            print("Data already exists. Skipping population.")
            return

        # Create Categories
        cat_blood = TestCategory(name="Blood Test", description="Hematology and Biochemistry")
        cat_urine = TestCategory(name="Urine Test", description="Urinalysis")
        cat_imaging = TestCategory(name="Imaging", description="X-Ray, Ultrasound, CT, MRI")
        
        session.add_all([cat_blood, cat_urine, cat_imaging])
        await session.commit()
        await session.refresh(cat_blood)
        await session.refresh(cat_urine)
        await session.refresh(cat_imaging)

        # Create Tests
        test_cbc = Test(
            category_id=cat_blood.id,
            name="CBC (Complete Blood Count)",
            description="Evaluates overall health and detects a wide range of disorders.",
            price=500.00,
            discounted_price=450.00,
            sample_type="Blood",
            report_time_hours=24,
            is_active=True
        )
        test_lipid = Test(
            category_id=cat_blood.id,
            name="Lipid Profile",
            description="Measures cholesterol and triglycerides.",
            price=800.00,
            sample_type="Blood",
            report_time_hours=24,
            is_active=True
        )
        test_urine = Test(
            category_id=cat_urine.id,
            name="Urine Routine",
            description="Physical, chemical, and microscopic examination of urine.",
            price=300.00,
            sample_type="Urine",
            report_time_hours=12,
            is_active=True
        )
        test_xray = Test(
            category_id=cat_imaging.id,
            name="X-Ray Chest PA View",
            description="Radiograph of the chest.",
            price=600.00,
            report_time_hours=1,
            is_active=True
        )

        session.add_all([test_cbc, test_lipid, test_urine, test_xray])
        await session.commit()
        
        # Create Tags
        tag_cbc_1 = TestTag(test_id=test_cbc.id, tag="Basic")
        tag_cbc_2 = TestTag(test_id=test_cbc.id, tag="Health Checkup")
        tag_lipid = TestTag(test_id=test_lipid.id, tag="Heart Health")

        session.add_all([tag_cbc_1, tag_cbc_2, tag_lipid])
        await session.commit()

        print("Sample data populated successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
