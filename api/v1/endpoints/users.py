from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.session import get_db
from schemas.user import User, UserCreate, UserUpdate
from crud import crud_address, crud_user
from schemas.address import CheckoutNewUser
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    # Only admins can list all users
    users = await crud_user.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=User)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    # Only admins can create users
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    # Users can view their own profile, admins can view any
    if current_user.id != user_id and not current_user.is_superuser and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to view this user")
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/phone/{phone}", response_model=User)
async def read_user_by_phone(
    phone: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin_or_staff_user)
):
    # Only admin/staff can lookup users by phone
    user = await crud_user.get_by_phone(db, phone=phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    # Users can update their own profile, admins can update any
    if current_user.id != user_id and not current_user.is_superuser and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud_user.update(db, db_obj=user, obj_in=user_in)

@router.delete("/{user_id}", response_model=User)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    # Only admins can delete users
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud_user.delete(db, id=user_id)
from crud import crud_pet
from schemas.pet import PetBase
@router.post("/checkout-new-user")
async def checkout_new_user(
    data: CheckoutNewUser,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    user = await crud_user.get(db, id=current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pet = PetBase(
        name=data.pet_name, species="cat", age_years=data.pet_age, weight_kg=data.pet_weight)
    # Create a UserUpdate object with the full_name to update
    from schemas.user import UserUpdate
    user_update = UserUpdate(full_name=data.full_name)
    await crud_user.update(db, db_obj=user, obj_in=user_update)
    await crud_pet.create(
        db=db,
        obj_in=pet,
        user_id=current_user.id
    )
    # Create a new address for the current user
    await crud_address.create(
        db=db,
        obj_in=data,
        user_id=current_user.id
    )
    return {"message": "Checkout data saved successfully"}