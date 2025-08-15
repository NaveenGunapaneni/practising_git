#!/usr/bin/env python3
"""
Test login API with detailed response analysis
"""

import requests
import json

def test_login_detailed():
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
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print("\n=== FULL RESPONSE STRUCTURE ===")
            print(json.dumps(data, indent=2))
            
            print("\n=== KEY FIELDS ===")
            print(f"Status: {data.get('status', 'No status')}")
            print(f"Message: {data.get('message', 'No message')}")
            
            # Check data structure
            data_section = data.get('data', {})
            print(f"Has 'data' section: {bool(data_section)}")
            
            if data_section:
                print(f"Access Token: {data_section.get('access_token', 'No token')[:50]}...")
                print(f"Token Type: {data_section.get('token_type', 'No type')}")
                print(f"Expires In: {data_section.get('expires_in', 'No expiry')}")
                
                # Check user data
                user_section = data_section.get('user', {})
                print(f"Has 'user' section: {bool(user_section)}")
                if user_section:
                    print(f"User ID: {user_section.get('user_id', 'No ID')}")
                    print(f"User Name: {user_section.get('user_name', 'No name')}")
                    print(f"Email: {user_section.get('email', 'No email')}")
                    print(f"Organization: {user_section.get('organization_name', 'No org')}")
        else:
            print("❌ Login failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login_detailed()
