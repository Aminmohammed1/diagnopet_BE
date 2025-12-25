from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Optional
from db.models.otp import OTP
from datetime import datetime, timedelta

async def create_otp(db: AsyncSession, phone: str, otp_code: str, expires_in_minutes: int = 10) -> OTP:
    expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
      
    
    db_obj = OTP(
        phone=phone,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_recent_otps_count(db: AsyncSession, phone: str, hours: int = 6) -> int:
    since = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(
        select(func.count(OTP.id)).filter(
            OTP.phone == phone,
            OTP.created_at >= since
        )
    )
    return result.scalar() or 0

async def verify_otp(db: AsyncSession, phone: str, otp_code: str) -> Optional[OTP]:
    result = await db.execute(
        select(OTP).filter(
            OTP.phone == phone,
            OTP.otp_code == otp_code,
            OTP.is_used == False,
            OTP.expires_at > datetime.utcnow()
        )
    )
    otp_obj = result.scalars().first()
    if otp_obj:
        otp_obj.is_used = True
        db.add(otp_obj)
        await db.commit()
        await db.refresh(otp_obj)
    return otp_obj


def check_phone_number(phone: str) -> tuple[bool, str]:
    phone = phone.strip()
    if not phone.startswith("+91"):
        phone = "+91" + phone
    if len(phone) >= 14:
        return False, phone
    return True, phone
