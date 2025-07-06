#!/usr/bin/env python3
"""
Quick test for the Railway-deployed eBay webhook
"""
import requests
import hashlib

def test_railway_webhook(railway_url):
    """Test the Railway webhook for eBay compliance"""
    
    print(f"🧪 Testing Railway webhook: {railway_url}")
    print("=" * 60)
    
    # Test 1: Health check
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{railway_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed!")
            print(f"   Server: {data.get('server', 'Unknown')}")
            print(f"   Platform: {data.get('platform', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: eBay challenge simulation
    print("\n2️⃣ Testing eBay compliance endpoint...")
    challenge_code = "test_challenge_abc123"
    verification_token = "pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123"
    endpoint_url = f"{railway_url}/marketplace-deletion"
    
    # Calculate expected hash
    hash_input = challenge_code + verification_token + endpoint_url
    expected_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    try:
        response = requests.get(
            endpoint_url,
            params={"challenge_code": challenge_code},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            returned_hash = data.get('challengeResponse')
            
            print(f"✅ eBay endpoint responded!")
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            print(f"   Expected hash: {expected_hash}")
            print(f"   Returned hash: {returned_hash}")
            
            if returned_hash == expected_hash:
                print("🎉 HASH CALCULATION PERFECT!")
                print("🛡️  eBay compliance READY!")
                return True
            else:
                print("❌ Hash mismatch")
                return False
        else:
            print(f"❌ eBay endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ eBay endpoint error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 RAILWAY WEBHOOK TESTER")
    print("=" * 60)
    
    railway_url = input("Enter your Railway URL (without trailing slash): ").strip().rstrip('/')
    
    if not railway_url.startswith('http'):
        railway_url = f"https://{railway_url}"
    
    success = test_railway_webhook(railway_url)
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print(f"🛡️  eBay Compliance Endpoint: {railway_url}/marketplace-deletion")
        print("🔗 Use this URL in eBay Developer Portal!")
        print("🚀 Your webhook is production-ready!")
    else:
        print("\n❌ Some tests failed.")
        print("💡 Make sure environment variables are set in Railway!")
