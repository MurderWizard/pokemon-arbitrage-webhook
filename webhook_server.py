#!/usr/bin/env python3
"""
Production Webhook Server for Railway Deployment
eBay Marketplace Account Deletion Compliance
"""
import os
import json
import hashlib
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "pokemon_arbitrage_webhook",
        "platform": "railway",
        "compliance": "ebay_production",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/marketplace-deletion', methods=['GET', 'POST'])
def marketplace_deletion():
    """eBay Marketplace Account Deletion Notification Endpoint - PRODUCTION"""
    
    if request.method == 'GET':
        # eBay verification challenge
        challenge_code = request.args.get('challenge_code')
        verification_token = os.getenv('EBAY_VERIFICATION_TOKEN', 'pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123')
        
        # Get the endpoint URL from Railway
        railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
        if railway_domain:
            endpoint = f"https://{railway_domain}/marketplace-deletion"
        else:
            # Fallback to request host
            endpoint = f"https://{request.host}/marketplace-deletion"
        
        logger.info(f"eBay verification: challenge={challenge_code}, endpoint={endpoint}")
        
        if challenge_code and verification_token:
            # Calculate SHA-256 hash: challengeCode + verificationToken + endpoint
            hash_input = challenge_code + verification_token + endpoint
            challenge_response = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
            
            logger.info(f"Hash input: {hash_input}")
            logger.info(f"Challenge response: {challenge_response}")
            
            response = {"challengeResponse": challenge_response}
            
            # Ensure proper JSON response with correct content-type
            return app.response_class(
                response=json.dumps(response),
                status=200,
                mimetype='application/json'
            )
        else:
            return jsonify({"error": "Missing challenge_code or verification_token"}), 400
    
    elif request.method == 'POST':
        # Actual deletion notification
        data = request.get_json()
        logger.info(f"eBay deletion notification: {data}")
        
        # Log for compliance
        timestamp = datetime.now().isoformat()
        logger.info(f"{timestamp}: Account deletion notification received: {data}")
        
        # Process the deletion (implement your logic here)
        if data and 'notification' in data:
            user_data = data['notification'].get('data', {})
            username = user_data.get('username')
            user_id = user_data.get('userId')
            logger.info(f"Processing deletion for user: {username} (ID: {user_id})")
        
        # Return 200 OK as required by eBay
        return jsonify({"status": "acknowledged"}), 200
    
    return jsonify({"error": "Method not allowed"}), 405

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Telegram webhook for deal approvals"""
    try:
        data = request.get_json()
        logger.info(f"Telegram webhook: {data}")
        
        # Your existing Telegram logic here
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "service": "Pokemon Arbitrage Webhook",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "ebay_compliance": "/marketplace-deletion",
            "telegram": "/webhook"
        }
    }), 200

if __name__ == "__main__":
    # Get port from environment variable (for Railway) or use default
    port = int(os.getenv("PORT", 5000))
    
    # Run the Flask app
    app.run(host="0.0.0.0", port=port)
