from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field
from api import deps
from crud import crud_booking, crud_user, crud_address, crud_pet, crud_test
from schemas.booking import Booking, BookingCreate, BookingUpdate, PhoneLookupRequest
from db.session import get_db
from db.models.user import User
from db.models.booking import Booking as BookingModel
from db.models.booking_item import BookingItem as BookingItemModel
from db.models.test import Test
from datetime import date, datetime

router = APIRouter()


@router.get("/", response_model=List[Booking])
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


@router.post("/", response_model=Booking)
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


@router.get("/{booking_id}", response_model=Booking)
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


@router.put("/{booking_id}", response_model=Booking)
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


@router.post("/lookup-by-phone", response_model=List[Booking])
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
            "booking_date": booking.booking_date,
            "status": booking.status,
            "address_id": booking.address_id,
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
        }
        booking_responses.append(Booking(**booking_dict))

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


# @router.post("/upcoming-bookings", response_model=UpcomingBookingsResponse)
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
            {"id": 1, "name": "Complete Blood Count (CBC)", "sample_type": "Blood"},
            {"id": 2, "name": "Liver Function Test", "sample_type": "Blood"}
        ],
        "total_amount": 2499.0,
        "created_at": "2026-01-25T10:30:00Z"
    }]
    """
    # Fetch upcoming bookings for the current user
    bookings = await crud_booking.get_upcoming_bookings(db=db, user_id=current_user.id)
    result = []
    from datetime import timezone
    import pytz

    ist = pytz.timezone("Asia/Kolkata")

    
    for booking in bookings:
        tests = await crud_test.get_tests_by_booking_id(db, booking.id)
        temp = {}
        temp["id"] = booking.id
        temp["booking_date"] = booking.booking_date
        utc_dt = booking.booking_date
        local_time = utc_dt.astimezone(ist).strftime("%I:%M %p")
        temp["booking_time"] = local_time
        temp["status"] = booking.status
        complete_address = await crud_address.get(db, booking.address_id)
        temp["address"] = complete_address.address_line1 + ", " + complete_address.address_line2 + ", " + complete_address.city + ", " + complete_address.state + "\n" + complete_address.postal_code
        temp["address_link"] = complete_address.google_maps_link
        temp["tests"] = [{
            "id": test.id,
            "name": test.name,
            "sample_type": test.sample_type
        } for test in tests]
        temp["total_amount"] = sum(test.price for test in tests) if tests else 0.0
        temp["created_at"] = booking.created_at
        result.append(temp)
    return result
