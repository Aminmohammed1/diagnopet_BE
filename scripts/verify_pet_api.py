import httpx
import asyncio
import random
import string

BASE_URL = "http://localhost:8000/api/v1"

async def verify_pet_api():
    async with httpx.AsyncClient() as client:
        try:
            # 1. Create a test user
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            phone = f"+9188888{random.randint(10000, 99999)}"
            email = f"api_test_{random_suffix}@example.com"
            user_data = {
                "email": email,
                "phone": phone,
                "password": "testpassword",
                "full_name": "API Test User"
            }
            response = await client.post(f"{BASE_URL}/users/", json=user_data)
            if response.status_code != 200:
                print(f"✗ Failed to create user: {response.text}")
                return
            user = response.json()
            user_id = user["id"]
            print(f"✓ Created test user: {user['email']} (ID: {user_id})")

            # 2. Create a pet for the user
            pet_data = {
                "user_id": user_id,
                "name": "Max",
                "species": "Cat",
                "breed": "Siamese",
                "age_years": 2.0,
                "weight_kg": 4.5,
                "medical_history": "None",
                "is_active": True
            }
            response = await client.post(f"{BASE_URL}/pets/", json=pet_data)
            if response.status_code != 200:
                print(f"✗ Failed to create pet: {response.text}")
                return
            pet = response.json()
            pet_id = pet["id"]
            print(f"✓ Created pet: {pet['name']} (ID: {pet_id})")

            # 3. Get the pet
            response = await client.get(f"{BASE_URL}/pets/{pet_id}")
            assert response.status_code == 200
            assert response.json()["name"] == "Max"
            print(f"✓ Fetched pet: {response.json()['name']}")

            # 4. List pets for user
            response = await client.get(f"{BASE_URL}/pets/", params={"user_id": user_id})
            assert response.status_code == 200
            pets = response.json()
            assert len(pets) >= 1
            print(f"✓ Listed {len(pets)} pets for user {user_id}")

            # 5. Get user with pets
            response = await client.get(f"{BASE_URL}/users/{user_id}")
            assert response.status_code == 200
            user_with_pets = response.json()
            assert "pets" in user_with_pets
            assert any(p["id"] == pet_id for p in user_with_pets["pets"])
            print(f"✓ Verified pet {pet_id} appears in user {user_id} response")

            # 6. Update the pet
            update_data = {"name": "Max Updated", "weight_kg": 5.0}
            response = await client.put(f"{BASE_URL}/pets/{pet_id}", json=update_data)
            assert response.status_code == 200
            assert response.json()["name"] == "Max Updated"
            print(f"✓ Updated pet: {response.json()['name']}")

            # 7. Delete the pet
            response = await client.delete(f"{BASE_URL}/pets/{pet_id}")
            assert response.status_code == 200
            print(f"✓ Deleted pet: {pet_id}")

            # 8. Verify deletion
            response = await client.get(f"{BASE_URL}/pets/{pet_id}")
            assert response.status_code == 404
            print("✓ Verified pet deletion via API")

            # Clean up user
            response = await client.delete(f"{BASE_URL}/users/{user_id}")
            assert response.status_code == 200
            print(f"✓ Cleaned up test user: {user_id}")

        except Exception as e:
            print(f"✗ Error during API verification: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_pet_api())
