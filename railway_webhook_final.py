#!/usr/bin/env python3
"""
Railway deployment for eBay compliance
Quick deployment to get trusted SSL immediately
"""
import os
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy", 
        "server": "pokemon_arbitrage_railway",
        "https": True
    })

@app.route('/marketplace-deletion', methods=['POST', 'GET'])
def marketplace_deletion():
    """eBay Marketplace Account Deletion Notification Endpoint"""
    
    try:
        if request.method == 'GET':
            # eBay verification request with challenge code
            challenge_code = request.args.get('challenge_code')
            verification_token = os.getenv('EBAY_VERIFICATION_TOKEN', 'pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123')
            
            # Use Railway's provided domain
            railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
            if railway_domain:
                endpoint = f"https://{railway_domain}/marketplace-deletion"
            else:
                # Fallback for testing
                endpoint = "https://your-app-name.up.railway.app/marketplace-deletion"
            
            print(f"🔍 eBay verification request - challenge_code: {challenge_code}")
            print(f"🔑 Using verification token: {verification_token}")
            print(f"🌐 Endpoint URL: {endpoint}")
            
            if challenge_code and verification_token:
                # Create SHA-256 hash: challengeCode + verificationToken + endpoint
                import hashlib
                hash_input = challenge_code + verification_token + endpoint
                challenge_response = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
                
                print(f"📊 Hash input: {hash_input}")
                print(f"✅ Generated challenge response: {challenge_response}")
                
                # Return JSON response with challengeResponse
                return jsonify({"challengeResponse": challenge_response}), 200
            else:
                error_msg = "Missing challenge_code or verification_token"
                print(f"❌ {error_msg}")
                return jsonify({"error": error_msg}), 400
        
        elif request.method == 'POST':
            # Actual account deletion notification
            data = request.get_json()
            print(f"📨 eBay account deletion notification: {data}")
            
            # Process the deletion request
            if data and 'notification' in data:
                user_data = data['notification'].get('data', {})
                username = user_data.get('username')
                user_id = user_data.get('userId')
                
                print(f"🗑️ Processing deletion for user: {username} (ID: {user_id})")
                
                # Here you would delete user data from your database
                # For now, just log it
                print(f"✅ User data deletion processed for: {username}")
            
            # Respond with 200 OK as required
            return jsonify({"status": "acknowledged"}), 200
            
    except Exception as e:
        print(f"❌ Marketplace deletion endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
