from pydantic import BaseModel
from typing import Optional
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
