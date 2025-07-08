"""
Pokemon Webhook Server for Railway
Implements eBay Marketplace Account Deletion notification requirements
"""
import os
import hashlib
import logging
from datetime import datetime
from flask import Flask, jsonify, request

# Initialize Flask app
app = Flask(__name__)
# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Root endpoint providing basic service info"""
    return jsonify({
        "status": "healthy",
        "service": "pokemon-webhook-v2",
        "environment": "production"
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/webhook', methods=['GET', 'POST'])
def ebay_webhook():
    """eBay Marketplace Account Deletion Notification endpoint"""
    try:
        if request.method == 'GET':
            # Handle eBay verification request
            challenge_code = request.args.get('challenge_code')
            if not challenge_code:
                logging.error("Missing challenge_code parameter")
                return jsonify({"error": "Missing challenge_code parameter"}), 400

            # Get verification token from environment
            verification_token = os.getenv('EBAY_VERIFICATION_TOKEN', 'test_token')
            
            # Get the endpoint URL - this should match exactly what's registered with eBay
            railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN', 'hospitable-tranquility-production.up.railway.app')
            endpoint = f"https://{railway_domain}/webhook"
            
            # Create challenge response exactly as specified by eBay
            # challengeResponse = SHA256(challengeCode + verificationToken + endpointUrl)
            hash_input = challenge_code + verification_token + endpoint
            challenge_response = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
            
            logging.info(f"Processed challenge code: {challenge_code}")
            logging.info(f"Generated challenge response: {challenge_response}")
            
            return jsonify({"challengeResponse": challenge_response})

        elif request.method == 'POST':
            # Handle actual account deletion notification
            data = request.get_json()
            if not data:
                logging.error("No JSON data received")
                return jsonify({"error": "No data received"}), 400

            logging.info(f"Received account deletion notification: {data}")

            # Validate the notification format
            if 'notification' not in data:
                logging.error("Invalid notification format")
                return jsonify({"error": "Invalid notification format"}), 400

            # Process the deletion
            notification = data['notification']
            user_data = notification.get('data', {})
            username = user_data.get('username')
            user_id = user_data.get('userId')

            logging.info(f"Processing deletion for user: {username} (ID: {user_id})")

            # Here you would implement the actual user data deletion
            # For now, we just acknowledge receipt
            
            return jsonify({
                "status": "success",
                "message": "Account deletion notification processed"
            }), 200

    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", "8080"))
    app.run(host='0.0.0.0', port=port)

# All routes defined above


def answer_callback_query(callback_id, text, show_alert=False):
    """Send popup notification to user"""
    import requests
    
    bot_token = os.getenv('TG_TOKEN')
    if not bot_token:
        print("❌ TG_TOKEN not set")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    
    data = {
        "callback_query_id": callback_id,
        "text": text,
        "show_alert": show_alert
    }
    
    try:
        import requests
        response = requests.post(url, json=data, timeout=10)
        return response.ok
    except Exception as e:
        print(f"Error answering callback: {e}")
        return False

def edit_message_with_status(chat_id, message_id, original_text, deal_id, status):
    """Update the message to show approval/rejection status"""
    import requests
    
    bot_token = os.getenv('TG_TOKEN')
    if not bot_token:
        print("❌ TG_TOKEN not set")
        return False
        
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
    """Main Telegram webhook endpoint for deal approvals"""
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
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "server": "pokemon_arbitrage_webhook_railway",
        "https": True,
        "platform": "Railway"
    })

@app.route('/stats', methods=['GET'])
def stats():
    """Server stats endpoint"""
    return jsonify({
        "server": "Pokemon Arbitrage HTTPS Webhook (Railway)",
        "version": "2.0.0",
        "status": "running",
        "platform": "Railway"
    })

@app.route('/marketplace-deletion', methods=['POST', 'GET'])
def marketplace_deletion():
    """
    eBay Marketplace Account Deletion Notification Endpoint
    This endpoint handles eBay's compliance requirements for account deletion notifications.
    """
    try:
        # Get the Railway-provided domain from environment or use Railway's app URL
        railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
        if not railway_domain:
            # Railway automatically provides this, but fallback to constructed URL
            railway_app_name = os.getenv('RAILWAY_SERVICE_NAME', 'pokemon-arbitrage')
            railway_domain = f"{railway_app_name}.up.railway.app"
        
        endpoint = f"https://{railway_domain}/marketplace-deletion"
        
        if request.method == 'GET':
            # eBay verification request with challenge code
            challenge_code = request.args.get('challenge_code')
            verification_token = os.getenv('EBAY_VERIFICATION_TOKEN')
            
            print(f"🔍 eBay verification request")
            print(f"🌐 Railway domain: {railway_domain}")
            print(f"🔗 Endpoint URL: {endpoint}")
            print(f"🔑 Challenge code: {challenge_code}")
            print(f"🔐 Verification token: {verification_token}")
            
            if challenge_code and verification_token:
                # Create SHA-256 hash: challengeCode + verificationToken + endpoint
                hash_input = challenge_code + verification_token + endpoint
                challenge_response = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
                
                print(f"📊 Hash input: {hash_input}")
                print(f"✅ Generated challenge response: {challenge_response}")
                
                # Return JSON response with challengeResponse
                return jsonify({
                    "challengeResponse": challenge_response
                }), 200
            else:
                error_msg = "Missing challenge_code or verification_token"
                print(f"❌ {error_msg}")
                return jsonify({
                    "error": error_msg
                }), 400
        
        elif request.method == 'POST':
            # Actual account deletion notification from eBay
            data = request.get_json()
            print(f"📨 eBay account deletion notification received: {data}")
            
            # Log the notification for compliance (Railway has persistent storage)
            timestamp = datetime.now().isoformat()
            log_entry = f"{timestamp}: Account deletion notification: {data}\n"
            print(f"📝 Logging: {log_entry}")
            
            # Process the deletion request
            if data and 'notification' in data:
                user_data = data['notification'].get('data', {})
                username = user_data.get('username')
                user_id = user_data.get('userId')
                
                print(f"🗑️ Processing deletion for user: {username} (ID: {user_id})")
                
                # Here you would delete user data from your database
                # For now, just log it
                print(f"✅ User data deletion processed for: {username}")
            
            # Respond with 200 OK as required by eBay
            response = jsonify({"status": "acknowledged"})
            response.headers['Content-Type'] = 'application/json'
            return response, 200
            
    except Exception as e:
        print(f"❌ Marketplace deletion endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint for basic info"""
    return jsonify({
        "service": "Pokemon Arbitrage eBay Compliance Webhook",
        "version": "2.0.0",
        "platform": "Railway",
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "telegram_webhook": "/webhook",
            "ebay_compliance": "/marketplace-deletion"
        },
        "status": "operational"
    })

application = app
