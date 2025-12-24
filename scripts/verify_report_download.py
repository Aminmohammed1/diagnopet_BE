import requests
import sys
import random
import string

BASE_URL = "http://127.0.0.1:8001/api/v1"

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def register_user():
    email = f"{generate_random_string()}@example.com"
    phone = "".join(random.choices(string.digits, k=10))
    password = "password123"
    
    user_data = {
        "email": email,
        "phone": phone,
        "password": password,
        "full_name": "Test User",
        "role": "USER"
    }
    
    print(f"Registering user: {email}")
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if response.status_code != 200:
        print(f"Registration failed: {response.text}")
        return None
    
    return {"phone": phone, "password": password, "email": email}

def login(credentials):
    print(f"Logging in with: {credentials['phone']}")
    # The auth endpoint expects username/password form data or json depending on implementation.
    # verify_report_auth.py used json.
    response = requests.post(f"{BASE_URL}/auth/login", json=credentials)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return None
    return response.json().get("access_token")

def get_reports(token):
    url = f"{BASE_URL}/reports/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def main():
    print("--- Verifying Report Download API ---")
    
    # 1. Register and Login as a standard user
    # user_creds = register_user()
    user_creds = {"phone": "string", "password": "string", "email": "user@example.com"}
    if not user_creds:
        return

    token = login(user_creds)
    if not token:
        return

    # 2. Get Reports (Should be empty initially)
    response = get_reports(token)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        reports = response.json()
        if isinstance(reports, list):
            print("SUCCESS: Retrieved reports list.")
        else:
            print("FAILURE: Response is not a list.")
    else:
        print("FAILURE: Could not retrieve reports.")

    # Note: To verify actual files, we would need to upload one first.
    # However, uploading requires ADMIN/STAFF privileges as per previous task.
    # So a normal user cannot upload their own report to test this fully end-to-end 
    # without admin intervention.
    # For now, verifying that the endpoint returns 200 and an empty list is a good start.

if __name__ == "__main__":
    main()
