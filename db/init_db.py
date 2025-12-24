from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.config import settings
from crud import crud_user
from schemas.user import UserCreate
from db.models.user import User
from core.security import get_password_hash

async def init_db(db: AsyncSession) -> None:
    if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        print(f"Initializing Admin: {settings.ADMIN_EMAIL}")
        
        # 1. Check if user with .env EMAIL exists
        user = await crud_user.get_by_email(db, email=settings.ADMIN_EMAIL)
        
        # 2. If not, check if user with .env PHONE exists
        if not user and settings.ADMIN_PHONE:
            user = await crud_user.get_by_phone(db, phone=settings.ADMIN_PHONE)
            
        # 3. If still not found, check if ANY admin exists (to replace)
        if not user:
            result = await db.execute(select(User).filter(User.role == "ADMIN"))
            user = result.scalars().first()
            if user:
                print(f"Found existing admin to replace: {user.email}")

        if not user:
            print("Creating new admin user...")
            user_in = UserCreate(
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                full_name=settings.ADMIN_NAME,
                phone=settings.ADMIN_PHONE or "0000000000",
                is_superuser=True,
                is_active=True,
                is_verified=True,
                role="ADMIN",
            )
            await crud_user.create(db, obj_in=user_in)
        else:
            print(f"Updating existing user {user.email} to Admin...")
            # Update details to match .env
            user.email = settings.ADMIN_EMAIL
            if settings.ADMIN_PHONE:
                user.phone = settings.ADMIN_PHONE
            user.hashed_password = get_password_hash(settings.ADMIN_PASSWORD)
            user.full_name = settings.ADMIN_NAME
            user.role = "ADMIN"
            user.is_superuser = True
            user.is_active = True
            user.is_verified = True
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print("Admin user updated successfully.")
