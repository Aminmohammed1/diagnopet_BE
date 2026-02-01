from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.session import get_db
from schemas.test_category import TestCategory, TestCategoryCreate, TestCategoryUpdate
from crud import crud_test_category
from db.models.user import User
from api import deps

router = APIRouter()

@router.get("/all", response_model=List[TestCategory])
async def get_all_categories_full(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(deps.get_current_admin_user)
):
    try:
        return await crud_test_category.get_all(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[str])
async def get_all_categories(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(deps.get_current_admin_user)
):
    try:
        result = []
        categories = await crud_test_category.get_all(db)
        for category in categories:
            result.append(category.name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=TestCategory)
async def create_category(
    category_in: TestCategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(deps.get_current_admin_user)
):
    return await crud_test_category.create(db, obj_in=category_in)

@router.get("/{category_id}", response_model=TestCategory)
async def read_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    category = await crud_test_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=TestCategory)
async def update_category(
    category_id: int,
    category_in: TestCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(deps.get_current_admin_user)
):
    category = await crud_test_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return await crud_test_category.update(db, db_obj=category, obj_in=category_in)

@router.delete("/{category_id}", response_model=TestCategory)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(deps.get_current_admin_user)
):
    category = await crud_test_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return await crud_test_category.delete(db, id=category_id)
