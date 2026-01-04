from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PetBase(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    age_years: Optional[float] = None
    weight_kg: Optional[float] = None
    medical_history: Optional[str] = None
    is_active: Optional[bool] = True

class PetCreate(PetBase):
    user_id: int

class PetUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    age_years: Optional[float] = None
    weight_kg: Optional[float] = None
    medical_history: Optional[str] = None
    is_active: Optional[bool] = None

class PetCreateBase(PetBase):
    pass    

class Pet(PetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
