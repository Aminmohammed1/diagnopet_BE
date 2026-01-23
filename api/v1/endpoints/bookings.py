from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api import deps
from crud import crud_booking, crud_user
from schemas.booking import Booking, BookingCreate, BookingUpdate, PhoneLookupRequest
from db.session import get_db
from db.models.user import User
from db.models.booking import Booking as BookingModel
from db.models.booking_item import BookingItem as BookingItemModel
from db.models.test import Test

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
            "address": booking.address,
            "address_link": booking.address_link,
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


from pydantic import BaseModel, Field, HttpUrl, constr


class PetRegistrationRequest(BaseModel):
    owner_name: str = Field(..., description="Full name of the pet owner")
    pet_name: str = Field(..., description="Name of the pet")
    pet_species: str = Field(..., description="Species of the pet (e.g., Dog, Cat)")
    pet_breed: str = Field(..., description="Breed of the pet")
    pet_age: int = Field(..., ge=0, description="Age of the pet in years")
    pet_gender: str = Field(..., description="Gender of the pet (e.g., Male, Female)")
    pet_weight: float = Field(..., gt=0, description="Weight of the pet in kilograms")

    address_line1: str = Field(..., description="House / Flat / Street")
    address_line2: str = Field(
        ..., description="Area and Landmark concatenated into a single string"
    )
    city: str = Field(..., description="City name")
    postal_code: constr(min_length=4, max_length=10) = Field(
        ..., description="Postal / ZIP code"
    )
    google_maps_link: str = Field(..., description="Google Maps location link")


from crud import crud_address, crud_pet
from .addresses import AddressCreate
from schemas.user import UserUpdate
from schemas.pet import PetCreate


@router.post("/confirm-booking")
async def confirm_booking(
    data: PetRegistrationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Request:
    {
    owner_name: str,
    pet_name: str,
    pet_species: str,
    pet_breed: str,
    pet_age: int,
    pet_gender: str,
    pet_weight: float,
    address_line1: str,(House / Flat / Street)
    address_line2: str,(Area / Landmark)(concatenate Area and Landmark in a single string)
    city: str,
    postal_code: str,
    google_maps_link: str,(from map location),
    }
    """
    if current_user.is_active == False:  # means user is completely new to app
        # create new address for the user
        new_address = AddressCreate(user_id=current_user.id, **data.model_dump())
        await crud_address.create(db, obj_in=new_address)
        # update user details
        user_update = UserUpdate(
            full_name=data.owner_name,
            is_active=True,  # User becomes active on successful registration
        )
        await crud_user.update(db, db_obj=current_user, obj_in=user_update)
        user_new_pet = PetCreate(
            name=data.pet_name,
            species=data.pet_species,
            breed=data.pet_breed,
            gender=data.pet_gender,
            age=data.pet_age,
            weight=data.pet_weight,
        )
        await crud_pet.create(db, obj_in=user_new_pet, user_id=current_user.id)
        return {"msg": "Booking confirmed for new user with new pet and address."}
