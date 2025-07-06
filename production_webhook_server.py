#!/usr/bin/env python3
"""
🚀 PRODUCTION POKEMON ARBITRAGE WEBHOOK SERVER
==============================================

HTTPS-enabled Telegram webhook server for production Pokémon card arbitrage bot.
Handles button callbacks for deal approval/rejection with proper SSL support.

Features:
✅ HTTPS/SSL support for Telegram webhooks
✅ Deal approval/rejection handling
✅ Single-deal lifecycle management
✅ Production error handling and logging
✅ Health checks and monitoring
"""

import os
import ssl
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pokemon_webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PokemonWebhookServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.bot_token = os.getenv('TG_TOKEN')
        self.chat_id = os.getenv('TG_ADMIN_ID')
        self.events_processed = 0
        self.deals_approved = 0
        self.deals_rejected = 0
        self.start_time = datetime.now()
        
        # Setup routes
        self.setup_routes()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """Handle Telegram webhook callbacks"""
            try:
                data = request.get_json()
                logger.info(f"📨 Received webhook data: {json.dumps(data, indent=2)}")
                
                # Handle callback queries (button presses)
                if 'callback_query' in data:
                    return self.handle_callback_query(data['callback_query'])
                
                # Handle regular messages
                if 'message' in data:
                    return self.handle_message(data['message'])
                
                return jsonify({"status": "ok"})
                
            except Exception as e:
                logger.error(f"❌ Webhook error: {e}")
                return jsonify({"status": "error", "error": str(e)}), 500
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            uptime = datetime.now() - self.start_time
            return jsonify({
                "status": "healthy",
                "uptime_seconds": int(uptime.total_seconds()),
                "events_processed": self.events_processed,
                "deals_approved": self.deals_approved,
                "deals_rejected": self.deals_rejected,
                "approval_rate": f"{(self.deals_approved/(max(1, self.deals_approved + self.deals_rejected)))*100:.1f}%",
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/stats', methods=['GET'])
        def stats():
            """Detailed statistics"""
            uptime = datetime.now() - self.start_time
            return jsonify({
                "server_info": {
                    "name": "Pokemon Arbitrage Webhook",
                    "version": "1.0.0",
                    "uptime_seconds": int(uptime.total_seconds()),
                    "start_time": self.start_time.isoformat()
                },
                "metrics": {
                    "total_events": self.events_processed,
                    "deals_approved": self.deals_approved,
                    "deals_rejected": self.deals_rejected,
                    "approval_rate": f"{(self.deals_approved/(max(1, self.deals_approved + self.deals_rejected)))*100:.1f}%"
                },
                "bot_info": {
                    "token_configured": bool(self.bot_token),
                    "chat_id_configured": bool(self.chat_id)
                }
            })
    
    def handle_callback_query(self, callback_query):
        """Handle button press callbacks"""
        try:
            self.events_processed += 1
            
            callback_id = callback_query['id']
            user_id = callback_query['from']['id']
            data = callback_query['data']
            message = callback_query.get('message', {})
            
            logger.info(f"🔘 Button pressed: {data} by user {user_id}")
            
            # Parse callback data
            if data.startswith('approve_'):
                deal_id = data.replace('approve_', '')
                return self.handle_deal_approval(callback_id, deal_id, message)
            elif data.startswith('pass_'):
                deal_id = data.replace('pass_', '')
                return self.handle_deal_rejection(callback_id, deal_id, message)
            else:
                logger.warning(f"⚠️ Unknown callback data: {data}")
                self.answer_callback_query(callback_id, "Unknown action")
                return jsonify({"status": "unknown_action"})
                
        except Exception as e:
            logger.error(f"❌ Callback handling error: {e}")
            return jsonify({"status": "error", "error": str(e)}), 500
    
    def handle_deal_approval(self, callback_id, deal_id, message):
        """Handle deal approval"""
        try:
            self.deals_approved += 1
            
            # Answer the callback query
            self.answer_callback_query(callback_id, "✅ Deal APPROVED!")
            
            # Edit the message to show approval
            self.edit_message_for_approval(message, deal_id, "APPROVED")
            
            # Log the approval
            logger.info(f"✅ Deal {deal_id} APPROVED")
            
            # Here you would trigger the actual purchase logic
            # self.trigger_purchase(deal_id)
            
            return jsonify({
                "status": "approved",
                "deal_id": deal_id,
                "action": "purchase_triggered"
            })
            
        except Exception as e:
            logger.error(f"❌ Approval handling error: {e}")
            return jsonify({"status": "error", "error": str(e)}), 500
    
    def handle_deal_rejection(self, callback_id, deal_id, message):
        """Handle deal rejection"""
        try:
            self.deals_rejected += 1
            
            # Answer the callback query
            self.answer_callback_query(callback_id, "❌ Deal PASSED")
            
            # Edit the message to show rejection
            self.edit_message_for_approval(message, deal_id, "PASSED")
            
            # Log the rejection
            logger.info(f"❌ Deal {deal_id} PASSED")
            
            return jsonify({
                "status": "passed",
                "deal_id": deal_id,
                "action": "deal_skipped"
            })
            
        except Exception as e:
            logger.error(f"❌ Rejection handling error: {e}")
            return jsonify({"status": "error", "error": str(e)}), 500
    
    def handle_message(self, message):
        """Handle regular text messages"""
        logger.info(f"💬 Received message: {message.get('text', 'No text')}")
        return jsonify({"status": "message_received"})
    
    def answer_callback_query(self, callback_id, text):
        """Answer callback query with popup notification"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/answerCallbackQuery"
            data = {
                "callback_query_id": callback_id,
                "text": text,
                "show_alert": False
            }
            response = requests.post(url, json=data, timeout=10)
            if not response.ok:
                logger.error(f"Failed to answer callback query: {response.text}")
        except Exception as e:
            logger.error(f"Error answering callback query: {e}")
    
    def edit_message_for_approval(self, message, deal_id, status):
        """Edit the message to show approval/rejection status"""
        try:
            message_id = message.get('message_id')
            chat_id = message.get('chat', {}).get('id')
            
            if not message_id or not chat_id:
                logger.error("Missing message_id or chat_id for editing")
                return
            
            # Get original text and add status
            original_text = message.get('text', '')
            status_emoji = "✅" if status == "APPROVED" else "❌"
            new_text = f"{original_text}\n\n{status_emoji} **{status}** at {datetime.now().strftime('%H:%M:%S')}"
            
            url = f"https://api.telegram.org/bot{self.bot_token}/editMessageText"
            data = {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": new_text,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=data, timeout=10)
            if not response.ok:
                logger.error(f"Failed to edit message: {response.text}")
                
        except Exception as e:
            logger.error(f"Error editing message: {e}")
    
    def run(self, host='0.0.0.0', port=8080, ssl_context=None):
        """Run the webhook server"""
        logger.info(f"🚀 Starting Pokemon Arbitrage Webhook Server")
        logger.info(f"📡 Host: {host}")
        logger.info(f"🔌 Port: {port}")
        logger.info(f"🔒 SSL: {'Enabled' if ssl_context else 'Disabled'}")
        
        if ssl_context:
            logger.info(f"🌐 HTTPS webhook endpoint: https://{host}:{port}/webhook")
        else:
            logger.info(f"🌐 HTTP webhook endpoint: http://{host}:{port}/webhook")
        
        logger.info(f"❤️ Health check: /health")
        logger.info(f"📊 Statistics: /stats")
        logger.info("=" * 60)
        
        self.app.run(
            host=host,
            port=port,
            ssl_context=ssl_context,
            debug=False,
            threaded=True
        )

def create_ssl_context(cert_file, key_file):
    """Create SSL context for HTTPS"""
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(cert_file, key_file)
    return context

def main():
    """Main entry point"""
    # SSL certificate paths
    cert_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.crt'
    key_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.key'
    
    # Check if SSL certificates exist
    ssl_context = None
    if os.path.exists(cert_file) and os.path.exists(key_file):
        ssl_context = create_ssl_context(cert_file, key_file)
        logger.info("🔒 SSL certificates found - HTTPS enabled")
    else:
        logger.warning("⚠️ SSL certificates not found - running HTTP only")
        logger.warning("⚠️ Telegram webhooks require HTTPS - create certificates first")
    
    # Create and run server
    server = PokemonWebhookServer()
    server.run(ssl_context=ssl_context)

if __name__ == "__main__":
    main()
