from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class TestCategory(Base):
    __tablename__ = "test_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tests: Mapped[list["Test"]] = relationship(
        back_populates="category",
        cascade="all, delete"
    )
