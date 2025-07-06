#!/usr/bin/env python3
"""
Test script for Render.com deployed webhook endpoint
"""
import requests
import json
import sys

def test_render_endpoint(base_url="https://pokemon-webhook.onrender.com"):
    """Test the deployed Render.com webhook endpoint"""
    
    print(f"🚀 Testing Render endpoint: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Root endpoint
    print("\n2️⃣ Testing root endpoint...")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            print("✅ Root endpoint passed")
        else:
            print("❌ Root endpoint failed")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: eBay challenge response
    print("\n3️⃣ Testing eBay challenge response...")
    test_challenge = "test_challenge_12345"
    try:
        response = requests.get(
            f"{base_url}/ebay/marketplace_account_deletion",
            params={"challenge_code": test_challenge},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("challengeResponse") == test_challenge:
                print("✅ eBay challenge response passed")
            else:
                print("❌ eBay challenge response incorrect")
        else:
            print("❌ eBay challenge response failed")
    except Exception as e:
        print(f"❌ eBay challenge error: {e}")
    
    # Test 4: eBay POST webhook
    print("\n4️⃣ Testing eBay POST webhook...")
    test_payload = {
        "metadata": {
            "topic": "MARKETPLACE_ACCOUNT_DELETION",
            "schemaVersion": "1.0",
            "deprecated": False
        },
        "notification": {
            "notificationId": "test-notification-123",
            "eventDate": "2024-01-06T10:00:00.000Z",
            "publishedDate": "2024-01-06T10:00:00.000Z",
            "data": {
                "username": "test_user",
                "userId": "test_user_id",
                "eiasToken": "test_token"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/ebay/marketplace_account_deletion",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            print("✅ eBay POST webhook passed")
        else:
            print("❌ eBay POST webhook failed")
    except Exception as e:
        print(f"❌ eBay POST webhook error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed! If all tests pass, your endpoint is eBay-ready!")

if __name__ == "__main__":
    # Allow custom URL via command line
    url = sys.argv[1] if len(sys.argv) > 1 else "https://pokemon-webhook.onrender.com"
    test_render_endpoint(url)
