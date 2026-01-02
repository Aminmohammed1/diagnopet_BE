from sqlalchemy import String, DateTime, ForeignKey, Float, Time, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from db.base import Base
from datetime import datetime, time


class ClinicInfo(Base):
    __tablename__ = "clinic_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Only one record in this table
    
    # Contact
    whatsapp_number: Mapped[str] = mapped_column(String(50))
    # with country code, e.g., "+91XXXXXXXXXX"
    
    whatsapp_link: Mapped[str | None] = mapped_column(Text)
    # Generated WhatsApp link
    
    # Location
    clinic_address: Mapped[str] = mapped_column(Text)
    google_maps_link: Mapped[str] = mapped_column(Text)
    
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    
    # Hours
    opening_time: Mapped[time | None] = mapped_column(Time)
    # e.g., "09:00"
    
    closing_time: Mapped[time | None] = mapped_column(Time)
    # e.g., "18:00"
    
    # Updated by admin
    updated_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("staff.id", ondelete="SET NULL"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
