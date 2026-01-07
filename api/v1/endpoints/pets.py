from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from db.session import get_db
from db.models.user import User
from schemas.pet import Pet, PetBase, PetUpdate
from crud import crud_pet
from api import deps

router = APIRouter()

@router.get("/", response_model=List[Pet])
async def read_pets(
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retrieve pets. If user_id is provided, filter by user.
    Users can only view their own pets, admins can view any.
    """
    if user_id:
        # Check authorization
        if current_user.id != user_id and not current_user.is_superuser and current_user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Not authorized to view these pets")
        pets = await crud_pet.get_multi_by_owner(db, user_id=user_id, skip=skip, limit=limit)
    else:
        # If no user_id provided, return current user's pets
        if current_user.is_superuser or current_user.role == "ADMIN":
            # Admins can view all pets
            from sqlalchemy.future import select
            from db.models.pet import Pet as PetModel
            result = await db.execute(select(PetModel).offset(skip).limit(limit))
            pets = result.scalars().all()
        else:
            # Regular users see their own pets
            pets = await crud_pet.get_multi_by_owner(db, user_id=current_user.id, skip=skip, limit=limit)
    return pets

@router.post("/", response_model=Pet)
async def create_pet(
    pet_in: PetBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Create a new pet.
    """
    return await crud_pet.create(db, obj_in=pet_in, user_id=current_user.id)

@router.get("/{pet_id}", response_model=Pet)
async def read_pet(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get pet by ID.
    """
    pet = await crud_pet.get(db, id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
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
    return await crud_pet.delete(db, id=pet_id)
