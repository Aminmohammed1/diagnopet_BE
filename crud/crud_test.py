from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from db.models.test import Test
from schemas.test import TestCreate, TestUpdate

async def get(db: AsyncSession, id: int) -> Optional[Test]:
    result = await db.execute(select(Test).filter(Test.id == id))
    return result.scalars().first()

async def get_multi(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Test]:
    result = await db.execute(select(Test).offset(skip).limit(limit))
    return result.scalars().all()

async def create(db: AsyncSession, obj_in: TestCreate) -> Test:
    db_obj = Test(**obj_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update(db: AsyncSession, db_obj: Test, obj_in: TestUpdate) -> Test:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete(db: AsyncSession, id: int) -> Optional[Test]:
    obj = await get(db, id)
    if obj:
        await db.delete(obj)
        await db.commit()
    return obj
