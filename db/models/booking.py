from sqlalchemy import ForeignKey, DateTime, String, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base
from datetime import datetime
from typing import List

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id", ondelete="CASCADE"), index=True)
    collection_staff_id: Mapped[int | None] = mapped_column(ForeignKey("staff.id", ondelete="SET NULL"))
    
    booking_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    address: Mapped[str] = mapped_column(String(255))
    address_link: Mapped[str] = mapped_column(String(255))
    
    # New fields
    notes: Mapped[str | None] = mapped_column(Text)
    estimated_distance_km: Mapped[float | None]
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship(back_populates="bookings")
    pet: Mapped["Pet"] = relationship(back_populates="bookings")
    collection_staff: Mapped["Staff | None"] = relationship(foreign_keys=[collection_staff_id])
    items: Mapped[List["BookingItem"]] = relationship(back_populates="booking", cascade="all, delete-orphan")
    batch_groups: Mapped[List["TestBatchGroup"]] = relationship(back_populates="booking", cascade="all, delete-orphan")
