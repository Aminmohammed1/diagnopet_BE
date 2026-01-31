from pydantic import BaseModel
from typing import Optional


class TestCategoryBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True


class TestCategoryCreate(TestCategoryBase):
    name: str


class TestCategoryUpdate(TestCategoryBase):
    pass


class TestCategoryInDBBase(TestCategoryBase):
    id: int

    class Config:
        from_attributes = True


class TestCategory(TestCategoryInDBBase):
    pass
