from pydantic import BaseModel
from typing import Optional

class PetBase(BaseModel):
    name: str
    species: str
    breed: str
    age: int
    gender: str
    weight: float

class PetCreate(PetBase):
    pass

class PetUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[float] = None

class PetInDBBase(PetBase):
    id: int
    # user_id: int

    class Config:
        from_attributes = True

class Pet(PetInDBBase):
    pass