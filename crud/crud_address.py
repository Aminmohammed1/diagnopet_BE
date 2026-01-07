from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from db.models.address import Address
from schemas.address import CheckoutNewUser, AddressUpdate

async def get(db: AsyncSession, id: int) -> Optional[Address]:
    result = await db.execute(select(Address).filter(Address.id == id))
    return result.scalars().first()

async def get_multi_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[Address]:
    result = await db.execute(
        select(Address).filter(Address.user_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def create(db: AsyncSession, obj_in: CheckoutNewUser, user_id: int) -> Address:
    # if obj_in.is_default:
        # Unset existing default address for this user
        # await db.execute(
        #     Address.__table__.update()
        #     .where(Address.user_id == user_id)
        #     .values(is_default=False)
        # )
        
    db_obj = Address(
        user_id=user_id,
        address_line1=obj_in.address_line1,
        address_line2=obj_in.address_line2,
        city=obj_in.city,
        state=obj_in.state,
        postal_code=obj_in.postal_code,
        country=obj_in.country,
        google_maps_link=obj_in.google_maps_link,
        is_default=obj_in.is_default
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update(db: AsyncSession, db_obj: Address, obj_in: AddressUpdate) -> Address:
    update_data = obj_in.model_dump(exclude_unset=True)
    
    if update_data.get("is_default"):
        # Unset existing default address for this user
        await db.execute(
            Address.__table__.update()
            .where(Address.user_id == db_obj.user_id)
            .values(is_default=False)
        )
        
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def set_default(db: AsyncSession, address_id: int, user_id: int) -> Optional[Address]:
    # Unset existing default address for this user
    await db.execute(
        Address.__table__.update()
        .where(Address.user_id == user_id)
        .values(is_default=False)
    )
    
    # Set the new default address
    await db.execute(
        Address.__table__.update()
        .where(Address.id == address_id)
        .values(is_default=True)
    )
    
    await db.commit()
    return await get(db, address_id)

async def delete(db: AsyncSession, id: int) -> Optional[Address]:
    obj = await get(db, id)
    if obj:
        await db.delete(obj)
        await db.commit()
    return obj
