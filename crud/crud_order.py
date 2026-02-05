from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional
from fastapi import HTTPException
from db.models.order import Order
from db.models.booking import Booking
from db.models.booking_item import BookingItem
from db.models.test import Test
from db.models.address import Address
from schemas.order import OrderCreate, OrderUpdate
from twilio.rest import Client
from core.config import settings
from utils.send_whatsapp_msg import new_send_whatsapp_template_via_twilio
import json
from datetime import datetime


class CrudOrder:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, obj_in: OrderCreate):
        db_order = Order(**obj_in.dict())
        self.db.add(db_order)
        await self.db.commit()
        await self.db.refresh(db_order)
        return db_order

    async def get_order(self, id: int):
        return await self.db.get(Order, id)

    async def get_orders(self):
        return await self.db.query(Order).all()

    async def update_order(self, id: int, obj_in: OrderUpdate):
        db_order = await self.get_order(id)
        if not db_order:
            raise HTTPException(status_code=404, detail="Order not found")
        update_data = obj_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_order, key, value)
        self.db.add(db_order)
        await self.db.commit()
        await self.db.refresh(db_order)
        return db_order

    async def delete_order(self, id: int):
        db_order = await self.get_order(id)
        if not db_order:
            raise HTTPException(status_code=404, detail="Order not found")
        await self.db.delete(db_order)
        await self.db.commit()
        return db_order

    async def get_orders_by_user(self, user_id: int):
        print("user id", user_id)
        # user_id = 1
        stmt = select(Order).where(Order.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def   get_by_booking_id_and_booking_item_id(self, booking_id: int, booking_item_id: int):
        print("booking item id is ", booking_item_id)
        stmt = select(Order).where(Order.booking_item_id == booking_item_id, Order.booking_id == booking_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()   

    async def get_user_orders_with_details(
        self, 
        user_id: int, 
        booking_id: Optional[int] = None,
        booking_item_id: Optional[int] = None
    ):
        """
        Get detailed orders for a user with booking details, address, and test information.
        Can filter by booking_id and/or booking_item_id if provided.
        """
        # Build the query to join all necessary tables
        stmt = (
            select(Order, Booking, BookingItem, Test, Address)
            .join(Booking, Order.booking_id == Booking.id)
            .join(BookingItem, Order.booking_item_id == BookingItem.id)
            .join(Test, BookingItem.test_id == Test.id)
            .join(Address, Booking.address_id == Address.id)
            .where(Order.user_id == user_id)
        )
        
        # Apply optional filters
        if booking_id is not None:
            stmt = stmt.where(Order.booking_id == booking_id)
        if booking_item_id is not None:
            stmt = stmt.where(Order.booking_item_id == booking_item_id)
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        # Group orders by booking_id
        bookings_dict = {}
        for order, booking, booking_item, test, address in rows:
            if booking.id not in bookings_dict:
                # Format address as a single string
                address_str = f"{address.address_line1}"
                if address.address_line2:
                    address_str += f", {address.address_line2}"
                address_str += f", {address.city}, {address.state} {address.postal_code}, {address.country}"
                
                bookings_dict[booking.id] = {
                    "booking_id": booking.id,
                    "booking_date": booking.booking_date,
                    "booking_address": address_str,
                    "tests": []
                }
            
            # Add test details
            bookings_dict[booking.id]["tests"].append({
                "test_id": test.id,
                "test_name": test.name,
                "booking_item_id": booking_item.id,
                "file_link": order.file_link
            })
        
        return list(bookings_dict.values())