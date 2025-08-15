#!/usr/bin/env python3
"""
Test registration and login flow
"""

import requests
import json

def test_register_and_login():
    # Test user data
    test_user = {
        "user_name": "Test User",
        "email": "test@test.com",
        "password": "TestPassword123",
        "organization_name": "Test Organization",
        "contact_phone": "+1234567890"
    }
    
    print("1. Testing Registration...")
    try:
        # Register the user
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Registration Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Registration successful!")
        else:
            print(f"❌ Registration failed: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    print("\n2. Testing Login...")
    try:
        # Login with the same credentials
        login_data = {
            "username": test_user["email"],
            "password": test_user["password"]
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Token: {data.get('data', {}).get('access_token', 'No token')[:50]}...")
            print(f"User: {data.get('data', {}).get('user', {}).get('user_name', 'No user name')}")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Login error: {e}")

if __name__ == "__main__":
    test_register_and_login()
