from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base
from datetime import datetime
from typing import List

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    role: Mapped[str] = mapped_column(String(50), default="USER")
    
    # Session tracking
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    addresses: Mapped[List["Address"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    pets: Mapped[List["Pet"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    bookings: Mapped[List["Booking"]] = relationship(back_populates="user", cascade="all, delete-orphan")
