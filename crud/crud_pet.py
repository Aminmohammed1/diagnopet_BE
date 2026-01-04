from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from db.models.pet import Pet
from schemas.pet import PetCreate, PetUpdate

async def get(db: AsyncSession, id: int) -> Optional[Pet]:
    result = await db.execute(select(Pet).filter(Pet.id == id))
    return result.scalars().first()

async def get_multi_by_owner(
    db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
) -> List[Pet]:
    result = await db.execute(
        select(Pet)
        .filter(Pet.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create(db: AsyncSession, *, obj_in: PetCreate) -> Pet:
    db_obj = Pet(
        user_id=obj_in.user_id,
        name=obj_in.name,
        species=obj_in.species,
        breed=obj_in.breed,
        age_years=obj_in.age_years,
        weight_kg=obj_in.weight_kg,
        medical_history=obj_in.medical_history,
        is_active=obj_in.is_active,
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update(
    db: AsyncSession, *, db_obj: Pet, obj_in: PetUpdate
) -> Pet:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete(db: AsyncSession, *, id: int) -> Optional[Pet]:
    obj = await get(db, id)
    if obj:
        await db.delete(obj)
        await db.commit()
    return obj
