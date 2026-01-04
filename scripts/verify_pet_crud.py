import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings
from db.models.user import User
from db.models.pet import Pet
from crud import crud_user, crud_pet
from schemas.user import UserCreate
from schemas.pet import PetCreate, PetUpdate
import random
import string

async def verify_pet_crud():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with AsyncSessionLocal() as db:
        try:
            # 1. Create a test user
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            phone = f"+9199999{random.randint(10000, 99999)}"
            email = f"test_user_{random_suffix}@example.com"
            user_in = UserCreate(
                email=email,
                phone=phone,
                password="testpassword",
                full_name="Test User for Pet CRUD"
            )
            user = await crud_user.create(db, obj_in=user_in)
            print(f"✓ Created test user: {user.email} (ID: {user.id})")

            # 2. Create a pet for the user
            pet_in = PetCreate(
                user_id=user.id,
                name="Buddy",
                species="Dog",
                breed="Golden Retriever",
                age_years=3.5,
                weight_kg=25.0,
                medical_history="Healthy"
            )
            pet = await crud_pet.create(db, obj_in=pet_in)
            print(f"✓ Created pet: {pet.name} (ID: {pet.id})")

            # 3. Get the pet
            fetched_pet = await crud_pet.get(db, id=pet.id)
            assert fetched_pet.name == "Buddy"
            print(f"✓ Fetched pet: {fetched_pet.name}")

            # 4. Get multi pets by owner
            pets = await crud_pet.get_multi_by_owner(db, user_id=user.id)
            assert len(pets) >= 1
            print(f"✓ Fetched {len(pets)} pets for user {user.id}")

            # 5. Update the pet
            pet_update = PetUpdate(name="Buddy Updated", weight_kg=26.0)
            updated_pet = await crud_pet.update(db, db_obj=pet, obj_in=pet_update)
            assert updated_pet.name == "Buddy Updated"
            assert updated_pet.weight_kg == 26.0
            print(f"✓ Updated pet: {updated_pet.name}")

            # 6. Delete the pet
            deleted_pet = await crud_pet.delete(db, id=pet.id)
            assert deleted_pet.id == pet.id
            print(f"✓ Deleted pet: {deleted_pet.id}")

            # 7. Verify deletion
            refetched_pet = await crud_pet.get(db, id=pet.id)
            assert refetched_pet is None
            print("✓ Verified pet deletion")

            # Clean up user
            await crud_user.delete(db, id=user.id)
            print(f"✓ Cleaned up test user: {user.id}")

        except Exception as e:
            print(f"✗ Error during verification: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_pet_crud())
