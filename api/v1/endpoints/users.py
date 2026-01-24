from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.session import get_db
from schemas.user import User, UserCreate, UserUpdate, UserWithPetAndAddressInfo
from schemas.pet import Pet as PetSchema
from schemas.address import Address as AddressSchema
from crud import crud_user, crud_pet, crud_address

from api import deps

router = APIRouter()

@router.get("/me", response_model=User)
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
):
    return current_user

@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    users = await crud_user.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/all-user-info", response_model=UserWithPetAndAddressInfo)
async def read_user_with_pet_and_address_info(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all user information including pets and addresses.
    Returns is_new_user=True if user has no pets and no addresses.
    """
    # Fetch user's pets
    pets = await crud_pet.get_multi_by_user(db, user_id=current_user.id)
    
    # Fetch user's addresses
    addresses = await crud_address.get_multi_by_user(db, user_id=current_user.id)
    
    # Convert to response format
    pets_data = [PetSchema.model_validate(pet) for pet in pets]
    addresses_data = [AddressSchema.model_validate(address) for address in addresses]
    
    return UserWithPetAndAddressInfo(
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        pets=pets_data,
        addresses=addresses_data,
    )
 

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

@router.post("/user-is-active")
async def user_is_active(
    current_user: User = Depends(deps.get_current_user)):

    return {"user_is_active": current_user.is_active}