from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class TestBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    discounted_price: Optional[Decimal] = None
    sample_type: Optional[str] = None
    report_time_hours: Optional[int] = None
    is_active: Optional[bool] = True
    category_id: Optional[int] = None

class TestCreate(TestBase):
    name: str
    price: Decimal
    category_id: int

class TestUpdate(TestBase):
    pass

class TestInDBBase(TestBase):
    id: int

    class Config:
        from_attributes = True

class Test(TestInDBBase):
    pass
