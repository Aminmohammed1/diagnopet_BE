import requests
import random
import string

# Configuration
API_URL = "http://127.0.0.1:8001/api/v1"

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def register_user(role="USER"):
    email = f"{generate_random_string()}@example.com"
    phone = "".join(random.choices(string.digits, k=10))
    password = "password123"
    
    user_data = {
        "email": email,
        "phone": phone,
        "password": password,
        "full_name": f"Test {role}",
        "role": role # Note: Register endpoint might ignore role, defaulting to USER
    }
    
    print(f"Registering user: {email}")
    response = requests.post(f"{API_URL}/auth/register", json=user_data)
    if response.status_code != 200:
        print(f"Registration failed: {response.text}")
        return None
    
    return {"phone": phone, "password": password}

def login(credentials):
    print(f"Logging in with: {credentials['phone']}")
    response = requests.post(f"{API_URL}/auth/login", json=credentials)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return None
    return response.json().get("access_token")

def upload_report(token):
    headers = {"Authorization": f"Bearer {token}"}
    files = {'file': ('test.pdf', b'%PDF-1.4 empty pdf content', 'application/pdf')}
    data = {
        "user_id": 1,
        "appointment_id": 1,
        "phone_number": "1234567890"
    }
    
    print("Attempting to upload report...")
    response = requests.post(f"{API_URL}/reports/upload-report", headers=headers, files=files, data=data)
    return response

def verify():
    # 1. Test Normal User
    print("\n--- Testing Normal User ---")
    user_creds = register_user()
    if user_creds:
        token = login(user_creds)
        if token:
            response = upload_report(token)
            print(f"Response Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            
            if response.status_code == 400 and "privileges" in response.text:
                print("SUCCESS: Normal user denied access.")
            else:
                print("FAILURE: Normal user should be denied.")

    # 2. Test Admin User
    print("\n--- Testing Admin User ---")
    # Using credentials from verify_jwt.py / init_db assumption
    admin_creds = {
        "phone": "1234567890", 
        "password": "pass123456"
    }
    token = login(admin_creds)
    if token:
        response = upload_report(token)
        print(f"Response Code: {response.status_code}")
        # Note: It might fail due to other reasons (Supabase config, etc), but if it passes Auth, it shouldn't be the privilege error.
        if response.status_code != 400 or "privileges" not in response.text:
             print("SUCCESS: Admin user passed auth check (even if upload failed).")
        else:
             print(f"FAILURE: Admin user denied access. {response.text}")

if __name__ == "__main__":
    verify()
