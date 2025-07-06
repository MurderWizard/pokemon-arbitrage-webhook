#!/usr/bin/env python3
"""
eBay Challenge Response Generator - Production Version
For testing with your actual server endpoint
"""
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Your production values
verification_token = os.getenv('EBAY_VERIFICATION_TOKEN')
endpoint = "https://34.74.208.133:8443/marketplace-deletion"  # Your actual server

print("🔧 eBay Challenge Response Generator - PRODUCTION")
print("=" * 60)
print(f"Verification Token: {verification_token}")
print(f"Production Endpoint: {endpoint}")
print()

if not verification_token:
    print("❌ ERROR: EBAY_VERIFICATION_TOKEN not found in .env file!")
    print("Please make sure you have added it to your .env file:")
    print("EBAY_VERIFICATION_TOKEN=pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123")
    exit(1)

print("💡 Instructions:")
print("1. Enter this endpoint in eBay Developer Portal:")
print(f"   {endpoint}")
print("2. Enter this verification token:")
print(f"   {verification_token}")
print("3. eBay will send a challenge_code to test your endpoint")
print("4. Enter that challenge_code below to generate the response")
print()

# Wait for user to enter challenge code
challenge_code = input("Enter the challenge_code from eBay (when it appears): ")

if challenge_code:
    # Create hash: challengeCode + verificationToken + endpoint
    hash_input = challenge_code + verification_token + endpoint
    challenge_response = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    print()
    print("📊 CALCULATION:")
    print(f"Challenge Code: '{challenge_code}'")
    print(f"Verification Token: '{verification_token}'")
    print(f"Endpoint: '{endpoint}'")
    print(f"Hash Input: '{hash_input}'")
    print(f"SHA-256 Hash: {challenge_response}")
    print()
    print("🎯 JSON RESPONSE FOR EBAY:")
    print(f'{{"challengeResponse":"{challenge_response}"}}')
    print()
    print("✅ Your webhook server should automatically return this response!")
    print("   But you can also copy the JSON above if needed for manual testing.")
else:
    print("❌ No challenge code provided")
