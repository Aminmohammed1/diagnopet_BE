from sqlalchemy import String, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base
from datetime import datetime
from typing import List


class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    offer_id: Mapped[int | None] = mapped_column(
        ForeignKey("offers.id", ondelete="CASCADE"),
        index=True
    )
    
    # Validity
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Usage limits
    max_uses: Mapped[int | None]  # None = unlimited
    current_uses: Mapped[int] = mapped_column(Integer, default=0)
    max_uses_per_user: Mapped[int] = mapped_column(Integer, default=1)
    
    # Tracking
    created_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("staff.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    offer: Mapped["Offer | None"] = relationship(back_populates="coupons")
    redemptions: Mapped[List["CouponRedemption"]] = relationship(back_populates="coupon", cascade="all, delete-orphan")
