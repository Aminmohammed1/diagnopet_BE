from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class OrderBase(BaseModel):
    user_id: int
    booking_id: int
    booking_item_id: int
    file_link: Optional[str] = None

class OrderCreate(OrderBase):
    file_link: Optional[str] = None

class OrderUpdate(OrderBase):
    pass

class OrderInDBBase(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Order(OrderInDBBase):
    pass

# Response schema for detailed order information
class TestDetail(BaseModel):
    test_id: int
    test_name: str
    booking_item_id: int
    file_link: Optional[str] = None

class OrderDetailResponse(BaseModel):
    booking_id: int
    booking_date: datetime
    booking_address: str
    tests: List[TestDetail]

    class Config:
        from_attributes = True
