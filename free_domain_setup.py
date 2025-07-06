#!/usr/bin/env python3
"""
Free eBay Compliance Setup - Duck DNS + Let's Encrypt
"""

print("🆓 FREE EBAY COMPLIANCE SETUP")
print("=" * 50)
print()
print("🌐 STEP 1: Get Free Domain (Duck DNS)")
print("1. Go to: https://www.duckdns.org")
print("2. Sign in with Google/GitHub/Reddit (free)")
print("3. Create a subdomain like: pokemon-arbitrage")
print("4. You'll get: pokemon-arbitrage.duckdns.org")
print("5. Set the IP to: 34.74.208.133")
print()
print("🔒 STEP 2: Get Free SSL Certificate (Let's Encrypt)")
print("We'll install Certbot and get a free SSL certificate")
print()
print("⚡ STEP 3: Update Webhook Server")
print("Update your server to use port 443 (standard HTTPS)")
print()
print("💰 TOTAL COST: $0.00 (completely free!)")
print()
print("Let me help you set this up step by step...")
print()

# First, let's install certbot
print("🔧 Installing Certbot (Let's Encrypt client)...")
import subprocess
import os

try:
    # Check if certbot is already installed
    result = subprocess.run(['which', 'certbot'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Certbot already installed")
    else:
        print("📦 Installing Certbot...")
        # Install certbot
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        subprocess.run(['sudo', 'apt', 'install', '-y', 'certbot'], check=True)
        print("✅ Certbot installed successfully")
        
except Exception as e:
    print(f"❌ Error installing certbot: {e}")
    print("Manual installation:")
    print("sudo apt update")
    print("sudo apt install -y certbot")

print()
print("🎯 NEXT STEPS:")
print("1. Set up Duck DNS domain (manual step)")
print("2. Get SSL certificate with certbot")
print("3. Update webhook server configuration")
print("4. Test with eBay")
print()
print("Ready to continue with Duck DNS setup?")
