#!/usr/bin/env python3
"""
Minimal working HTTPS webhook server for testing
"""
import os
import ssl
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print(f"Received webhook: {data}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "server": "minimal_webhook"})

if __name__ == '__main__':
    cert_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.crt'
    key_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.key'
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(cert_file, key_file)
        print("🔒 Starting HTTPS webhook server on https://0.0.0.0:8080")
        app.run(host='0.0.0.0', port=8080, ssl_context=context)
    else:
        print("❌ SSL certificates not found!")
        print("🌐 Starting HTTP webhook server on http://0.0.0.0:8080")
        app.run(host='0.0.0.0', port=8080)
