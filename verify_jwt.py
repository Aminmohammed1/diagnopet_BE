import requests
from jose import jwt

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1"
SECRET_KEY = "YOUR_SECRET_KEY_HERE_PLEASE_CHANGE_IN_PRODUCTION"
ALGORITHM = "HS256"

def verify_login():
    # 1. Login
    login_data = {
        "phone": "1234567890",
        "password": "admin123",
        "email": "admin@example.com", # Not used for login but required by schema if not optional, checking schema...
        "full_name": "Admin" # Same here
    }
    # Actually UserLogin only needs phone and password based on my edit?
    # Let's check schema again. UserLogin inherits from UserBase.
    # UserBase has email, phone, full_name as optional.
    # So phone and password should be enough if I defined UserLogin correctly.
    
    login_payload = {
        "phone": "1234567890",
        "password": "admin123"
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
        
        if payload.get("sub") == "admin@example.com":
            print("Verification SUCCESS: Subject matches admin email.")
        else:
            print(f"Verification FAILED: Subject mismatch. Expected 'admin@example.com', got '{payload.get('sub')}'")

    except Exception as e:
        print(f"Token decoding failed: {e}")

if __name__ == "__main__":
    verify_login()
