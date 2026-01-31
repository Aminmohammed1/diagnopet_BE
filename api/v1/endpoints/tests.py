from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.session import get_db
from schemas.test import Test, TestCreate, TestUpdate
from crud import crud_test, crud_test_category
from db.models.user import User
from api import deps

router = APIRouter()

@router.get("/", response_model=List[Test])
async def read_tests(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    tests = await crud_test.get_multi(db, skip=skip, limit=limit)
    return tests

@router.post("/", response_model=Test)
async def create_test(
    test_in: TestCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(deps.get_current_admin_user)
):
    return await crud_test.create(db, obj_in=test_in)

@router.get("/categories", response_model=List[str])
async def get_all_categories_test(
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

@router.get("/{test_id}", response_model=Test)
async def read_test(
    test_id: int,
    db: AsyncSession = Depends(get_db)
):
    test = await crud_test.get(db, id=test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@router.put("/{test_id}", response_model=Test)
async def update_test(
    test_id: int,
    test_in: TestUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(deps.get_current_admin_user)
):
    test = await crud_test.get(db, id=test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return await crud_test.update(db, db_obj=test, obj_in=test_in)

@router.delete("/{test_id}", response_model=Test)
async def delete_test(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(deps.get_current_admin_user)

):
    test = await crud_test.get(db, id=test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return await crud_test.delete(db, id=test_id)