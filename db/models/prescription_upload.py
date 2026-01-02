from sqlalchemy import String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.base import Base
from datetime import datetime


class PrescriptionUpload(Base):
    __tablename__ = "prescription_uploads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    # File metadata
    file_url: Mapped[str] = mapped_column(Text)
    # Supabase storage URL
    
    file_name: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(100))
    # e.g., "application/pdf", "image/jpeg"
    
    file_size_bytes: Mapped[int] = mapped_column(Integer)
    
    # Upload tracking
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, server_default=func.now())
    verified_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("staff.id", ondelete="SET NULL"))
    verification_notes: Mapped[str | None] = mapped_column(Text)
    
    # Relationships
    booking: Mapped["Booking"] = relationship()
    user: Mapped["User"] = relationship()
    verified_by: Mapped["Staff | None"] = relationship(foreign_keys=[verified_by_admin_id])
