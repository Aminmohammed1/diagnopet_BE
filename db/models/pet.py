from sqlalchemy import String, Float, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base
from datetime import datetime
from typing import List


class Pet(Base):
    __tablename__ = "pets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    name: Mapped[str] = mapped_column(String(255), index=True)
    species: Mapped[str] = mapped_column(String(100))  # e.g., "Dog", "Cat", "Bird"
    breed: Mapped[str | None] = mapped_column(String(100))
    age_years: Mapped[float | None]
    weight_kg: Mapped[float | None]
    
    medical_history: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="pets")
    bookings: Mapped[List["Booking"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    reports: Mapped[List["TestReport"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
