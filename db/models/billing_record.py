from sqlalchemy import String, DateTime, ForeignKey, Float, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base
from datetime import date, datetime


class BillingRecord(Base):
    __tablename__ = "billing_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    # Test & pricing
    test_ids: Mapped[str | None] = mapped_column(Text)
    # JSON format: list of test IDs
    
    base_amount: Mapped[float] = mapped_column(Float)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0)
    distance_charge: Mapped[float] = mapped_column(Float, default=0.0)
    final_amount: Mapped[float] = mapped_column(Float)
    
    # Billing period
    billing_date: Mapped[date] = mapped_column(Date, index=True)
    billing_period: Mapped[str] = mapped_column(String(10))
    # Format: "YYYY-MM" for month, "YYYY-MM-DD" for day
    
    # Status
    status: Mapped[str] = mapped_column(String(50), index=True)
    # enum: draft, finalized, invoiced, paid
    
    invoice_number: Mapped[str | None] = mapped_column(String(100), unique=True)
    invoice_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paid_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    booking: Mapped["Booking"] = relationship()
    user: Mapped["User"] = relationship()
