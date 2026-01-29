from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from fastapi import HTTPException
from db.models.order import Order
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
