import httpx
import asyncio
import random
import string

async def debug_user_creation():
    async with httpx.AsyncClient() as client:
        try:
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            user_data = {
                "email": f"debug_{random_suffix}@example.com",
                "phone": f"+9177777{random.randint(10000, 99999)}",
                "password": "password",
                "full_name": "Debug User"
            }
            response = await client.post("http://localhost:8000/api/v1/users/", json=user_data)
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_user_creation())
