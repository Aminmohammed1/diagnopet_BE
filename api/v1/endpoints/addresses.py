from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.session import get_db
from db.models.user import User
from schemas.address import Address, AddressUpdate
from crud import crud_address
from api import deps

router = APIRouter()

# @router.post("/", response_model=Address)
# async def create_address(
#     address_in: AddressBase,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(deps.get_current_active_user),
# ):
#     """
#     Create a new address for the authenticated user.
#     User identity is derived from JWT, not request body.
#     """

#     return await crud_address.create(
#         db=db,
#         obj_in=address_in,
#         user_id=current_user.id
#     )


@router.get("/user/{user_id}", response_model=List[Address])
async def read_addresses_by_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    # Users can only view their own addresses, admins can view any
    if current_user.id != user_id and not current_user.is_superuser and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to view these addresses")
    return await crud_address.get_multi_by_user(db, user_id=user_id, skip=skip, limit=limit)

@router.get("/{address_id}", response_model=Address)
async def read_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    address = await crud_address.get(db, id=address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@router.put("/{address_id}", response_model=Address)
async def update_address(
    address_id: int,
    address_in: AddressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    address = await crud_address.get(db, id=address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return await crud_address.update(db, db_obj=address, obj_in=address_in)

@router.delete("/{address_id}", response_model=Address)
async def delete_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    address = await crud_address.get(db, id=address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return await crud_address.delete(db, id=address_id)

@router.post("/{address_id}/set-default", response_model=Address)
async def set_default_address(
    address_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    address = await crud_address.get(db, id=address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    if address.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this address")
    return await crud_address.set_default(db, address_id=address_id, user_id=user_id)
