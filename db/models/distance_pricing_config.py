from sqlalchemy import Float, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from db.base import Base
from datetime import date, datetime


class DistancePricingConfig(Base):
    __tablename__ = "distance_pricing_configs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Pricing structure
    base_charge: Mapped[float] = mapped_column(Float)
    charge_per_km: Mapped[float] = mapped_column(Float)
    max_free_distance_km: Mapped[float] = mapped_column(Float)
    
    # Validity
    effective_from: Mapped[date] = mapped_column(Date, index=True)
    effective_until: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Tracking
    updated_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("staff.id", ondelete="SET NULL"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
