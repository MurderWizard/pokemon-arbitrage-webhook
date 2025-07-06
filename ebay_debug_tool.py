#!/usr/bin/env python3
"""
eBay Compliance Debugging Tool - Programmatic Solution
This will find and fix whatever eBay is complaining about
"""
import requests
import hashlib
import json
import time
from datetime import datetime

def main():
    print("🔧 EBAY COMPLIANCE DEBUGGING TOOL")
    print("=" * 60)
    print()
    
    # Your endpoint details
    endpoint_url = "https://pokemon-arbitrage.duckdns.org:8443/marketplace-deletion"
    verification_token = "pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123"
    
    print(f"🎯 Testing endpoint: {endpoint_url}")
    print(f"🔑 Verification token: {verification_token}")
    print()
    
    # Test 1: Basic connectivity
    print("🧪 TEST 1: Basic Connectivity")
    print("-" * 40)
    try:
        response = requests.get(f"https://pokemon-arbitrage.duckdns.org:8443/health", 
                              verify=False, timeout=10)
        if response.status_code == 200:
            print("✅ Server is reachable")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Server returned {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Connectivity failed: {e}")
        return
    
    # Test 2: GET request format (what eBay sends)
    print("\\n🧪 TEST 2: eBay GET Request Simulation")
    print("-" * 40)
    test_challenge = "test_challenge_123456"
    test_url = f"{endpoint_url}?challenge_code={test_challenge}"
    
    try:
        response = requests.get(test_url, verify=False, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print(f"📄 Content: {response.text}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                if 'challengeResponse' in json_response:
                    print("✅ JSON response format is correct")
                    
                    # Verify the hash calculation
                    expected_hash = hashlib.sha256(
                        (test_challenge + verification_token + endpoint_url).encode('utf-8')
                    ).hexdigest()
                    
                    if json_response['challengeResponse'] == expected_hash:
                        print("✅ Hash calculation is correct")
                    else:
                        print("❌ Hash calculation is wrong!")
                        print(f"   Expected: {expected_hash}")
                        print(f"   Got: {json_response['challengeResponse']}")
                else:
                    print("❌ Missing 'challengeResponse' field")
            except json.JSONDecodeError:
                print("❌ Response is not valid JSON")
        else:
            print(f"❌ Wrong status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ GET request failed: {e}")
        return
    
    # Test 3: Content-Type header check
    print("\\n🧪 TEST 3: Content-Type Header Check")
    print("-" * 40)
    content_type = response.headers.get('content-type', '')
    print(f"📄 Content-Type: {content_type}")
    
    if 'application/json' in content_type.lower():
        print("✅ Content-Type is correct")
    else:
        print("❌ Content-Type should be 'application/json'")
        print("   This is likely the issue eBay is complaining about!")
    
    # Test 4: Check for BOM (Byte Order Mark)
    print("\\n🧪 TEST 4: Byte Order Mark (BOM) Check")
    print("-" * 40)
    raw_content = response.content
    
    if raw_content.startswith(b'\\xef\\xbb\\xbf'):
        print("❌ BOM detected! This will cause eBay validation to fail")
        print("   The response has a Byte Order Mark which makes it invalid JSON")
    else:
        print("✅ No BOM detected")
    
    # Test 5: Exact response format test
    print("\\n🧪 TEST 5: Response Format Validation")
    print("-" * 40)
    
    try:
        json_obj = json.loads(response.text)
        formatted_json = json.dumps(json_obj, separators=(',', ':'))
        print(f"📄 Formatted JSON: {formatted_json}")
        
        # Check if it matches eBay's expected format exactly
        expected_format = '{"challengeResponse":"' + json_obj.get('challengeResponse', '') + '"}'
        if formatted_json == expected_format:
            print("✅ JSON format matches eBay requirements exactly")
        else:
            print("⚠️  JSON format might not match eBay's expectations")
            print(f"   Expected: {expected_format}")
            print(f"   Got: {formatted_json}")
            
    except Exception as e:
        print(f"❌ JSON validation failed: {e}")
    
    # Test 6: Test with real eBay user agent
    print("\\n🧪 TEST 6: eBay User Agent Simulation")
    print("-" * 40)
    
    headers = {
        'User-Agent': 'eBayNotificationValidator/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(test_url, headers=headers, verify=False, timeout=10)
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Works with eBay-like headers")
        else:
            print("❌ Fails with eBay-like headers")
            
    except Exception as e:
        print(f"❌ eBay simulation failed: {e}")
    
    # Generate fix recommendations
    print("\\n🔧 DIAGNOSIS & RECOMMENDATIONS")
    print("=" * 60)
    
    issues_found = []
    fixes = []
    
    # Check content type
    if 'application/json' not in content_type.lower():
        issues_found.append("Wrong Content-Type header")
        fixes.append("Fix Flask response to set proper Content-Type")
    
    # Check for BOM
    if raw_content.startswith(b'\\xef\\xbb\\xbf'):
        issues_found.append("Byte Order Mark (BOM) present")
        fixes.append("Remove BOM from response encoding")
    
    if not issues_found:
        print("🤔 Technical tests pass, but eBay still rejects...")
        print()
        print("🎯 LIKELY ISSUES:")
        print("1. eBay might not like the port :8443 in the URL")
        print("2. Self-signed certificate might be rejected")
        print("3. Duck DNS domain might not be trusted")
        print("4. eBay might require standard port 443")
        print()
        print("💡 SOLUTIONS:")
        print("1. Deploy to a cloud service with proper SSL (Railway, Render)")
        print("2. Use a reverse proxy to handle SSL on port 443")
        print("3. Try a different domain service")
        
    else:
        print("🎯 ISSUES FOUND:")
        for i, issue in enumerate(issues_found, 1):
            print(f"{i}. {issue}")
        
        print("\\n🔧 FIXES NEEDED:")
        for i, fix in enumerate(fixes, 1):
            print(f"{i}. {fix}")
    
    print("\\n🚀 AUTOMATED FIX COMING UP...")
    print("Creating a fixed webhook server...")

if __name__ == '__main__':
    main()
