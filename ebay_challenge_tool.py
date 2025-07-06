#!/usr/bin/env python3
"""
eBay Challenge Response Generator
"""
import hashlib

# Your specific values
verification_token = "pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123"
endpoint = "https://webhook.site/878b378e-2c5d-4a2f-9cda-9247f4e08bf5"

print("🔧 eBay Challenge Response Generator")
print("=" * 50)
print(f"Verification Token: {verification_token}")
print(f"Endpoint: {endpoint}")
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
    print(f"Hash Input: '{hash_input}'")
    print(f"SHA-256 Hash: {challenge_response}")
    print()
    print("🎯 JSON RESPONSE FOR EBAY:")
    print(f'{{"challengeResponse":"{challenge_response}"}}')
    print()
    print("✅ Copy the JSON response above and send it back to eBay!")
else:
    print("❌ No challenge code provided")
