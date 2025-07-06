#!/usr/bin/env python3
"""
Minimal Railway-optimized Flask webhook server
"""
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def health():
    return jsonify({
        "status": "healthy",
        "service": "pokemon-arbitrage-webhook",
        "environment": "railway"
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": "2025-07-06"})

@app.route('/ebay/marketplace_account_deletion', methods=['GET', 'POST'])
def ebay_webhook():
    if request.method == 'GET':
        challenge = request.args.get('challenge_code')
        if challenge:
            return jsonify({"challengeResponse": challenge})
        return jsonify({"error": "No challenge code provided"}), 400
    
    if request.method == 'POST':
        notification = request.get_json() or {}
        return jsonify({
            "status": "received", 
            "notificationId": notification.get("notificationId", "unknown")
        })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
