#!/usr/bin/env python3
"""
eBay Endpoint Connectivity Tester
Tests if eBay can reach your endpoint from external networks
"""
import requests
import socket
import subprocess
import os
from urllib.parse import urlparse

print("🔧 eBay ENDPOINT CONNECTIVITY TESTER")
print("=" * 60)

# Your endpoint details
endpoint_url = "https://34.74.208.133:8443/marketplace-deletion"
health_url = "https://34.74.208.133:8443/health"
server_ip = "34.74.208.133"
server_port = 8443

print(f"🎯 Testing endpoint: {endpoint_url}")
print()

# Test 1: Local connectivity
print("1️⃣ Testing local connectivity...")
try:
    response = requests.get(health_url, verify=False, timeout=5)
    if response.status_code == 200:
        print("✅ Local health check: SUCCESS")
    else:
        print(f"❌ Local health check: FAILED ({response.status_code})")
except Exception as e:
    print(f"❌ Local connectivity: FAILED - {e}")
    print("   Server may not be running!")
    exit(1)

# Test 2: Port accessibility 
print("\n2️⃣ Testing port accessibility...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((server_ip, server_port))
    sock.close()
    
    if result == 0:
        print("✅ Port 8443 is accessible")
    else:
        print("❌ Port 8443 is NOT accessible from external networks")
        print("   This is likely why eBay validation failed!")
except Exception as e:
    print(f"❌ Port test failed: {e}")

# Test 3: Firewall status
print("\n3️⃣ Checking firewall status...")
try:
    result = subprocess.run(['sudo', 'ufw', 'status'], capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print("🔥 UFW Firewall status:")
        print(result.stdout)
        
        # Check if port 8443 is allowed
        if "8443" in result.stdout:
            print("✅ Port 8443 appears to be allowed in firewall")
        else:
            print("❌ Port 8443 NOT found in firewall rules")
            print("   Run: sudo ufw allow 8443")
    else:
        print("⚠️ Could not check UFW status (may not be installed)")
except Exception as e:
    print(f"⚠️ Firewall check failed: {e}")

# Test 4: External HTTP test
print("\n4️⃣ Testing external HTTP accessibility...")
try:
    # Try a simple curl test
    result = subprocess.run([
        'curl', '-k', '--connect-timeout', '10', '--max-time', '15', 
        f'{health_url}'
    ], capture_output=True, text=True, timeout=20)
    
    if result.returncode == 0 and "healthy" in result.stdout:
        print("✅ External HTTP test: SUCCESS")
        print(f"   Response: {result.stdout.strip()}")
    else:
        print("❌ External HTTP test: FAILED")
        print(f"   Return code: {result.returncode}")
        print(f"   Error: {result.stderr}")
except Exception as e:
    print(f"❌ External HTTP test failed: {e}")

# Test 5: SSL Certificate check
print("\n5️⃣ Testing SSL certificate...")
try:
    result = subprocess.run([
        'openssl', 's_client', '-connect', f'{server_ip}:{server_port}', 
        '-servername', server_ip
    ], input="", capture_output=True, text=True, timeout=10)
    
    if "CONNECTED" in result.stdout:
        print("✅ SSL connection established")
        if "self signed certificate" in result.stderr or "self-signed" in result.stderr:
            print("⚠️ Using self-signed certificate (eBay might reject this)")
            print("   Consider getting a proper SSL certificate")
        else:
            print("✅ SSL certificate appears valid")
    else:
        print("❌ SSL connection failed")
        print(f"   Error: {result.stderr}")
except Exception as e:
    print(f"❌ SSL test failed: {e}")

print("\n" + "=" * 60)
print("🎯 DIAGNOSIS SUMMARY:")
print()
print("If eBay validation failed, the most likely causes are:")
print("1. 🔥 Firewall blocking external access to port 8443")
print("2. 🔒 Self-signed SSL certificate rejected by eBay")
print("3. 🌐 Network/ISP blocking incoming HTTPS connections")
print("4. ☁️ Cloud provider security groups blocking the port")
print()
print("💡 SOLUTIONS:")
print("1. Open firewall: sudo ufw allow 8443")
print("2. Get a proper SSL certificate (Let's Encrypt, etc.)")
print("3. Check cloud provider security groups")
print("4. Test from external network: curl -k", health_url)
print()
print("🔧 ALTERNATIVE: Use a service like ngrok for testing:")
print("   ngrok http 8443")
print("   Then use the ngrok HTTPS URL in eBay developer portal")
