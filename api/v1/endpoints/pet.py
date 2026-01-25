from crud import crud_pet, crud_user
from schemas.user import UserUpdate
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from schemas.pet import Pet, PetCreate, PetUpdate
from api import deps
from schemas.user import User

router = APIRouter()

@router.post("/", response_model=Pet)
async def create_pet(
    pet_in: PetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    await crud_user.update(db, db_obj=current_user, obj_in=UserUpdate(is_active=True, full_name=pet_in.userFullName))
    return await crud_pet.create(db, obj_in=pet_in, user_id=current_user.id)

@router.get("/", response_model=List[Pet])
async def read_pets(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retrieve pets for the current user.
    """
    return await crud_pet.get_multi_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{pet_id}", response_model=Pet)
async def read_pet(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get a specific pet by ID.
    """
    pet = await crud_pet.get(db, id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    if pet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return pet

@router.put("/{pet_id}", response_model=Pet)
async def update_pet(
    pet_id: int,
    pet_in: PetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Update a pet.
    """
    pet = await crud_pet.get(db, id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    if pet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud_pet.update(db, db_obj=pet, obj_in=pet_in)

@router.delete("/{pet_id}", response_model=Pet)
async def delete_pet(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Delete a pet.
    """
    pet = await crud_pet.get(db, id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    if pet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud_pet.delete(db, id=pet_id)