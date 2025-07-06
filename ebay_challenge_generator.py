#!/usr/bin/env python3
"""
Generate eBay Challenge Response
"""
import hashlib

def generate_challenge_response(challenge_code):
    verification_token = "pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123"
    endpoint = "https://webhook.site/878b378e-2c5d-4a2f-9cda-9247f4e08bf5"  # Your actual webhook.site URL
    
    # Create hash: challengeCode + verificationToken + endpoint
    hash_input = challenge_code + verification_token + endpoint
    challenge_response = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    print(f"Challenge Code: {challenge_code}")
    print(f"Verification Token: {verification_token}")
    print(f"Endpoint: {endpoint}")
    print(f"Hash Input: {hash_input}")
    print(f"Challenge Response: {challenge_response}")
    
    # JSON response format
    json_response = f'{{"challengeResponse":"{challenge_response}"}}'
    print(f"\nJSON Response:\n{json_response}")
    
    return challenge_response

if __name__ == "__main__":
    # Example usage - replace with actual challenge code from eBay
    challenge_code = input("Enter challenge_code from eBay: ")
    generate_challenge_response(challenge_code)
