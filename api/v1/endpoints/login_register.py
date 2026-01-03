from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.session import get_db
from schemas.user import User, UserCreate, UserUpdate, UserLogin
from crud import crud_user
from datetime import timedelta
from core.config import settings
from core.security import verify_password, create_access_token
from schemas.token import Token
from schemas.user import UserLogin
from crud import crud_otp
import random
from utils.send_whatsapp_msg import send_message_via_twilio_sms
from schemas.verify_otp import VerifyOtpRequest
from api.deps import get_current_admin_or_staff_user
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from schemas.token import TokenPayload

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud_user.create(db, obj_in=user_in)

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_by_phone(db, phone=user_in.phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/send-otp")
async def send_otp(phone: str, db: AsyncSession = Depends(get_db)):
    if not crud_otp.check_phone_number(phone):
        raise HTTPException(status_code=400, detail="Invalid phone number")

    # Check rate limit: 3 OTPs in 6 hours
    otp_count = await crud_otp.get_recent_otps_count(db, phone=phone, hours=6)
    if otp_count >= 4:
        raise HTTPException(
            status_code=429, 
            detail="Too many OTP requests. Please try again after 6 hours."
        )
    
    # # Original OTP generation and Twilio code (commented out to save credits)
    # otp_code = f"{random.randint(100000, 999999)}"
    # await crud_otp.create_otp(db, phone=phone, otp_code=otp_code, expires_in_minutes=10)
    # try:
    #     send_message_via_twilio_sms(
    #         body=f"Your Diagnopet OTP is {otp_code}. Valid for 10 minutes.",
    #         to=phone
    #     )
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")
    
    # Hardcoded OTP for testing (000000)
    otp_code = "000000"
    await crud_otp.create_otp(db, phone=phone, otp_code=otp_code, expires_in_minutes=10)
    
    return {"message": "OTP sent successfully (test mode: 000000)"}

@router.post("/verify-otp", response_model=Token)
async def verify_otp(payload: VerifyOtpRequest, db: AsyncSession = Depends(get_db)):
    phone = payload.phone
    otp_code = payload.otp_code
    valid, phone = crud_otp.check_phone_number(phone)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid phone number")
    
    otp_obj = await crud_otp.verify_otp(db, phone=phone, otp_code=otp_code)
    if not otp_obj:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    user = await crud_user.get_by_phone(db, phone=phone)
    if not user:
        # If user doesn't exist, create a new one
        # Note: We might need more info for UserCreate, but for now let's use defaults
        # or just create a minimal user.
        user_in = UserCreate(
            phone=phone,
            email=f"{phone}@diagnopet.com", # Placeholder email
            password=str(random.randint(100000, 999999)), # Placeholder password
            full_name="New User",
            is_verified=True
        )
        user = await crud_user.create(db, obj_in=user_in)
    
    # Mark user as verified if not already
    if not user.is_verified:
        user.is_verified = True
        db.add(user)
        await db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/validate-token")
async def validate_token(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate JWT token and check if user has admin or staff role.
    Returns user info if valid and has required role.
    """
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired token",
        )
    
    # Get user from database
    user = await crud_user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Check if user has admin or staff role
    if user.role not in ["ADMIN", "STAFF"] and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User doesn't have admin or staff privileges",
        )
    
    return {
        "valid": True,
        "user_id": user.id,
        "role": user.role,
        "is_superuser": user.is_superuser,
        "full_name": user.full_name,
        "email": user.email
    }