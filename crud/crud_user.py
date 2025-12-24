from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from db.models.user import User
from schemas.user import UserCreate, UserUpdate
from core.security import get_password_hash

async def get(db: AsyncSession, id: int) -> Optional[User]:
    result = await db.execute(select(User).filter(User.id == id))
    return result.scalars().first()

async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def get_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.phone == phone))
    return result.scalars().first()

async def get_multi(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

async def create(db: AsyncSession, obj_in: UserCreate) -> User:
    db_obj = User(
        email=obj_in.email,
        phone=obj_in.phone,
        hashed_password=get_password_hash(obj_in.password),
        full_name=obj_in.full_name,
        is_active=obj_in.is_active,
        is_superuser=obj_in.is_superuser,
        is_verified=obj_in.is_verified,
        role=obj_in.role,
    )

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update(db: AsyncSession, db_obj: User, obj_in: UserUpdate) -> User:
    update_data = obj_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete(db: AsyncSession, id: int) -> Optional[User]:
    obj = await get(db, id)
    if obj:
        await db.delete(obj)
        await db.commit()
    return obj
