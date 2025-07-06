#!/usr/bin/env python3
"""
Test Railway webhook endpoint for eBay compliance
"""
import requests
import json
from datetime import datetime

def test_railway_endpoint():
    """Test the Railway deployed webhook endpoint"""
    
    # Railway URL (update this with your actual Railway domain)
    base_url = "https://web-production-dc94.up.railway.app"
    
    print("🧪 TESTING RAILWAY WEBHOOK ENDPOINT")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print()
    
    # Test 1: Health check
    print("1. Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
            print("   ✅ Health check passed!")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    print()
    
    # Test 2: eBay challenge verification
    print("2. Testing eBay challenge verification...")
    challenge_token = "test_challenge_12345"
    try:
        response = requests.get(
            f"{base_url}/ebay/marketplace_account_deletion",
            params={"challenge_code": challenge_token},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            print(f"   Response: {response_data}")
            if response_data.get("challengeResponse") == challenge_token:
                print("   ✅ Challenge verification passed!")
            else:
                print("   ❌ Challenge response doesn't match")
        else:
            print(f"   ❌ Challenge verification failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Challenge verification error: {e}")
    
    print()
    
    # Test 3: POST notification endpoint
    print("3. Testing POST notification endpoint...")
    test_notification = {
        "notificationId": "test_123",
        "eventDate": datetime.now().isoformat(),
        "publishedDate": datetime.now().isoformat(),
        "sourceId": "test_source",
        "eventType": "ACCOUNT_DELETION_COMPLETED",
        "username": "test_user"
    }
    
    try:
        response = requests.post(
            f"{base_url}/ebay/marketplace_account_deletion",
            json=test_notification,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
            print("   ✅ POST notification passed!")
        else:
            print(f"   ❌ POST notification failed: {response.text}")
    except Exception as e:
        print(f"   ❌ POST notification error: {e}")
    
    print()
    
    # Test 4: Root endpoint
    print("4. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
            print("   ✅ Root endpoint passed!")
        else:
            print(f"   ❌ Root endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    print()
    print("🎯 SUMMARY")
    print("=" * 50)
    print("If all tests passed, your webhook is ready for eBay compliance!")
    print("Next steps:")
    print("1. Go to eBay Developer Portal")
    print("2. Update webhook URL to: " + base_url + "/ebay/marketplace_account_deletion")
    print("3. Set verification token to: pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123")
    print("4. Test the webhook configuration in eBay portal")

if __name__ == "__main__":
    test_railway_endpoint()
