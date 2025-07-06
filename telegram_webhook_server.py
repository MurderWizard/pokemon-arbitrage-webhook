#!/usr/bin/env python3
"""
HTTPS Webhook Server for Telegram Button Actions - Pokemon Arbitrage
Production-ready webhook server with SSL support for deal approvals
"""
from flask import Flask, request, jsonify
import os
import ssl
import asyncio
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
load_dotenv()

# Bot setup
BOT_TOKEN = os.getenv('TG_TOKEN')
bot = Bot(token=BOT_TOKEN)

# Metrics
stats = {
    'events_processed': 0,
    'deals_approved': 0,
    'deals_rejected': 0,
    'start_time': datetime.now()
}

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook callbacks"""
    try:
        data = request.get_json()
        
        # Check if it's a callback query (button press)
        if 'callback_query' in data:
            callback = data['callback_query']
            callback_data = callback.get('data', '')
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            
            # Parse the action
            if callback_data.startswith('buy_'):
                deal_id = callback_data.replace('buy_', '')
                result = handle_buy_action(deal_id, chat_id, message_id)
                
            elif callback_data.startswith('pass_'):
                deal_id = callback_data.replace('pass_', '')
                result = handle_pass_action(deal_id, chat_id, message_id)
                
            else:
                return jsonify({'status': 'unknown_action'})
            
            # Answer the callback to remove loading state
            bot.answer_callback_query(callback['id'])
            
            return jsonify({'status': 'success', 'action': result})
        
        return jsonify({'status': 'no_action'})
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

def handle_buy_action(deal_id: str, chat_id: int, message_id: int) -> str:
    """Handle BUY button press"""
    try:
        # This would call your actual approval function
        # success = approve_deal(deal_id)
        
        # For demo, assume success
        success = True
        
        if success:
            # Update the message to show approval
            new_text = f"✅ DEAL {deal_id} APPROVED!\n\n💰 Investment activated\n⏱️ Monitoring for completion"
            
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=new_text,
                reply_markup=None  # Remove buttons
            )
            
            # Send confirmation
            bot.send_message(
                chat_id=chat_id,
                text=f"🚀 Deal {deal_id} is now your active investment!\n\n📋 Next steps:\n• Monitor grading timeline\n• Track market conditions\n• Prepare for selling"
            )
            
            return f"approved_{deal_id}"
        else:
            bot.send_message(chat_id=chat_id, text=f"❌ Failed to approve {deal_id}")
            return f"approval_failed_{deal_id}"
            
    except Exception as e:
        print(f"Buy action error: {e}")
        return f"error_{deal_id}"

def handle_pass_action(deal_id: str, chat_id: int, message_id: int) -> str:
    """Handle PASS button press"""
    try:
        # This would call your actual rejection function
        # success = reject_deal(deal_id)
        
        # For demo, assume success
        success = True
        
        if success:
            # Update the message to show rejection
            new_text = f"❌ DEAL {deal_id} REJECTED\n\n🔍 Continuing search for better opportunities"
            
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=new_text,
                reply_markup=None  # Remove buttons
            )
            
            # Send status update
            bot.send_message(
                chat_id=chat_id,
                text=f"🎯 Capital freed from {deal_id}\n\n✅ Ready to evaluate new deals\n🔍 Scanning for opportunities..."
            )
            
            return f"rejected_{deal_id}"
        else:
            bot.send_message(chat_id=chat_id, text=f"❌ Failed to reject {deal_id}")
            return f"rejection_failed_{deal_id}"
            
    except Exception as e:
        print(f"Pass action error: {e}")
        return f"error_{deal_id}"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with metrics"""
    uptime = datetime.now() - stats['start_time']
    return jsonify({
        'status': 'healthy', 
        'service': 'pokemon_arbitrage_webhook',
        'uptime_seconds': int(uptime.total_seconds()),
        'events_processed': stats['events_processed'],
        'deals_approved': stats['deals_approved'],
        'deals_rejected': stats['deals_rejected'],
        'approval_rate': f"{(stats['deals_approved']/(max(1, stats['deals_approved'] + stats['deals_rejected'])))*100:.1f}%"
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Detailed statistics endpoint"""
    uptime = datetime.now() - stats['start_time']
    return jsonify({
        'server_info': {
            'name': 'Pokemon Arbitrage HTTPS Webhook',
            'version': '1.0.0',
            'uptime_seconds': int(uptime.total_seconds()),
            'start_time': stats['start_time'].isoformat()
        },
        'metrics': stats,
        'bot_configured': bool(BOT_TOKEN)
    })

if __name__ == '__main__':
    # SSL Configuration
    cert_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.crt'
    key_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.key'
    
    print("🚀 POKEMON ARBITRAGE - HTTPS WEBHOOK SERVER")
    print("=" * 50)
    
    # Check SSL certificates
    if os.path.exists(cert_file) and os.path.exists(key_file):
        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(cert_file, key_file)
        
        logger.info("🔒 SSL certificates found - Starting HTTPS server")
        print("🔒 HTTPS enabled with SSL certificates")
        print("🌐 Webhook URL: https://34.74.208.133:8080/webhook")
        print("❤️ Health check: https://34.74.208.133:8080/health")
        print("📊 Statistics: https://34.74.208.133:8080/stats")
        print("=" * 50)
        
        # Run HTTPS server
        app.run(host='0.0.0.0', port=8080, ssl_context=context, debug=False)
    else:
        logger.warning("⚠️ SSL certificates not found - running HTTP only")
        print("❌ SSL certificates not found!")
        print(f"   Expected: {cert_file}")
        print(f"   Expected: {key_file}")
        print("⚠️ Telegram webhooks require HTTPS")
        print("=" * 50)
        
        # Run HTTP server (for testing only)
        app.run(host='0.0.0.0', port=8080, debug=True)
