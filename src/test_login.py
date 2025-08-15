#!/usr/bin/env python3
"""
Test login API with real user data
"""

import requests
import json

def test_login():
    # Test login with the provided credentials
    login_data = {
        "username": "dl1@gmail.com",
        "password": "SecurePassword123!"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Token: {data.get('data', {}).get('access_token', 'No token')[:50]}...")
            print(f"User: {data.get('data', {}).get('user', {}).get('user_name', 'No user name')}")
            print(f"Email: {data.get('data', {}).get('user', {}).get('email', 'No email')}")
            print(f"Organization: {data.get('data', {}).get('user', {}).get('organization_name', 'No organization')}")
        else:
            print("❌ Login failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
