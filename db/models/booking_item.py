from sqlalchemy import ForeignKey, Integer, Float, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class BookingItem(Base):
    __tablename__ = "booking_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), index=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete="CASCADE"), index=True)

    # New fields
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    # Status options: pending, collected, processing, completed

    # Relationships
    booking: Mapped["Booking"] = relationship(back_populates="items")
    test: Mapped["Test"] = relationship()
    report: Mapped["TestReport | None"] = relationship(back_populates="booking_item", uselist=False)
