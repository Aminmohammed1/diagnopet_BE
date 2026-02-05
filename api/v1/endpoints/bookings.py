from crud.crud_order import CrudOrder
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field
from api import deps

from crud import crud_booking, crud_user, crud_address, crud_pet, crud_test, crud_order
from schemas.booking import Booking as BookingSchema
from schemas.booking import (
    BookingCreate,
    BookingUpdate,
    PhoneLookupRequest,
)

from db.session import get_db
from db.models.user import User
from db.models.booking import Booking as BookingModel
from db.models.booking_item import BookingItem as BookingItemModel
from db.models.test import Test
from datetime import date, datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta

router = APIRouter()


@router.get("/", response_model=List[BookingSchema])
async def read_bookings(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve bookings.
    """
    if (
        current_user.is_superuser
        or current_user.role == "ADMIN"
        or current_user.role == "STAFF"
    ):
        bookings = await crud_booking.get_multi(db, skip=skip, limit=limit)
    else:
        bookings = await crud_booking.get_multi_by_user(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    return bookings


@router.post("/", response_model=BookingSchema)
async def create_booking(
    *,
    db: AsyncSession = Depends(get_db),
    booking_in: BookingCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new booking.
    """
    booking = await crud_booking.create(
        db=db, obj_in=booking_in, user_id=current_user.id
    )
    return booking


@router.get("/{booking_id}", response_model=BookingSchema)
async def read_booking(
    *,
    db: AsyncSession = Depends(get_db),
    booking_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get booking by ID.
    """
    booking = await crud_booking.get(db=db, id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if not current_user.is_superuser and (booking.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return booking


@router.put("/{booking_id}", response_model=BookingSchema)
async def update_booking(
    *,
    db: AsyncSession = Depends(get_db),
    booking_id: int,
    booking_in: BookingUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a booking.
    """
    booking = await crud_booking.get(db=db, id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if not current_user.is_superuser and (booking.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    booking = await crud_booking.update(db=db, db_obj=booking, obj_in=booking_in)
    return booking


@router.post("/lookup-by-phone", response_model=List[BookingSchema])
async def get_bookings_by_phone(
    *,
    db: AsyncSession = Depends(get_db),
    phone_request: PhoneLookupRequest,
    current_user: User = Depends(deps.get_current_admin_or_staff_user),
) -> Any:
    """
    Get all bookings for a user by phone number (admin/staff/superuser only).
    """
    # Find user by phone number
    user = await crud_user.get_by_phone(db=db, phone=phone_request.phone)
    if not user:
        raise HTTPException(
            status_code=404, detail="User not found with this phone number"
        )

    # Get all bookings for this user with test names
    result = await db.execute(
        select(BookingModel)
        .options(selectinload(BookingModel.address))
        .filter(BookingModel.user_id == user.id)
        .order_by(BookingModel.created_at.desc())
    )
    print("Result is:", result)
    bookings = result.scalars().all()

    # Manually construct the response with test names
    booking_responses = []
    for booking in bookings:
        # Get booking items with test names
        if booking.status == "done":
            continue
        items_result = await db.execute(
            select(BookingItemModel, Test.name)
            .join(Test, BookingItemModel.test_id == Test.id)
            .filter(BookingItemModel.booking_id == booking.id)
        )
        items_with_names = items_result.all()
        # Construct booking response
        booking_dict = {
            "id": booking.id,
            "user_id": booking.user_id,
            "address_id": booking.address_id,
            "booking_date": booking.booking_date,
            "status": booking.status,
            "address": booking.address,
            "address_link": booking.address.google_maps_link if booking.address else "",
            "created_at": booking.created_at,
            "updated_at": booking.updated_at,
            "items": [
                {
                    "id": item.id,
                    "booking_id": item.booking_id,
                    "test_id": item.test_id,
                    "test_name": test_name,
                }
                for item, test_name in items_with_names
            ],
            "booking_item_ids": [item.id for item, _ in items_with_names],
        }
        booking_responses.append(BookingSchema(**booking_dict))

    return booking_responses


class PetRegistrationRequest(BaseModel):
    pet_id: int = Field(..., description="ID of the user's pet")
    address_id: int = Field(..., description="ID of the user's address")
    test_ids: list[int] = Field(
        ..., description="List of test IDs to be included in the booking"
    )
    date_time: str = Field(..., description="Preferred date and time for the booking")


class TestItem(BaseModel):
    id: int
    name: str
    sample_type: str


class UpcomingBookingsResponse(BaseModel):
    id: int = Field(..., description="ID of the booking")
    booking_date: date = Field(..., description="Date of the booking")
    booking_time: str = Field(..., description="Time of the booking (AM/PM format)")
    status: str = Field(..., description="Status of the booking")
    address: str = Field(..., description="Address for the booking")
    address_link: str = Field(..., description="Google Maps link for the address")
    tests: List[TestItem] = Field(..., description="List of tests in the booking")
    total_amount: float = Field(..., description="Total amount for the booking")
    created_at: datetime = Field(..., description="Creation timestamp of the booking")

    class Config:
        schema_extra = {
            "example": {
                "id": 101,
                "booking_date": "2026-01-28",
                "booking_time": "10:00 AM",
                "status": "confirmed",
                "address": "123 Pet Street, Hyderabad, Telangana 500001",
                "address_link": "https://maps.google.com/?q=123+Pet+Street+Hyderabad",
                "tests": [
                    {
                        "id": 1,
                        "name": "Complete Blood Count (CBC)",
                        "sample_type": "Blood",
                    },
                    {"id": 2, "name": "Liver Function Test", "sample_type": "Blood"},
                ],
                "total_amount": 2499.0,
                "created_at": "2026-01-25T10:30:00Z",
            }
        }


@router.post("/confirm-booking")
async def confirm_booking(
    data: PetRegistrationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Request:
    {
        "pet_id": 1,
        "address_id": 2,
        "test_ids": [1, 2, 3],
        "date_time": "2024-07-01T10:00:00"
    }
    """
    # Validate data sent from frontend to check if the address and pet belong to the user
    if (
        current_user.id != (await crud_address.get(db, data.address_id)).user_id
        or current_user.id != (await crud_pet.get(db, data.pet_id)).user_id
    ):
        raise HTTPException(
            status_code=400, detail="Address/pet id does not belong to user"
        )
    # Create booking
    new_booking = BookingCreate(
        booking_date=data.date_time, address_id=data.address_id, test_ids=data.test_ids
    )
    await crud_booking.create(db=db, obj_in=new_booking, user_id=current_user.id)
    return {"message": "Booking confirmed successfully"}

@router.post("/upcoming-bookings")
async def get_upcoming_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Request: Payload None, only token authentication is required.
    Response:
    [{
        "id": 101,
        "booking_date": "2026-01-28",
        "booking_time": "10:00 AM",
        "status": "confirmed",
        "address": "123 Pet Street, Hyderabad, Telangana 500001",
        "address_link": "https://maps.google.com/?q=123+Pet+Street+Hyderabad",
        "tests": [
            {
                "id": 1, 
                "name": "Complete Blood Count (CBC)", 
                "sample_type": "Blood",
                "booking_item_id": 10,
                "file_link": "https://..."
            },
            {
                "id": 2, 
                "name": "Liver Function Test", 
                "sample_type": "Blood",
                "booking_item_id": 11,
                "file_link": "https://..."
            }
        ],
        "total_amount": 2499.0,
        "created_at": "2026-01-25T10:30:00Z"
    }]
    """
    # Fetch all orders for the current user
    orders = await CrudOrder(db=db).get_orders_by_user(user_id=current_user.id)
    
    from datetime import timezone
    import pytz
    ist = pytz.timezone("Asia/Kolkata")

    print("these are the orders", orders)
    
    # Group orders by booking_id
    bookings_dict = {}
    
    for order in orders:
        booking_id = order.booking_id
        
        # Initialize booking entry if not exists
        if booking_id not in bookings_dict:
            # Fetch booking details from the booking model
            booking_model = await crud_booking.get(db, booking_id)
            if not booking_model:
                continue
                
            # Get address details
            complete_address = await crud_address.get(db, booking_model.address_id)
            
            # Convert UTC to IST for display
            utc_dt = booking_model.booking_date
            local_time = utc_dt.astimezone(ist).strftime("%I:%M %p")
            
            # Build address string
            address_parts = []
            if complete_address.address_line1:
                address_parts.append(complete_address.address_line1)
            if complete_address.address_line2:
                address_parts.append(complete_address.address_line2)
            if complete_address.city:
                address_parts.append(complete_address.city)
            if complete_address.state:
                address_parts.append(complete_address.state)
            if complete_address.postal_code:
                address_parts.append(complete_address.postal_code)
            
            bookings_dict[booking_id] = {
                "id": booking_id,
                "booking_date": booking_model.booking_date.date(),
                "booking_time": local_time,
                "status": booking_model.status,
                "address": ", ".join(address_parts),
                "address_link": complete_address.google_maps_link if complete_address.google_maps_link else "",
                "tests": [],
                "created_at": booking_model.created_at,
            }
        
        # Fetch test details for this booking item
        booking_item = await db.get(BookingItemModel, order.booking_item_id)
        if booking_item:
            test = await crud_test.get(db, booking_item.test_id)
            if test:
                # Add test with booking_item_id and file_link
                bookings_dict[booking_id]["tests"].append({
                    "id": test.id,
                    "name": test.name,
                    "sample_type": test.sample_type,
                    "booking_item_id": order.booking_item_id,
                    "file_link": order.file_link if order.file_link else None
                })
    
    # Calculate total_amount for each booking and convert to list
    result = []
    for booking_data in bookings_dict.values():
        # Get all test prices for this booking
        test_prices = []
        for test_info in booking_data["tests"]:
            test = await crud_test.get(db, test_info["id"])
            if test:
                test_prices.append(test.price)
        
        booking_data["total_amount"] = sum(test_prices) if test_prices else 0.0
        result.append(booking_data)
    
    # Sort by booking_date descending (most recent first)
    result.sort(key=lambda x: x["created_at"], reverse=True)
    
    return result

from pydantic import BaseModel, Field

class AdminBillingRequest(BaseModel):
    # month: int = Field(..., ge=1, le=12)
    # year: int = Field(..., ge=2000)
    # day: int | None = Field(None, ge=1, le=31)
    start_date: str = Field(..., description="Start ISO date time string")
    end_date: str = Field(..., description="End ISO date time string")
    
from db.models.booking import Booking
async def response_builder(bookings: List[Booking], db: AsyncSession) -> List[Any]:
    result = []
    for booking in bookings:
        temp = {}
        temp["booking_id"] = booking.id
        customer = await crud_user.get(db, booking.user_id)
        temp["customer"] = customer.full_name
        temp["phone_number"] = customer.phone
        temp["date"] = booking.booking_date
        temp["status"] = booking.status
        tests = await crud_test.get_tests_by_booking_id(db, booking.id)
        temp["tests"] = [{
            "id": test.id,
            "name": test.name,
            "sample_type": test.sample_type,
            "price": test.price
        } for test in tests]
        temp["amount"] = sum(test.price for test in tests) if tests else 0.0
        result.append(temp)
    return result

@router.post("/admin/billing")
async def get_filtered_bookings(
    request: AdminBillingRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(deps.get_current_admin_user),
) -> Any:

    # Parse ISO format strings and handle IST timezone
    # IST is UTC+5:30
    try:
        ist_tz = timezone(timedelta(hours=5, minutes=30))
        
        # Parse the ISO string
        if request.start_date.endswith('Z'):
            # Already in UTC
            start_dt = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
        else:
            # Assume IST if no timezone info, convert to UTC
            start_dt = datetime.fromisoformat(request.start_date)
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=ist_tz)
            start_dt = start_dt.astimezone(timezone.utc)
        
        if request.end_date.endswith('Z'):
            # Already in UTC
            end_dt = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
        else:
            # Assume IST if no timezone info, convert to UTC
            end_dt = datetime.fromisoformat(request.end_date)
            if end_dt.tzinfo is None:
                end_dt = end_dt.replace(tzinfo=ist_tz)
            end_dt = end_dt.astimezone(timezone.utc)
        filtered_bookings = await db.execute(select(Booking).where(
            Booking.booking_date >= start_dt,
            Booking.booking_date <= end_dt,
        ).order_by(Booking.booking_date.asc()))
        result = await response_builder(filtered_bookings.scalars().all(), db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format(must be ISO)/error occured in processing\n{e}")

@router.get("/admin/billing/{date_str}")
async def get_today_bookings(
    date_str: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(deps.get_current_admin_user),
) -> Any:
    from sqlalchemy import Date, cast
    import pytz
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    if date_str == "today":
        target_date = now.date()
        result = await db.execute(select(Booking).where(
            cast(Booking.booking_date, Date) == target_date
        ))
        bookings = result.scalars().all()
        return await response_builder(bookings, db)
    elif date_str == "month":
          # Get current time in IST
        first_day = now.replace(day=1).date()
        last_day = (now.replace(day=1) + relativedelta(months=1) - timedelta(days=1)).date()
        result = await db.execute(select(Booking).where(
            cast(Booking.booking_date, Date) >= first_day,
            cast(Booking.booking_date, Date) <= last_day
        ).order_by(Booking.booking_date.asc()))
        bookings = result.scalars().all()
        return await response_builder(bookings, db)
    elif date_str == "pending":
        past_confirmed_bookings = await db.execute(select(Booking).where(Booking.booking_date < now, Booking.status == "confirmed").order_by(Booking.booking_date.asc()))
        bookings = past_confirmed_bookings.scalars().all()
        return await response_builder(bookings, db)
    elif date_str == "future":
        future_bookings = await db.execute(select(Booking).where(Booking.booking_date >= now).order_by(Booking.booking_date.asc()))
        bookings = future_bookings.scalars().all()
        return await response_builder(bookings, db)
    elif date_str == "all":
        all_bookings = await db.execute(select(Booking).order_by(Booking.booking_date.desc()))
        bookings = all_bookings.scalars().all()
        return await response_builder(bookings, db)
    raise HTTPException(status_code=400, detail="Invalid date parameter")

class UpdateBookingStatusRequest(BaseModel):
    booking_id: int = Field(..., description="ID of the booking to update")
    status: str = Field(..., description="New status for the booking")

@router.post("/admin/booking-status-update")
async def update_booking_status(
    request: UpdateBookingStatusRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(deps.get_current_admin_user),
) -> Any:
    """
    Update booking status (admin/staff/superuser only).
    """
    booking = await crud_booking.get(db=db, id=request.booking_id)
    if not booking:
        raise HTTPException(status_code=400, detail="Booking not found")
    booking_in = BookingUpdate(status=request.status)
    booking = await crud_booking.update(db=db, db_obj=booking, obj_in=booking_in)
    return {"message": f"Booking {booking.id} status updated to {request.status} successfully"}