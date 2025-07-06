#!/usr/bin/env python3
"""
eBay Debug and Fix Tool - Find out exactly what's wrong
"""
import json
import hashlib
import requests
from datetime import datetime

def test_ebay_endpoint():
    print("🔍 DEBUGGING EBAY VALIDATION FAILURE")
    print("=" * 60)
    
    # Your exact values
    endpoint = "https://pokemon-arbitrage.duckdns.org:8443/marketplace-deletion"
    token = "pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123"
    
    print(f"🌐 Testing endpoint: {endpoint}")
    print(f"🔑 Using token: {token}")
    print(f"📏 Token length: {len(token)} chars (eBay requires 32-80)")
    print()
    
    # Test 1: Basic connectivity
    print("📡 TEST 1: Basic Connectivity")
    try:
        response = requests.get(f"{endpoint}?challenge_code=test123", 
                              timeout=10, verify=False)
        print(f"✅ Response code: {response.status_code}")
        print(f"✅ Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON response: {data}")
                
                if 'challengeResponse' in data:
                    print("✅ Contains challengeResponse field")
                    hash_value = data['challengeResponse']
                    print(f"✅ Hash value: {hash_value}")
                    print(f"📏 Hash length: {len(hash_value)} chars")
                else:
                    print("❌ Missing challengeResponse field")
            except Exception as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Raw response: {response.text}")
        else:
            print(f"❌ Bad response code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Test 2: Content-Type header check
    print(f"\n📄 TEST 2: Content-Type Header")
    content_type = response.headers.get('content-type', '').lower()
    if 'application/json' in content_type:
        print("✅ Correct Content-Type: application/json")
    else:
        print(f"❌ Wrong Content-Type: {content_type}")
        print("   eBay requires 'application/json'")
    
    # Test 3: Manual hash calculation
    print(f"\n🧮 TEST 3: Hash Calculation Verification")
    test_challenge = "test123"
    
    # Exactly as eBay docs specify: challengeCode + verificationToken + endpoint
    hash_input = test_challenge + token + endpoint
    expected_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    print(f"Challenge: '{test_challenge}'")
    print(f"Token: '{token}'")
    print(f"Endpoint: '{endpoint}'")
    print(f"Hash input: '{hash_input}'")
    print(f"Expected hash: {expected_hash}")
    
    if 'challengeResponse' in data:
        actual_hash = data['challengeResponse']
        if actual_hash == expected_hash:
            print("✅ Hash calculation is CORRECT")
        else:
            print("❌ Hash calculation is WRONG")
            print(f"   Expected: {expected_hash}")
            print(f"   Got:      {actual_hash}")
    
    # Test 4: Try from external source (simulate eBay)
    print(f"\n🌍 TEST 4: External Access Test")
    try:
        # Test from a public API to see if it's accessible externally
        test_url = f"https://httpbin.org/get?test_endpoint={endpoint}"
        print(f"Testing external visibility...")
        
        # Just test basic DNS resolution
        import socket
        ip = socket.gethostbyname('pokemon-arbitrage.duckdns.org')
        print(f"✅ DNS resolves to: {ip}")
        
    except Exception as e:
        print(f"❌ DNS resolution failed: {e}")
    
    # Test 5: Check for common eBay issues
    print(f"\n🚨 TEST 5: Common eBay Issues")
    
    issues = []
    
    # Check port
    if ':8443' in endpoint:
        issues.append("⚠️  Using non-standard port 8443 (eBay prefers 443)")
    
    # Check protocol
    if not endpoint.startswith('https://'):
        issues.append("❌ Must use HTTPS")
    
    # Check domain
    if 'localhost' in endpoint or '127.0.0.1' in endpoint:
        issues.append("❌ Cannot use localhost or internal IPs")
    
    # Check token format
    if len(token) < 32 or len(token) > 80:
        issues.append(f"❌ Token length {len(token)} not in range 32-80")
    
    if not all(c.isalnum() or c in '_-' for c in token):
        issues.append("❌ Token contains invalid characters (only alphanumeric, _, - allowed)")
    
    if issues:
        print("Found potential issues:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ No obvious issues found")
    
    print(f"\n🎯 RECOMMENDATION:")
    if not issues and response.status_code == 200 and 'challengeResponse' in data:
        print("✅ Your endpoint appears to be working correctly!")
        print("   The issue might be:")
        print("   1. eBay's servers can't reach your endpoint due to network routing")
        print("   2. eBay doesn't accept self-signed certificates")
        print("   3. eBay doesn't like the non-standard port :8443")
        print(f"\n🔧 Try using a tunneling service like ngrok:")
        print("   1. Install ngrok: curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null")
        print("   2. Run: ngrok http 8443")
        print("   3. Use the ngrok HTTPS URL in eBay portal")
    else:
        print("❌ Found issues that need to be fixed first")
    
    return True

if __name__ == '__main__':
    test_ebay_endpoint()
