from sqlalchemy import String, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base
from datetime import datetime


class CouponRedemption(Base):
    __tablename__ = "coupon_redemptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    coupon_id: Mapped[int] = mapped_column(
        ForeignKey("coupons.id", ondelete="CASCADE"),
        index=True
    )
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    discount_amount: Mapped[float] = mapped_column(Float)
    redemption_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, server_default=func.now())
    
    # Relationships
    coupon: Mapped["Coupon"] = relationship(back_populates="redemptions")
    booking: Mapped["Booking"] = relationship()
    user: Mapped["User"] = relationship()
