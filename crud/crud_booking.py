from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from fastapi import HTTPException
from db.models.booking import Booking
from db.models.booking_item import BookingItem
from db.models.test import Test
from schemas.booking import BookingCreate, BookingUpdate
from twilio.rest import Client
from core.config import settings
from utils.send_whatsapp_msg import new_send_whatsapp_template_via_twilio
import json
from crud import crud_address, crud_test


account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
twilio_whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER

twilio_client = Client(account_sid, auth_token)


async def get(db: AsyncSession, id: int) -> Optional[Booking]:
    result = await db.execute(
        select(Booking).options(selectinload(Booking.items)).filter(Booking.id == id)
    )
    return result.scalars().first()

async def get_multi(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Booking]:
    result = await db.execute(
        select(Booking).options(selectinload(Booking.items)).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def get_multi_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[Booking]:
    result = await db.execute(
        select(Booking).options(selectinload(Booking.items)).filter(Booking.user_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()
async def create(db: AsyncSession, obj_in: BookingCreate, user_id: int) -> Booking:
    # 0. Validate Test IDs
    unique_test_ids = list(set(obj_in.test_ids))
    result = await db.execute(select(Test.id).filter(Test.id.in_(unique_test_ids)))
    existing_ids = result.scalars().all()
    
    if len(existing_ids) != len(unique_test_ids):
        missing_ids = set(unique_test_ids) - set(existing_ids)
        raise HTTPException(status_code=400, detail=f"Tests with IDs {missing_ids} do not exist.")

    # 1. Create Booking
    #TODO should get gmap link of the locatoin from the front end.
    booking_data = obj_in.model_dump(exclude={"test_ids"})
    db_obj = Booking(**booking_data, user_id=user_id)
    db.add(db_obj)
    await db.flush()
    # 2. Create BookingItems
    msg = "Tests :"
    for i, test_id in enumerate(obj_in.test_ids):
        booking_item = BookingItem(booking_id=db_obj.id, test_id=test_id)
        db.add(booking_item)
        msg += f"\n{i+1}. {test_id}" 

    await db.commit()
    # 3. notify owner about the booking
    from crud import crud_user
    user = await crud_user.get(db, id=user_id)
    user_name = user.full_name if user else "Unknown User"
    try:
        content_sid = settings.TEMPLATE_ID  # Your template SID
        to = "+918639675595"  # Recipient's number
        address = await crud_address.get(db, obj_in.address_id)
        if not address or not address.google_maps_link:
            address_link = "Address link not provided"
        else:
            address_link = address.google_maps_link
        tests = await crud_test.get_by_list_of_ids(db, obj_in.test_ids)
        tests_names = ""
        for i, test in enumerate(tests):
            tests_names += f"{i+1}.{test.name} "
        user_name_with_date = f'{user_name} on {obj_in.booking_date.strftime("%d-%m-%Y %I:%M %p")}.'
        content_variables = json.dumps({
            "1": user_name_with_date,
            "2": address_link,
            "3": tests_names,
        })
        new_send_whatsapp_template_via_twilio(content_sid, to, content_variables)
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")
    return await get(db, db_obj.id)

async def update(db: AsyncSession, db_obj: Booking, obj_in: BookingUpdate) -> Booking:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return await get(db, db_obj.id)

async def delete(db: AsyncSession, id: int) -> Optional[Booking]:
    obj = await get(db, id)
    if obj:
        await db.delete(obj)
        await db.commit()
    return obj
