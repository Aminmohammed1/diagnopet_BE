from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api import deps
from crud import crud_booking
from schemas.booking import Booking, BookingCreate, BookingUpdate
from db.session import get_db
from db.models.user import User

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
    if current_user.is_superuser:
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
    booking = await crud_booking.create(db=db, obj_in=booking_in, user_id=current_user.id)
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
