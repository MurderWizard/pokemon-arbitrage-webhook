from flask import Flask, request, jsonify
import hashlib
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "Pokemon Arbitrage eBay Webhook", "ssl": "valid"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "ssl": "railway_valid"})

@app.route('/marketplace-deletion', methods=['GET', 'POST'])
def marketplace_deletion():
    """eBay Marketplace Account Deletion Endpoint with Valid SSL"""
    try:
        if request.method == 'GET':
            challenge_code = request.args.get('challenge_code')
            verification_token = "pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123"
            
            # Use Railway's provided domain
            endpoint = f"https://{request.host}/marketplace-deletion"
            
            if challenge_code and verification_token:
                hash_input = challenge_code + verification_token + endpoint
                challenge_response = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
                
                print(f"✅ eBay Challenge Response: {challenge_response}")
                return jsonify({"challengeResponse": challenge_response}), 200
            else:
                return jsonify({"error": "Missing challenge_code"}), 400
        
        elif request.method == 'POST':
            data = request.get_json()
            print(f"📨 eBay account deletion notification: {data}")
            return jsonify({"status": "acknowledged"}), 200
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
