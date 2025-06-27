#!/usr/bin/env python3
"""
Simple script to test FCM token registration
Run this after fixing browser permissions
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
USERNAME = "muhedin89"  # Change this to your username
PASSWORD = "your_password"  # Change this to your password

def login_and_get_csrf():
    """Login and get CSRF token"""
    session = requests.Session()
    
    # Get login page to get CSRF token
    login_url = f"{BASE_URL}/user_login/"
    response = session.get(login_url)
    
    # Extract CSRF token from cookies
    csrf_token = session.cookies.get('csrftoken')
    
    # Login
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf_token
    }
    
    response = session.post(login_url, data=login_data)
    
    if response.status_code == 200:
        print("✅ Login successful")
        return session, csrf_token
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None, None

def test_fcm_registration(session, csrf_token):
    """Test FCM token registration"""
    # Test FCM token (this is a dummy token)
    test_token = "dummy_fcm_token_for_testing_12345678901234567890"
    
    fcm_url = f"{BASE_URL}/fcm/register-token/"
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,
        'Referer': BASE_URL
    }
    
    data = {
        'token': test_token,
        'device_id': 'test-browser-device'
    }
    
    response = session.post(fcm_url, json=data, headers=headers)
    
    print(f"FCM Registration Response: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 200:
        print("✅ FCM token registration successful")
        return True
    else:
        print("❌ FCM token registration failed")
        return False

if __name__ == "__main__":
    print("Testing FCM token registration...")
    print("Make sure Django server is running on http://127.0.0.1:8000")
    print(f"Testing with user: {USERNAME}")
    print("-" * 50)
    
    session, csrf_token = login_and_get_csrf()
    
    if session and csrf_token:
        test_fcm_registration(session, csrf_token)
    else:
        print("Cannot proceed without valid session")
    
    print("\nNote: This is a test with a dummy token.")
    print("For real FCM tokens, you need to enable notifications in the browser.")