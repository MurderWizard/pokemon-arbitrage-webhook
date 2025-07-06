#!/usr/bin/env python3
"""
Final test script for Railway deployment after fixing railway.toml and Dockerfile
"""

import requests
import json
import time

def test_railway_endpoint():
    """Test the Railway webhook endpoint for eBay compliance"""
    
    # Replace with your actual Railway URL
    base_url = "https://pokemon-arbitrage-webhook-production.up.railway.app"
    
    print("🚀 Testing Railway Webhook Endpoint")
    print(f"Base URL: {base_url}")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: eBay GET challenge (verification)
    print("\n2. Testing eBay GET challenge endpoint...")
    challenge_params = {
        'challenge_code': 'test_challenge_123',
        'verification_token': 'test_token'
    }
    
    try:
        response = requests.get(f"{base_url}/webhook", params=challenge_params, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            if data.get('challengeResponse') == 'test_challenge_123':
                print("   ✅ Challenge response correct")
            else:
                print("   ❌ Challenge response incorrect")
                return False
        else:
            print(f"   ❌ Challenge failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Challenge error: {e}")
        return False
    
    # Test 3: eBay POST notification
    print("\n3. Testing eBay POST notification endpoint...")
    notification_data = {
        "metadata": {
            "topic": "MARKETPLACE_ACCOUNT_DELETION",
            "schemaVersion": "1.0",
            "deprecated": False
        },
        "notification": {
            "notificationId": "test123",
            "eventDate": "2024-01-01T12:00:00Z",
            "publishedDate": "2024-01-01T12:00:00Z",
            "data": {
                "username": "testuser",
                "userId": "12345",
                "eiasToken": "test_token"
            }
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'eBay/Marketplace'
    }
    
    try:
        response = requests.post(
            f"{base_url}/webhook", 
            json=notification_data, 
            headers=headers, 
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            if data.get('status') == 'success':
                print("   ✅ Notification processed successfully")
            else:
                print("   ❌ Notification processing failed")
                return False
        else:
            print(f"   ❌ Notification failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Notification error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! Railway endpoint is eBay compliant!")
    print("\nNext steps:")
    print("1. Copy your Railway URL to eBay Developer Portal")
    print("2. Set your verification token in Railway environment variables")
    print("3. Run eBay's validation test")
    return True

if __name__ == "__main__":
    # Wait a bit for Railway to deploy
    print("Waiting 30 seconds for Railway deployment...")
    time.sleep(30)
    
    success = test_railway_endpoint()
    exit(0 if success else 1)
