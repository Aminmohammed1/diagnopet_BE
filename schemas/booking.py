from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class BookingItemBase(BaseModel):
    test_id: int

class BookingItemCreate(BookingItemBase):
    pass

class BookingItem(BookingItemBase):
    id: int
    booking_id: int
    test_name: Optional[str] = None

    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    booking_date: datetime
    status: Optional[str] = "pending"
    address: str
    address_link: Optional[str] = None

class BookingCreate(BookingBase):
    test_ids: List[int]

class BookingUpdate(BaseModel):
    status: Optional[str] = None
    booking_date: Optional[datetime] = None
    address: Optional[str] = None
    address_link: Optional[str] = None

class BookingInDBBase(BookingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    items: List[BookingItem] = []

    class Config:
        from_attributes = True

class Booking(BookingInDBBase):
    pass

class PhoneLookupRequest(BaseModel):
    phone: str
