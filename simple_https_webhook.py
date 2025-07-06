#!/usr/bin/env python3
"""
Simple HTTPS webhook test server for Pokemon arbitrage bot
"""
import os
import ssl
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    print("📨 Received webhook:", request.get_json())
    return jsonify({"status": "ok"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    # SSL setup
    cert_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.crt'
    key_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.key'
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(cert_file, key_file)
        print("🔒 Starting HTTPS webhook server on port 8080...")
        app.run(host='0.0.0.0', port=8080, ssl_context=context, debug=True)
    else:
        print("❌ SSL certificates not found!")
