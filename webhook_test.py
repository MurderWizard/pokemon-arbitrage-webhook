#!/usr/bin/env python3
"""
Simple webhook test and deployment script
"""
import os
import ssl
import requests
import subprocess
import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

def test_ssl_certs():
    """Test SSL certificate files"""
    cert_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.crt'
    key_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.key'
    
    print("🔍 Testing SSL certificates...")
    if os.path.exists(cert_file):
        print(f"✅ Certificate found: {cert_file}")
    else:
        print(f"❌ Certificate missing: {cert_file}")
        return False
        
    if os.path.exists(key_file):
        print(f"✅ Key found: {key_file}")
    else:
        print(f"❌ Key missing: {key_file}")
        return False
    
    return True

def test_telegram_token():
    """Test Telegram bot token"""
    token = os.getenv('TG_TOKEN')
    print("🔍 Testing Telegram token...")
    if token:
        print("✅ Token found in environment")
        return token
    else:
        print("❌ Token not found")
        return None

def start_simple_webhook():
    """Start a simple webhook server"""
    print("🚀 Starting simple webhook server...")
    
    app = Flask(__name__)
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        data = request.get_json()
        print(f"📨 Webhook received: {data}")
        return jsonify({"status": "ok"})
    
    @app.route('/health', methods=['GET']) 
    def health():
        return jsonify({"status": "healthy"})
    
    # SSL setup
    cert_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.crt'
    key_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.key'
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.load_cert_chain(cert_file, key_file)
            print("🔒 Starting HTTPS server on port 8080...")
            app.run(host='0.0.0.0', port=8080, ssl_context=context, debug=False)
        except Exception as e:
            print(f"❌ HTTPS server failed: {e}")
            print("🌐 Falling back to HTTP...")
            app.run(host='0.0.0.0', port=8080, debug=False)
    else:
        print("🌐 Starting HTTP server on port 8080...")
        app.run(host='0.0.0.0', port=8080, debug=False)

def set_telegram_webhook(token):
    """Set the Telegram webhook"""
    webhook_url = "https://34.74.208.133:8080/webhook"
    cert_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.crt'
    
    print(f"🔗 Setting webhook to: {webhook_url}")
    
    try:
        url = f"https://api.telegram.org/bot{token}/setWebhook"
        
        if os.path.exists(cert_file):
            with open(cert_file, 'rb') as cert:
                files = {'certificate': cert}
                data = {
                    'url': webhook_url,
                    'max_connections': 40,
                    'allowed_updates': ['message', 'callback_query']
                }
                response = requests.post(url, data=data, files=files, timeout=30)
        else:
            # Try without certificate (for testing)
            data = {
                'url': webhook_url,
                'max_connections': 40,
                'allowed_updates': ['message', 'callback_query']
            }
            response = requests.post(url, json=data, timeout=30)
        
        if response.ok:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook set successfully!")
                return True
            else:
                print(f"❌ Telegram error: {result.get('description', 'Unknown')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🎴 POKEMON WEBHOOK TEST & DEPLOY")
    print("=" * 40)
    
    # Test 1: SSL certificates
    if not test_ssl_certs():
        print("❌ SSL test failed")
        return
    
    # Test 2: Telegram token
    token = test_telegram_token()
    if not token:
        print("❌ Token test failed")
        return
    
    print("\n" + "=" * 40)
    print("Choose an option:")
    print("1. Start webhook server")
    print("2. Set Telegram webhook")
    print("3. Both (recommended)")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        start_simple_webhook()
    elif choice == "2":
        set_telegram_webhook(token)
    elif choice == "3":
        print("🚀 Starting webhook server in background...")
        # Start server in background and set webhook
        import threading
        server_thread = threading.Thread(target=start_simple_webhook)
        server_thread.daemon = True
        server_thread.start()
        
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        print("🔗 Setting Telegram webhook...")
        if set_telegram_webhook(token):
            print("✅ Setup complete!")
            print("🎯 Webhook is now active")
            print("📱 Test by sending commands to your bot")
            try:
                input("Press Enter to stop server...")
            except KeyboardInterrupt:
                pass
        else:
            print("❌ Webhook setup failed")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
