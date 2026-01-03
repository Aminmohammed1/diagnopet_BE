from sqlalchemy import String, Text, ForeignKey, Boolean, Numeric, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base
from datetime import datetime

class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(primary_key=True)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("test_categories.id", ondelete="CASCADE"),
        index=True
    )

    name: Mapped[str] = mapped_column(String(150), index=True)
    description: Mapped[str | None] = mapped_column(Text)

    price: Mapped[float] = mapped_column(Numeric(10, 2))
    discounted_price: Mapped[float | None] = mapped_column(Numeric(10, 2))

    sample_type: Mapped[str | None] = mapped_column(String(50))
    report_time_hours: Mapped[int | None]
    
    # New fields for test information
    tube_type: Mapped[str | None] = mapped_column(String(100))
    sample_quantity_ml: Mapped[float | None] = mapped_column(Numeric(5, 2))
    sample_collection_instructions: Mapped[str | None] = mapped_column(Text)
    tat_hours: Mapped[int | None]  # Turnaround time alias

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    category: Mapped["TestCategory"] = relationship(back_populates="tests")
