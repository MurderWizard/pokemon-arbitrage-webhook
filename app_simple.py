from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "healthy", "service": "pokemon-webhook"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/ebay/marketplace_account_deletion', methods=['GET', 'POST'])
def ebay_webhook():
    if request.method == 'GET':
        challenge = request.args.get('challenge_code')
        if challenge:
            return jsonify({"challengeResponse": challenge})
        return jsonify({"error": "No challenge code"}), 400
    
    return jsonify({"status": "received"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
