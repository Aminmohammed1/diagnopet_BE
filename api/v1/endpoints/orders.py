from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from db.session import get_db
from api.deps import get_current_user
from db.models.user import User
from crud import crud_order
from schemas.order import OrderDetailResponse

router = APIRouter()


@router.get("/user-orders", response_model=List[OrderDetailResponse])
async def get_user_orders(
    booking_id: Optional[int] = Query(None, description="Filter by booking ID"),
    booking_item_id: Optional[int] = Query(None, description="Filter by booking item ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all orders for the current user with detailed information including:
    - Booking date
    - Booking address
    - Test details (test name, booking item ID)
    - File link for downloading the report
    
    Optional filters:
    - booking_id: Filter orders by a specific booking
    - booking_item_id: Filter orders by a specific booking item (test)
    """
    crud = crud_order.CrudOrder(db)
    
    orders = await crud.get_user_orders_with_details(
        user_id=current_user.id,
        booking_id=booking_id,
        booking_item_id=booking_item_id
    )
    
    if not orders:
        return []
    
    return orders
