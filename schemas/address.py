from pydantic import BaseModel
from typing import Optional

class AddressBase(BaseModel):
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "India"
    google_maps_link: Optional[str] = None
    is_default: bool = False

class AddressCreate(AddressBase):
    user_id: int

class AddressUpdate(BaseModel):
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    google_maps_link: Optional[str] = None
    is_default: Optional[bool] = None

class AddressInDBBase(AddressBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class Address(AddressInDBBase):
    pass
