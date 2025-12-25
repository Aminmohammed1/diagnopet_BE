from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.session import get_db
from schemas.user import User, UserCreate, UserUpdate
from crud import crud_user

router = APIRouter()

@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    users = await crud_user.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=User)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user = await crud_user.get_by_phone(db, phone=user_in.phone)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this phone already exists in the system.",
        )
    return await crud_user.create(db, obj_in=user_in)

@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/phone/{phone}", response_model=User)
async def read_user_by_phone(
    phone: str,
    db: AsyncSession = Depends(get_db)
):
    user = await crud_user.get_by_phone(db, phone=phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud_user.update(db, db_obj=user, obj_in=user_in)

@router.delete("/{user_id}", response_model=User)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud_user.delete(db, id=user_id)
