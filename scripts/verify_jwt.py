import requests
from jose import jwt

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1"
SECRET_KEY = "YOUR_SECRET_KEY_HERE_PLEASE_CHANGE_IN_PRODUCTION"
ALGORITHM = "HS256"

def verify_login():
    # 1. Login
    login_data = {
        "phone": "1234567890", # Ensure this matches .env ADMIN_PHONE if used, or update logic
        "password": "pass123456",
        "email": "your_admin@email.com", 
        "full_name": "Admin User" 
    }
    
    login_payload = {
        "phone": "1234567890", # Assuming this is the phone from .env or init_db
        "password": "pass123456"
    }

    print(f"Logging in with: {login_payload}")
    response = requests.post(f"{API_URL}/auth/login", json=login_payload)
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.text}")
        return

    token_data = response.json()
    print(f"Login successful! Token data: {token_data}")

    access_token = token_data.get("access_token")
    if not access_token:
        print("No access token found!")
        return

    # 2. Decode Token
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded Token Payload: {payload}")
        
        # The API returns the user ID in the 'sub' claim, not the phone number.
        if payload.get("sub").isdigit():
            print(f"Verification SUCCESS: Subject is a user ID ({payload.get('sub')}).")
        else:
            print(f"Verification FAILED: Subject mismatch. Expected user ID, got '{payload.get('sub')}'")

    except Exception as e:
        print(f"Token decoding failed: {e}")

if __name__ == "__main__":
    verify_login()
