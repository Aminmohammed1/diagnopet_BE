from sqlalchemy import String, Text, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base
from datetime import datetime


class TestReport(Base):
    __tablename__ = "test_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    booking_item_id: Mapped[int] = mapped_column(
        ForeignKey("booking_items.id", ondelete="CASCADE"),
        unique=True,
        index=True
    )
    pet_id: Mapped[int] = mapped_column(
        ForeignKey("pets.id", ondelete="CASCADE"),
        index=True
    )
    test_id: Mapped[int] = mapped_column(
        ForeignKey("tests.id", ondelete="CASCADE"),
        index=True
    )
    batch_group_id: Mapped[int | None] = mapped_column(
        ForeignKey("test_batch_groups.id", ondelete="SET NULL"),
        index=True
    )
    
    # Report content
    report_file_url: Mapped[str | None] = mapped_column(Text)
    findings: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    # Status options: pending, generated, verified, delivered
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    booking_item: Mapped["BookingItem"] = relationship(back_populates="report")
    pet: Mapped["Pet"] = relationship(back_populates="reports")
    test: Mapped["Test"] = relationship()
    batch_group: Mapped["TestBatchGroup | None"] = relationship(back_populates="reports")
