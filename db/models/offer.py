from sqlalchemy import String, Float, Text, Date, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base
from datetime import date, datetime
from typing import List


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    
    discount_type: Mapped[str] = mapped_column(String(50))
    # enum: percentage, fixed_amount
    discount_value: Mapped[float] = mapped_column(Float)
    
    # Validity
    start_date: Mapped[date] = mapped_column(Date, index=True)
    end_date: Mapped[date] = mapped_column(Date, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Targeting
    event_tag: Mapped[str | None] = mapped_column(String(100))
    # e.g., "Christmas", "New Year", "Health Month"
    
    applicable_tests: Mapped[str | None] = mapped_column(Text)
    # JSON format: ["test_id_1", "test_id_2"] or "all"
    
    minimum_order_value: Mapped[float | None] = mapped_column(Float)
    
    # Tracking
    created_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("staff.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    coupons: Mapped[List["Coupon"]] = relationship(back_populates="offer", cascade="all, delete-orphan")
