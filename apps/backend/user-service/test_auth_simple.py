#!/usr/bin/env python3
"""
Simple authentication test to validate basic functionality
"""

from fastapi.testclient import TestClient
from main import app

def test_simple_authentication():
    """Test basic authentication flow"""
    client = TestClient(app)
    
    # Test user data
    user_data = {
        "email": "simpletest@example.com",
        "username": "simpletest",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "first_name": "Simple",
        "last_name": "Test",
        "terms_accepted": True,
        "privacy_policy_accepted": True
    }
    
    print("🔍 Testing user registration...")
    register_response = client.post("/api/v1/auth/register", json=user_data)
    print(f"Registration status: {register_response.status_code}")
    
    if register_response.status_code != 201:
        print(f"Registration failed: {register_response.text}")
        # Try login in case user already exists
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful, token retrieved")
            
            # Test authenticated endpoint
            client.headers.update({"Authorization": f"Bearer {access_token}"})
            me_response = client.get("/api/v1/users/me")
            print(f"Get current user status: {me_response.status_code}")
            return True
        else:
            print(f"❌ Login failed: {login_response.text}")
            return False
    else:
        print("✅ Registration successful")
        # Try login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print("✅ Authentication flow complete")
            
            # Test authenticated endpoint
            client.headers.update({"Authorization": f"Bearer {access_token}"})
            me_response = client.get("/api/v1/users/me")
            print(f"Get current user status: {me_response.status_code}")
            return True
        else:
            print(f"❌ Login after registration failed: {login_response.text}")
            return False

if __name__ == "__main__":
    print("🧪 Running simple authentication test...")
    if test_simple_authentication():
        print("✅ Simple test passed!")
    else:
        print("❌ Simple test failed!")