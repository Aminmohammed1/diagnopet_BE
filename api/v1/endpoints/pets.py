from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from db.session import get_db
from schemas.pet import Pet, PetCreate, PetUpdate
from crud import crud_pet
from api import deps

router = APIRouter()

@router.get("/", response_model=List[Pet])
async def read_pets(
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve pets. If user_id is provided, filter by user.
    """
    if user_id:
        pets = await crud_pet.get_multi_by_owner(db, user_id=user_id, skip=skip, limit=limit)
    else:
        # For now, let's just return all pets if no user_id is provided
        # In a real app, this might be restricted to admins
        from sqlalchemy.future import select
        from db.models.pet import Pet as PetModel
        result = await db.execute(select(PetModel).offset(skip).limit(limit))
        pets = result.scalars().all()
    return pets

@router.post("/", response_model=Pet)
async def create_pet(
    pet_in: PetCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new pet.
    """
    return await crud_pet.create(db, obj_in=pet_in)

@router.get("/{pet_id}", response_model=Pet)
async def read_pet(
    pet_id: int,
    db: AsyncSession = Depends(get_db)
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
    db: AsyncSession = Depends(get_db)
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
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a pet.
    """
    pet = await crud_pet.get(db, id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return await crud_pet.delete(db, id=pet_id)
