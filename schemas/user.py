from pydantic import BaseModel, EmailStr
from typing import Optional
from schemas.address import AddressBase
from schemas.pet import Pet

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = False
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    role: Optional[str] = "USER"


class UserCreate(UserBase):
    email: EmailStr
    phone: str
    password: str
    full_name: str

class OnboardingUser(UserBase):
    email: EmailStr
    phone: str
    password: str
    full_name: str
    pets: list[Pet]
    address: AddressBase

class UserLogin(UserBase):
    phone: str
    password: str  

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserWithPetAndAddressInfo(BaseModel):
    full_name: str = None
    is_active: bool = False
    pets: list[Pet] = []
    addresses: list[AddressBase] = []

    class Config:
        from_attributes = True

