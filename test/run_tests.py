#!/usr/bin/env python3
"""
Test runner for JWT Authentication Bypass Lab
Automatically runs tests and demonstrates the exploit
"""

import subprocess
import sys
import time
import requests
from test_jwt_vulnerability import run_exploit_demo

def wait_for_app(url="http://localhost:3206", timeout=60):
    """Wait for the application to be ready"""
    print(f"⏳ Waiting for application at {url}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print("✅ Application is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(2)
    
    print("❌ Application failed to start within timeout")
    return False

def run_pytest():
    """Run pytest tests"""
    print("🧪 Running pytest tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_jwt_vulnerability.py", 
            "-v", "--tb=short"
        ], cwd="test", capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main test runner"""
    print("🚀 JWT Authentication Bypass Lab - Test Runner")
    print("=" * 50)
    
    # Wait for application to be ready
    if not wait_for_app():
        print("❌ Cannot proceed without running application")
        print("Please start the application with: docker-compose -f deploy/docker-compose.yaml up --build")
        sys.exit(1)
    
    # Run pytest tests
    print("\n" + "=" * 50)
    if not run_pytest():
        print("❌ Tests failed")
        sys.exit(1)
    
    # Run exploit demo
    print("\n" + "=" * 50)
    print("🎯 Running exploit demonstration...")
    if not run_exploit_demo():
        print("❌ Exploit demonstration failed")
        sys.exit(1)
    
    print("\n🎉 All tests and exploits completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main() 