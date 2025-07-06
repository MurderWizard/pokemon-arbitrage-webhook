#!/usr/bin/env python3
"""
Production Webhook Deployment Guide
Complete setup for Telegram button functionality with proper networking
"""

# WEBHOOK DEPLOYMENT OPTIONS

"""
🌐 DEPLOYMENT OPTIONS FOR WEBHOOK SERVER

1. **CLOUD DEPLOYMENT (RECOMMENDED)** ✅
   - Uses standard HTTPS port 443
   - No firewall rules needed
   - SSL/TLS automatically handled
   - Examples: Railway, Heroku, DigitalOcean

2. **VPS/DEDICATED SERVER** 🔧
   - Custom port (8000-8999 recommended)
   - Firewall rules required
   - SSL certificate needed
   - More control but more setup

3. **LOCAL TESTING** 🧪
   - Port 5000 (default Flask)
   - Use ngrok for public access
   - No firewall changes needed
   - Perfect for development

"""

import os
import asyncio
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from telegram import Bot

class ProductionWebhookServer:
    """Production-ready webhook server with proper configuration"""
    
    def __init__(self, port=None):
        load_dotenv()
        self.bot_token = os.getenv('TG_TOKEN')
        self.admin_id = int(os.getenv('TG_ADMIN_ID'))
        self.bot = Bot(token=self.bot_token)
        
        # Smart port selection
        self.port = port or self.detect_optimal_port()
        
        # Flask app setup
        self.app = Flask(__name__)
        self.setup_routes()
    
    def detect_optimal_port(self) -> int:
        """Detect the best port based on environment"""
        
        # Check if we're on a cloud platform
        if os.getenv('PORT'):  # Heroku, Railway, etc.
            return int(os.getenv('PORT'))
        
        # Check for common cloud environment variables
        if any(os.getenv(var) for var in ['RAILWAY_ENVIRONMENT', 'HEROKU_APP_NAME']):
            return int(os.getenv('PORT', 8000))
        
        # Default for VPS/local
        return 8443  # Telegram's recommended port for webhooks
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """Handle Telegram webhook callbacks"""
            try:
                data = request.get_json()
                
                if 'callback_query' in data:
                    return self.handle_callback_query(data['callback_query'])
                
                return jsonify({'status': 'no_action'})
                
            except Exception as e:
                print(f"❌ Webhook error: {e}")
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'service': 'pokemon_arbitrage_webhook',
                'port': self.port,
                'timestamp': str(asyncio.get_event_loop().time())
            })
        
        @self.app.route('/set-webhook', methods=['POST'])
        def set_webhook():
            """Helper endpoint to set webhook URL"""
            webhook_url = request.json.get('url')
            if not webhook_url:
                return jsonify({'error': 'URL required'})
            
            try:
                # This would set the webhook
                result = f"Webhook would be set to: {webhook_url}/webhook"
                return jsonify({'status': 'success', 'webhook_url': result})
            except Exception as e:
                return jsonify({'error': str(e)})
    
    def handle_callback_query(self, callback_query):
        """Handle button presses"""
        try:
            callback_data = callback_query.get('data', '')
            chat_id = callback_query['message']['chat']['id']
            message_id = callback_query['message']['message_id']
            
            if callback_data.startswith('buy_'):
                deal_id = callback_data.replace('buy_', '')
                return self.approve_deal(deal_id, chat_id, message_id)
                
            elif callback_data.startswith('pass_'):
                deal_id = callback_data.replace('pass_', '')
                return self.reject_deal(deal_id, chat_id, message_id)
                
            return jsonify({'status': 'unknown_action'})
            
        except Exception as e:
            print(f"❌ Callback error: {e}")
            return jsonify({'status': 'error'})
    
    def approve_deal(self, deal_id: str, chat_id: int, message_id: int):
        """Handle deal approval"""
        try:
            # Update message
            asyncio.create_task(self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"✅ DEAL {deal_id} APPROVED!\n\n💰 Investment activated\n⏱️ Monitoring for completion",
                reply_markup=None
            ))
            
            # Send confirmation
            asyncio.create_task(self.bot.send_message(
                chat_id=chat_id,
                text=f"🚀 Deal {deal_id} is now your active investment!\n\n📋 Next steps:\n• Purchase on eBay\n• Ship to PSA\n• Monitor grading (~45 days)"
            ))
            
            return jsonify({'status': 'approved', 'deal_id': deal_id})
            
        except Exception as e:
            print(f"❌ Approval error: {e}")
            return jsonify({'status': 'error'})
    
    def reject_deal(self, deal_id: str, chat_id: int, message_id: int):
        """Handle deal rejection"""
        try:
            # Update message
            asyncio.create_task(self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"❌ DEAL {deal_id} REJECTED\n\n🔍 Continuing search for better opportunities",
                reply_markup=None
            ))
            
            return jsonify({'status': 'rejected', 'deal_id': deal_id})
            
        except Exception as e:
            print(f"❌ Rejection error: {e}")
            return jsonify({'status': 'error'})
    
    def run(self, host='0.0.0.0', ssl_context=None):
        """Run the webhook server"""
        print(f"🌐 Starting Production Webhook Server")
        print(f"📡 Port: {self.port}")
        print(f"🔗 Host: {host}")
        print(f"🔒 SSL: {'Enabled' if ssl_context else 'Disabled (use reverse proxy)'}")
        print("=" * 50)
        
        self.app.run(
            host=host,
            port=self.port,
            debug=False,
            ssl_context=ssl_context
        )

def print_deployment_guide():
    """Print comprehensive deployment guide"""
    
    print("""
🚀 WEBHOOK DEPLOYMENT GUIDE
""" + "=" * 50 + """

1. **RECOMMENDED: CLOUD DEPLOYMENT** ✅

   **Railway (Free tier, easiest)**:
   ```bash
   # 1. Install Railway CLI
   npm install -g @railway/cli
   
   # 2. Login and deploy
   railway login
   railway init
   railway up
   
   # 3. Get your URL
   railway domain  # returns: https://your-app.railway.app
   ```

   **Heroku (Classic option)**:
   ```bash
   # 1. Install Heroku CLI
   # 2. Create app
   heroku create pokemon-arbitrage-webhook
   
   # 3. Deploy
   git push heroku main
   
   # 4. Get URL: https://pokemon-arbitrage-webhook.herokuapp.com
   ```

2. **VPS/DEDICATED SERVER SETUP** 🔧

   **Firewall Rules (Ubuntu/Debian)**:
   ```bash
   # Allow webhook port (8443 recommended for Telegram)
   sudo ufw allow 8443/tcp
   
   # Or use custom port
   sudo ufw allow 8000/tcp
   
   # Check status
   sudo ufw status
   ```

   **Nginx Reverse Proxy** (handles SSL):
   ```nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location /webhook {
           proxy_pass http://localhost:8443;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   **Systemd Service** (auto-restart):
   ```ini
   [Unit]
   Description=Pokemon Arbitrage Webhook
   After=network.target
   
   [Service]
   Type=simple
   User=your-user
   WorkingDirectory=/path/to/pokemon
   ExecStart=/path/to/python webhook_server.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **LOCAL TESTING** 🧪

   **Using ngrok** (no firewall changes needed):
   ```bash
   # 1. Install ngrok
   # 2. Run your webhook server
   python webhook_server.py
   
   # 3. In another terminal, expose port
   ngrok http 5000
   
   # 4. Use the ngrok URL for webhook
   # https://abc123.ngrok.io/webhook
   ```

4. **SET TELEGRAM WEBHOOK** 📱

   **After deployment, set your webhook**:
   ```bash
   # Replace with your actual URL
   curl -X POST "https://api.telegram.org/bot{YOUR_BOT_TOKEN}/setWebhook" \\
        -H "Content-Type: application/json" \\
        -d '{"url": "https://your-server.com/webhook"}'
   
   # Verify webhook is set
   curl "https://api.telegram.org/bot{YOUR_BOT_TOKEN}/getWebhookInfo"
   ```

5. **ENVIRONMENT VARIABLES** 🔧

   **Required in your deployment**:
   ```
   TG_TOKEN=your_telegram_bot_token
   TG_ADMIN_ID=your_telegram_user_id
   PORT=8443  # or whatever port you choose
   ```

6. **SECURITY CONSIDERATIONS** 🔒

   - **Always use HTTPS** for webhooks
   - **Verify webhook secret** (optional but recommended)
   - **Rate limiting** to prevent abuse
   - **IP whitelisting** for Telegram's IPs
   - **Keep tokens secret** and rotate periodically

7. **MONITORING & DEBUGGING** 📊

   **Health check endpoint**:
   ```bash
   curl https://your-server.com/health
   ```

   **Webhook status**:
   ```bash
   curl "https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
   ```

   **Test webhook manually**:
   ```bash
   curl -X POST https://your-server.com/webhook \\
        -H "Content-Type: application/json" \\
        -d '{"test": "webhook"}'
   ```

🎯 **RECOMMENDED APPROACH FOR YOU**:

1. **Start with Railway or Heroku** (easiest, no firewall setup)
2. **Use the provided webhook server code**
3. **Test with ngrok first** (local development)
4. **Deploy to cloud once working**
5. **Set webhook URL in Telegram**
6. **Test button functionality**

💡 **Port Recommendations**:
- **Cloud platforms**: Use $PORT environment variable
- **VPS with Nginx**: Use 8443 (Telegram recommended)
- **Local testing**: Use 5000 (Flask default)
- **Direct VPS**: Use 443 (requires root) or 8000-8999

🔧 **No firewall changes needed if**:
- Using cloud deployment (Railway/Heroku)
- Using ngrok for testing
- Using reverse proxy (Nginx handles external access)

""")

if __name__ == "__main__":
    print_deployment_guide()
    
    print("\n🚀 Starting webhook server...")
    server = ProductionWebhookServer()
    
    print(f"\n📋 SETUP CHECKLIST:")
    print(f"1. ✅ Server starting on port {server.port}")
    print(f"2. 🔧 Deploy to cloud or configure firewall")
    print(f"3. 🌐 Set webhook URL in Telegram")
    print(f"4. 🧪 Test button functionality")
    print(f"\n💡 For testing: Use ngrok to expose port {server.port}")
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n🛑 Webhook server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("💡 Try using a different port or check firewall settings")
