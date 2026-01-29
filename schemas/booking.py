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
    status: Optional[str] = "confirmed"
    address_id: int


class BookingCreate(BookingBase):
    test_ids: List[int]


class BookingUpdate(BaseModel):
    status: Optional[str] = None
    booking_date: Optional[datetime] = None
    address_id: Optional[int] = None


class BookingInDBBase(BookingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    items: List[BookingItem] = []

    class Config:
        from_attributes = True


from schemas.address import Address

class Booking(BookingInDBBase):
    address: Optional[Address] = None
    address_link: Optional[str] = None
    booking_item_ids: List[int] = []


class PhoneLookupRequest(BaseModel):
    phone: str
