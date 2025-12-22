from sqlalchemy import String, Text, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

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

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    category: Mapped["TestCategory"] = relationship(back_populates="tests")
