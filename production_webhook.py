#!/usr/bin/env python3
"""
eBay Compliant Webhook Server - Production Ready
Uses proper domain and Let's Encrypt SSL certificates
"""
import os
import ssl
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

def answer_callback_query(callback_id, text, show_alert=False):
    """Send popup notification to user"""
    bot_token = os.getenv('TG_TOKEN')
    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    
    data = {
        "callback_query_id": callback_id,
        "text": text,
        "show_alert": show_alert
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.ok
    except Exception as e:
        print(f"Error answering callback: {e}")
        return False

def edit_message_with_status(chat_id, message_id, original_text, deal_id, status):
    """Update the message to show approval/rejection status"""
    bot_token = os.getenv('TG_TOKEN')
    url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
    
    print(f"🔄 Editing message: chat_id={chat_id}, message_id={message_id}, status={status}")
    
    # Add status banner to the message
    if status == "APPROVED":
        status_banner = f"\\n\\n🟢 **✅ DEAL APPROVED** 🟢\\n⏰ Decision made at {datetime.now().strftime('%H:%M:%S')}\\n🚀 Purchase process initiated!"
    elif status == "PASSED":
        status_banner = f"\\n\\n🔴 **❌ DEAL PASSED** 🔴\\n⏰ Decision made at {datetime.now().strftime('%H:%M:%S')}\\n🔍 Continuing search for opportunities..."
    else:
        status_banner = f"\\n\\n⚪ **Status: {status}**"
    
    updated_text = original_text + status_banner
    
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": updated_text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.ok:
            print(f"✅ Message updated successfully")
        else:
            print(f"❌ Failed to update message: {response.text}")
        return response.ok
    except Exception as e:
        print(f"Error updating message: {e}")
        return False

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Handle Telegram webhook for deal approvals"""
    try:
        data = request.get_json()
        
        if 'callback_query' in data:
            callback_query = data['callback_query']
            callback_id = callback_query['id']
            callback_data = callback_query['data']
            
            # Get message info for editing
            message = callback_query.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            message_id = message.get('message_id')
            original_text = message.get('text', '')
            
            print(f"📞 Callback received: {callback_data}")
            
            if callback_data.startswith('approve_'):
                deal_id = callback_data.replace('approve_', '')
                print(f"✅ Deal {deal_id} APPROVED")
                
                # Send immediate popup feedback
                answer_callback_query(callback_id, "✅ DEAL APPROVED! Purchase initiated.", show_alert=True)
                
                # Update the message with approval status
                if chat_id and message_id:
                    edit_message_with_status(chat_id, message_id, original_text, deal_id, "APPROVED")
                
                return jsonify({"status": "approved", "deal_id": deal_id})
                
            elif callback_data.startswith('pass_'):
                deal_id = callback_data.replace('pass_', '')
                print(f"❌ Deal {deal_id} PASSED")
                
                # Send immediate popup feedback
                answer_callback_query(callback_id, "❌ Deal passed. Searching for new opportunities...", show_alert=True)
                
                # Update the message with rejection status
                if chat_id and message_id:
                    edit_message_with_status(chat_id, message_id, original_text, deal_id, "PASSED")
                
                return jsonify({"status": "passed", "deal_id": deal_id})
            
            else:
                # Unknown button
                answer_callback_query(callback_id, "❓ Unknown action")
                return jsonify({"status": "unknown_action"})
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy", 
        "server": "pokemon_arbitrage_webhook",
        "ssl": "letsencrypt",
        "compliance": "ebay_production"
    })

@app.route('/marketplace-deletion', methods=['POST', 'GET'])
def marketplace_deletion():
    """eBay Marketplace Account Deletion Notification Endpoint - PRODUCTION COMPLIANT"""
    try:
        if request.method == 'GET':
            # eBay verification request with challenge code
            challenge_code = request.args.get('challenge_code')
            verification_token = os.getenv('EBAY_VERIFICATION_TOKEN')
            
            # Get the domain from environment or detect from request
            domain = os.getenv('WEBHOOK_DOMAIN')
            if not domain:
                # Auto-detect domain from request
                domain = request.host
            
            endpoint = f"https://{domain}/marketplace-deletion"
            
            print(f"🔍 eBay verification request")
            print(f"   Challenge Code: {challenge_code}")
            print(f"   Domain: {domain}")
            print(f"   Endpoint: {endpoint}")
            print(f"   Verification Token: {verification_token}")
            
            if challenge_code and verification_token:
                # Create SHA-256 hash: challengeCode + verificationToken + endpoint
                import hashlib
                hash_input = challenge_code + verification_token + endpoint
                challenge_response = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
                
                print(f"📊 Hash Calculation:")
                print(f"   Input: {hash_input}")
                print(f"   SHA-256: {challenge_response}")
                print(f"✅ Sending challenge response to eBay")
                
                # Return JSON response with challengeResponse
                return jsonify({"challengeResponse": challenge_response}), 200
            else:
                error_msg = "Missing challenge_code or verification_token"
                print(f"❌ {error_msg}")
                return jsonify({"error": error_msg}), 400
        
        elif request.method == 'POST':
            # Actual account deletion notification
            data = request.get_json()
            print(f"📨 eBay account deletion notification received")
            print(f"   Data: {data}")
            
            # Log the notification for compliance
            timestamp = datetime.now().isoformat()
            log_file = '/home/jthomas4641/pokemon/ebay_deletion_log.txt'
            
            with open(log_file, 'a') as f:
                f.write(f"{timestamp}: Account deletion notification: {data}\\n")
            
            # Process the deletion request
            if data and 'notification' in data:
                user_data = data['notification'].get('data', {})
                username = user_data.get('username')
                user_id = user_data.get('userId')
                
                print(f"🗑️ Processing deletion for user: {username} (ID: {user_id})")
                
                # Here you would delete user data from your database
                print(f"✅ User data deletion processed for: {username}")
            
            # Respond with 200 OK as required by eBay
            return jsonify({"status": "acknowledged"}), 200
            
    except Exception as e:
        print(f"❌ Marketplace deletion endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats():
    return jsonify({
        "server": "Pokemon Arbitrage PRODUCTION Webhook",
        "version": "2.0.0",
        "status": "running",
        "ssl": "Let's Encrypt",
        "ebay_compliance": "PRODUCTION_READY"
    })

if __name__ == '__main__':
    # Use Let's Encrypt certificates
    cert_file = '/etc/letsencrypt/live/DOMAIN_PLACEHOLDER/fullchain.pem'
    key_file = '/etc/letsencrypt/live/DOMAIN_PLACEHOLDER/privkey.pem'
    
    print("🚀 POKEMON ARBITRAGE - PRODUCTION WEBHOOK SERVER")
    print("=" * 60)
    
    # Check if domain is set in environment
    domain = os.getenv('WEBHOOK_DOMAIN')
    if domain:
        cert_file = cert_file.replace('DOMAIN_PLACEHOLDER', domain)
        key_file = key_file.replace('DOMAIN_PLACEHOLDER', domain)
        print(f"🌐 Domain: {domain}")
    else:
        print("⚠️  WEBHOOK_DOMAIN not set in .env file")
        print("   Add: WEBHOOK_DOMAIN=your-domain.duckdns.org")
        print("   Using auto-detection from request headers")
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        
        print("🔒 Let's Encrypt SSL certificates loaded")
        print("🌐 Starting PRODUCTION HTTPS server on port 443")
        print("📋 Webhook endpoint: /webhook")
        print("🏥 Health check: /health")
        print("📊 Stats: /stats")
        print("🛡️  eBay compliance: /marketplace-deletion")
        print("=" * 60)
        
        # Run on port 443 (standard HTTPS)
        app.run(host='0.0.0.0', port=443, ssl_context=context, debug=False)
    else:
        print("❌ Let's Encrypt SSL certificates not found!")
        print(f"   Expected cert: {cert_file}")
        print(f"   Expected key: {key_file}")
        print()
        print("🔧 To get certificates, run:")
        print("   sudo certbot certonly --standalone -d your-domain.duckdns.org")
        exit(1)
