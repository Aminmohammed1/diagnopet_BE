from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base

class TestTag(Base):
    __tablename__ = "test_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    test_id: Mapped[int] = mapped_column(
        ForeignKey("tests.id", ondelete="CASCADE"),
        index=True
    )
    tag: Mapped[str] = mapped_column(String(50), index=True)
