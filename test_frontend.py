#!/usr/bin/env python3
"""
Simple test script to verify the frontend setup
"""

import requests
import json
import time

def test_api_endpoint():
    """Test the API endpoint with a simple request"""
    url = "http://localhost:8000/api/scan/scan"
    
    # Test data
    test_data = {
        "domain": "example.com",
        "scans": ["subdomain"]
    }
    
    try:
        print("Testing API endpoint...")
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            print("✅ API endpoint is working!")
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            return True
        else:
            print(f"❌ API endpoint returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running.")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out.")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_frontend_files():
    """Test if frontend files exist"""
    import os
    
    files_to_check = [
        "templates/index.html",
        "static/style.css", 
        "static/script.js",
        "config.yaml"
    ]
    
    print("\nChecking frontend files...")
    all_exist = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing!")
            all_exist = False
    
    return all_exist

def main():
    print("🚀 Attack Surface Discovery Scanner - Frontend Test")
    print("=" * 50)
    
    # Test frontend files
    files_ok = test_frontend_files()
    
    if not files_ok:
        print("\n❌ Frontend files are missing. Please check the setup.")
        return
    
    print("\n✅ All frontend files are present!")
    
    # Test API endpoint
    api_ok = test_api_endpoint()
    
    if api_ok:
        print("\n🎉 Frontend setup is complete and working!")
        print("\nTo start the application:")
        print("1. Run: uvicorn api_main:app --host 0.0.0.0 --port 8000 --reload")
        print("2. Open: http://localhost:8000")
    else:
        print("\n⚠️  API test failed. Make sure the server is running.")

if __name__ == "__main__":
    main()