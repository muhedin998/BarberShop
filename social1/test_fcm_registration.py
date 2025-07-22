#!/usr/bin/env python3
"""
FCM Token Registration Test Script
Run this to test the full FCM token registration flow
"""

import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social1.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from appointment.models import FCMToken

User = get_user_model()

def test_token_registration():
    print("=== FCM Token Registration Test ===\n")
    
    # 1. Check current tokens
    print("1. Current FCM tokens in database:")
    tokens = FCMToken.objects.all()
    for token in tokens:
        print(f"   - User: {token.user.username}, Device: {token.device_id}, Active: {token.is_active}")
    print(f"   Total: {tokens.count()} tokens\n")
    
    # 2. Test authentication requirement
    print("2. Testing authentication requirement...")
    client = Client()
    
    # Try without authentication
    test_data = {
        'token': 'test-token-12345',
        'device_id': 'test-device'
    }
    
    response = client.post('/fcm/register-token/', 
                          data=json.dumps(test_data),
                          content_type='application/json')
    print(f"   Without auth: {response.status_code} - {response.reason_phrase}")
    
    # 3. Test with authentication
    print("\n3. Testing with authentication...")
    
    # Get first user
    users = User.objects.all()[:3]
    if not users:
        print("   ERROR: No users found in database!")
        return
    
    for user in users:
        print(f"\n   Testing with user: {user.username}")
        
        # Login
        client.force_login(user)
        
        # Try to register token
        test_data = {
            'token': f'test-token-{user.username}-{len(str(user.id))*10}',
            'device_id': f'test-device-{user.username}'
        }
        
        response = client.post('/fcm/register-token/',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Success: {response.json()}")
        else:
            print(f"   Error: {response.content.decode()}")
    
    # 4. Check tokens after test
    print("\n4. FCM tokens after test:")
    tokens = FCMToken.objects.all().order_by('-created_at')
    for token in tokens[:5]:  # Show last 5
        print(f"   - User: {token.user.username}, Device: {token.device_id}, Active: {token.is_active}, Created: {token.created_at}")

def test_csrf_token_endpoint():
    print("\n=== CSRF Token Test ===")
    
    client = Client()
    
    # Test getting CSRF token
    response = client.get('/')
    if 'csrftoken' in client.cookies:
        csrf_token = client.cookies['csrftoken'].value
        print(f"CSRF token available: {csrf_token[:10]}...")
    else:
        print("CSRF token NOT found in cookies")
    
    # Test token status endpoint
    response = client.get('/fcm/token-status/')
    print(f"Token status endpoint (no auth): {response.status_code}")

def test_javascript_token_flow():
    print("\n=== JavaScript Token Flow Test ===")
    print("To test in browser console:")
    print("""
// 1. Check if user is authenticated
console.log('User authenticated:', document.body.innerHTML.includes('logout') || document.body.innerHTML.includes('Logout'));

// 2. Check CSRF token
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return null;
}
console.log('CSRF token:', getCSRFToken());

// 3. Test token registration
async function testTokenRegistration() {
    const testToken = 'test-browser-token-' + Date.now();
    const deviceId = 'test-browser-device';
    
    try {
        const response = await fetch('/fcm/register-token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                token: testToken,
                device_id: deviceId
            })
        });
        
        console.log('Registration response:', response.status);
        const data = await response.json();
        console.log('Response data:', data);
    } catch (error) {
        console.error('Registration error:', error);
    }
}

// Run the test
testTokenRegistration();
    """)

if __name__ == '__main__':
    test_token_registration()
    test_csrf_token_endpoint() 
    test_javascript_token_flow()