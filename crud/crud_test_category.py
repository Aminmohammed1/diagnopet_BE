from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from db.models.test_category import TestCategory
from schemas.test_category import TestCategoryCreate, TestCategoryUpdate


async def get(db: AsyncSession, id: int) -> Optional[TestCategory]:
    result = await db.execute(select(TestCategory).filter(TestCategory.id == id))
    return result.scalars().first()


async def get_by_name(db: AsyncSession, name: str) -> Optional[TestCategory]:
    result = await db.execute(select(TestCategory).filter(TestCategory.name == name))
    return result.scalars().first()


async def get_all(db: AsyncSession) -> List[TestCategory]:
    result = await db.execute(select(TestCategory))
    return result.scalars().all()


async def get_active(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[TestCategory]:
    result = await db.execute(
        select(TestCategory).filter(TestCategory.is_active == True).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def create(db: AsyncSession, obj_in: TestCategoryCreate) -> TestCategory:
    db_obj = TestCategory(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update(db: AsyncSession, db_obj: TestCategory, obj_in: TestCategoryUpdate) -> TestCategory:
    update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete(db: AsyncSession, id: int) -> Optional[TestCategory]:
    obj = await get(db, id)
    if obj:
        await db.delete(obj)
        await db.commit()
    return obj
