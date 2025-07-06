#!/usr/bin/env python3
"""
Comprehensive eBay Compliance Check
Tests all aspects of the marketplace deletion endpoint
"""
import requests
import hashlib
import json
import ssl
from urllib.parse import urlencode

# Configuration
DOMAIN = "pokemon-arbitrage.duckdns.org"
ENDPOINT_PATH = "/marketplace-deletion"
VERIFICATION_TOKEN = "pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123"
FULL_ENDPOINT_URL = f"https://{DOMAIN}{ENDPOINT_PATH}"

def test_ssl_certificate():
    """Test SSL certificate validity"""
    print("🔒 Testing SSL Certificate...")
    try:
        import socket
        context = ssl.create_default_context()
        with socket.create_connection((DOMAIN, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=DOMAIN) as ssock:
                cert = ssock.getpeercert()
                print(f"   ✅ SSL connection successful")
                print(f"   📋 Subject: {cert.get('subject')}")
                print(f"   📅 Not after: {cert.get('notAfter')}")
                print(f"   🏢 Issuer: {cert.get('issuer')}")
                return True
    except Exception as e:
        print(f"   ❌ SSL Error: {e}")
        return False

def test_domain_resolution():
    """Test domain name resolution"""
    print("🌐 Testing Domain Resolution...")
    try:
        import socket
        ip = socket.gethostbyname(DOMAIN)
        print(f"   ✅ Domain resolves to: {ip}")
        return True
    except Exception as e:
        print(f"   ❌ Domain resolution error: {e}")
        return False

def test_basic_connectivity():
    """Test basic HTTPS connectivity"""
    print("🔗 Testing Basic HTTPS Connectivity...")
    try:
        response = requests.get(f"https://{DOMAIN}/health", verify=False, timeout=10)
        print(f"   ✅ HTTPS connection successful")
        print(f"   📊 Status: {response.status_code}")
        print(f"   📋 Response: {response.text}")
        return True
    except Exception as e:
        print(f"   ❌ Connectivity error: {e}")
        return False

def test_challenge_response(challenge_code="ebay_test_challenge_12345"):
    """Test the challenge/response mechanism"""
    print(f"🎯 Testing Challenge/Response with code: {challenge_code}...")
    
    try:
        # Test the endpoint
        url = f"{FULL_ENDPOINT_URL}?challenge_code={challenge_code}"
        print(f"   🔗 Request URL: {url}")
        
        headers = {
            'User-Agent': 'eBayMarketplaceNotification/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        
        print(f"   📊 Status Code: {response.status_code}")
        print(f"   📋 Headers: {dict(response.headers)}")
        print(f"   📄 Response: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                returned_hash = data.get('challengeResponse')
                
                # Calculate expected hash
                hash_input = challenge_code + VERIFICATION_TOKEN + FULL_ENDPOINT_URL
                expected_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
                
                print(f"   🔑 Hash input: {hash_input}")
                print(f"   ✅ Expected hash: {expected_hash}")
                print(f"   🎯 Returned hash: {returned_hash}")
                
                if returned_hash == expected_hash:
                    print(f"   ✅ Challenge/response CORRECT!")
                    return True
                else:
                    print(f"   ❌ Challenge/response MISMATCH!")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON decode error: {e}")
                return False
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Challenge test error: {e}")
        return False

def test_post_endpoint():
    """Test the POST endpoint for notifications"""
    print("📬 Testing POST Endpoint...")
    
    try:
        test_notification = {
            "notification": {
                "notificationId": "test123",
                "eventDate": "2025-07-06T06:00:00.000Z",
                "publishDate": "2025-07-06T06:00:00.000Z",
                "sourceSystem": "MARKETPLACE",
                "data": {
                    "username": "testuser123",
                    "userId": "12345",
                    "email": "test@example.com"
                }
            }
        }
        
        headers = {
            'User-Agent': 'eBayMarketplaceNotification/1.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(
            FULL_ENDPOINT_URL, 
            json=test_notification, 
            headers=headers, 
            verify=False, 
            timeout=10
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        print(f"   📋 Response: {response.text}")
        
        if response.status_code == 200:
            print(f"   ✅ POST endpoint working correctly!")
            return True
        else:
            print(f"   ❌ POST endpoint error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ POST test error: {e}")
        return False

def test_response_format():
    """Test that response format exactly matches eBay requirements"""
    print("📝 Testing Response Format Compliance...")
    
    challenge_code = "format_test_123"
    url = f"{FULL_ENDPOINT_URL}?challenge_code={challenge_code}"
    
    try:
        response = requests.get(url, verify=False, timeout=10)
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        print(f"   📋 Content-Type: {content_type}")
        
        if 'application/json' not in content_type:
            print(f"   ⚠️  Warning: Content-Type should be application/json")
        
        # Check response body
        response_text = response.text
        print(f"   📄 Raw Response: {repr(response_text)}")
        
        # Check for BOM or extra characters
        if response_text.startswith('\ufeff'):
            print(f"   ❌ Response has BOM character!")
        
        # Parse JSON
        try:
            data = response.json()
            if 'challengeResponse' in data and len(data) == 1:
                print(f"   ✅ Response format is correct")
                return True
            else:
                print(f"   ❌ Response format incorrect. Expected only 'challengeResponse' field")
                return False
        except:
            print(f"   ❌ Response is not valid JSON")
            return False
            
    except Exception as e:
        print(f"   ❌ Format test error: {e}")
        return False

def test_from_external():
    """Test from external perspective (like eBay would)"""
    print("🌍 Testing from External Perspective...")
    
    try:
        # Use a different user agent to simulate eBay
        headers = {
            'User-Agent': 'eBayMarketplaceAccountDeletion/1.0',
            'Accept': 'application/json'
        }
        
        challenge_code = "external_test_456"
        url = f"{FULL_ENDPOINT_URL}?challenge_code={challenge_code}"
        
        # Test with SSL verification enabled (like eBay would)
        response = requests.get(url, headers=headers, verify=True, timeout=15)
        
        print(f"   ✅ External test successful!")
        print(f"   📊 Status: {response.status_code}")
        return True
        
    except requests.exceptions.SSLError as e:
        print(f"   ❌ SSL Verification Failed: {e}")
        print(f"   💡 This might be why eBay validation fails!")
        return False
    except Exception as e:
        print(f"   ❌ External test error: {e}")
        return False

def main():
    print("🚀 eBay Marketplace Account Deletion Compliance Check")
    print("=" * 60)
    
    tests = [
        ("Domain Resolution", test_domain_resolution),
        ("SSL Certificate", test_ssl_certificate),
        ("Basic Connectivity", test_basic_connectivity),
        ("Challenge/Response", test_challenge_response),
        ("POST Endpoint", test_post_endpoint),
        ("Response Format", test_response_format),
        ("External Access", test_from_external)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        results[test_name] = test_func()
    
    print("\n" + "=" * 60)
    print("📊 COMPLIANCE CHECK SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Your endpoint should work with eBay.")
    else:
        print("⚠️  SOME TESTS FAILED. Check the issues above.")
        print("\n🔧 Common solutions:")
        print("   • SSL issues: Use Let's Encrypt or deploy to Railway/Render")
        print("   • Domain issues: Verify DNS propagation")
        print("   • Format issues: Check JSON response format")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
