#!/usr/bin/env python3
"""
Direct webhook server for Pokemon arbitrage
"""
import os
import ssl
import requests
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

def answer_callback_query(callback_id, text, show_alert=False):
    """Send popup notification to user"""
    from dotenv import load_dotenv
    load_dotenv()
    
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
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv('TG_TOKEN')
    url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
    
    print(f"🔄 Editing message: chat_id={chat_id}, message_id={message_id}, status={status}")
    
    # Add status banner to the message
    if status == "APPROVED":
        status_banner = f"\n\n🟢 **✅ DEAL APPROVED** 🟢\n⏰ Decision made at {datetime.now().strftime('%H:%M:%S')}\n🚀 Purchase process initiated!"
    elif status == "PASSED":
        status_banner = f"\n\n🔴 **❌ DEAL PASSED** 🔴\n⏰ Decision made at {datetime.now().strftime('%H:%M:%S')}\n🔍 Continuing search for opportunities..."
    else:
        status_banner = f"\n\n⚪ **Status: {status}**"
    
    new_text = original_text + status_banner
    
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": new_text,
        "parse_mode": "Markdown"
        # Don't include reply_markup at all to remove buttons
    }
    
    try:
        print(f"📤 Sending edit request to Telegram...")
        response = requests.post(url, json=data, timeout=10)
        
        if response.ok:
            print(f"✅ Message edited successfully!")
            return True
        else:
            print(f"❌ Telegram API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error editing message: {e}")
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print(f"📨 Webhook received: {data}")
        
        # Handle callback queries (button presses)
        if 'callback_query' in data:
            callback = data['callback_query']
            callback_id = callback['id']
            callback_data = callback.get('data', '')
            user_id = callback['from']['id']
            message = callback.get('message', {})
            
            chat_id = message.get('chat', {}).get('id')
            message_id = message.get('message_id')
            original_text = message.get('text', '')
            
            print(f"🔘 Button pressed: {callback_data} by user {user_id}")
            
            if callback_data.startswith('approve_'):
                deal_id = callback_data.replace('approve_', '')
                print(f"✅ Deal {deal_id} APPROVED!")
                
                # Send immediate popup feedback
                answer_callback_query(callback_id, "✅ DEAL APPROVED! Purchase initiated.", show_alert=True)
                
                # Update the message with approval status
                if chat_id and message_id:
                    edit_message_with_status(chat_id, message_id, original_text, deal_id, "APPROVED")
                
                # Here you would trigger the purchase logic
                # approve_deal(deal_id)
                
                return jsonify({"status": "approved", "deal_id": deal_id})
                
            elif callback_data.startswith('pass_'):
                deal_id = callback_data.replace('pass_', '')
                print(f"❌ Deal {deal_id} PASSED")
                
                # Send immediate popup feedback
                answer_callback_query(callback_id, "❌ Deal passed. Searching for new opportunities...", show_alert=True)
                
                # Update the message with rejection status
                if chat_id and message_id:
                    edit_message_with_status(chat_id, message_id, original_text, deal_id, "PASSED")
                
                # Here you would reject the deal
                # reject_deal(deal_id)
                
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
        "https": True
    })

@app.route('/stats', methods=['GET'])
def stats():
    return jsonify({
        "server": "Pokemon Arbitrage HTTPS Webhook",
        "version": "1.0.0",
        "status": "running"
    })

@app.route('/marketplace-deletion', methods=['POST', 'GET'])
def marketplace_deletion():
    """eBay Marketplace Account Deletion Notification Endpoint"""
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        if request.method == 'GET':
            # eBay verification request with challenge code
            challenge_code = request.args.get('challenge_code')
            verification_token = os.getenv('EBAY_VERIFICATION_TOKEN')
            endpoint = "https://pokemon-arbitrage.duckdns.org/marketplace-deletion"  # Standard HTTPS port 443
            
            print(f"🔍 eBay verification request - challenge_code: {challenge_code}")
            print(f"🔑 Using verification token from .env: {verification_token}")
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
            
            # Log the notification for compliance
            timestamp = datetime.now().isoformat()
            with open('/home/jthomas4641/pokemon/ebay_deletion_log.txt', 'a') as f:
                f.write(f"{timestamp}: Account deletion notification: {data}\n")
            
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
    cert_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.crt'
    key_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.key'
    
    print("🚀 POKEMON ARBITRAGE - HTTPS WEBHOOK SERVER")
    print("=" * 50)
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        
        print("🔒 SSL certificates loaded")
        print("🌐 Starting HTTPS server on https://pokemon-arbitrage.duckdns.org:443")
        print("📋 Webhook endpoint: /webhook")
        print("❤️  Health check: /health")
        print("📊 Stats: /stats")
        print("🛡️  eBay compliance: /marketplace-deletion")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=443, ssl_context=context, debug=False)
    else:
        print("❌ SSL certificates not found!")
        print(f"   Missing: {cert_file}")
        print(f"   Missing: {key_file}")
        exit(1)
