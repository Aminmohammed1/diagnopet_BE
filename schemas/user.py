from pydantic import BaseModel, EmailStr
from typing import Optional
from schemas.address import AddressBase

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
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

class Pet(BaseModel):
    name: str
    species: str
    breed: str
    age: int
    gender: str
    weight: float
