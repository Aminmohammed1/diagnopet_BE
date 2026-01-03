from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base
from datetime import datetime
from typing import List


class Staff(Base):
    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    name: Mapped[str] = mapped_column(String(255), index=True)
    phone: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    
    # Role and permissions
    role: Mapped[str] = mapped_column(String(50), index=True)
    # Role options: admin, collector, lab_tech, analyst
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Location
    assigned_area: Mapped[str | None] = mapped_column(String(255))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    collections: Mapped[List["Booking"]] = relationship(
        back_populates="collection_staff",
        foreign_keys="Booking.collection_staff_id"
    )
