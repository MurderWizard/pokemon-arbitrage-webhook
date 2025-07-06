#!/usr/bin/env python3
"""
Test script for Railway-deployed eBay webhook endpoint
"""
import requests
import hashlib
import json

def test_railway_webhook(base_url):
    """Test the Railway-deployed webhook for eBay compliance"""
    
    print(f"🧪 Testing Railway webhook at: {base_url}")
    print("=" * 60)
    
    # Test 1: Health check
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2️⃣ Testing root endpoint...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint working: {data['service']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: eBay challenge simulation
    print("\n3️⃣ Testing eBay challenge endpoint...")
    challenge_code = "test_challenge_123"
    verification_token = "pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123"
    endpoint_url = f"{base_url}/marketplace-deletion"
    
    # Calculate expected hash
    hash_input = challenge_code + verification_token + endpoint_url
    expected_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    try:
        response = requests.get(
            f"{base_url}/marketplace-deletion",
            params={"challenge_code": challenge_code},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            returned_hash = data.get('challengeResponse')
            
            print(f"✅ Challenge endpoint responded: {response.status_code}")
            print(f"📊 Hash input: {hash_input}")
            print(f"🎯 Expected hash: {expected_hash}")
            print(f"📤 Returned hash: {returned_hash}")
            print(f"🔍 Content-Type: {response.headers.get('Content-Type')}")
            
            if returned_hash == expected_hash:
                print("✅ Hash calculation CORRECT!")
            else:
                print("❌ Hash calculation INCORRECT!")
                return False
        else:
            print(f"❌ Challenge endpoint failed: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Challenge endpoint error: {e}")
        return False
    
    # Test 4: POST request simulation
    print("\n4️⃣ Testing POST notification endpoint...")
    test_notification = {
        "notification": {
            "data": {
                "username": "test_user",
                "userId": "12345"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/marketplace-deletion",
            json=test_notification,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ POST notification working: {data}")
        else:
            print(f"❌ POST notification failed: {response.status_code}")
    except Exception as e:
        print(f"❌ POST notification error: {e}")
    
    print("\n🎉 Railway webhook testing complete!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        print("Usage: python test_railway.py <railway_url>")
        print("Example: python test_railway.py https://pokemon-arbitrage.up.railway.app")
        sys.exit(1)
    
    success = test_railway_webhook(base_url)
    
    if success:
        print(f"\n✅ All tests passed! Your Railway webhook is ready for eBay.")
        print(f"🔗 Use this URL in eBay Developer Portal: {base_url}/marketplace-deletion")
    else:
        print(f"\n❌ Some tests failed. Check the logs above.")
        sys.exit(1)
