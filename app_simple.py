import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Pokemon Webhook v2"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
            # eBay requires SHA256 hash of: challengeCode + verificationToken + endpoint
            verification_token = os.getenv('EBAY_VERIFICATION_TOKEN', 'pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123')
            endpoint = request.url_root.rstrip('/') + '/ebay/marketplace_account_deletion'
            
            # Create hash as per eBay documentation
            hash_input = challenge_code + verification_token + endpoint
            hash_obj = hashlib.sha256(hash_input.encode('utf-8'))
            challenge_response = hash_obj.hexdigest()
            
            return jsonify({"challengeResponse": challenge_response})
        return jsonify({"error": "No challenge code"}), 400
    
    return jsonify({"status": "received"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
