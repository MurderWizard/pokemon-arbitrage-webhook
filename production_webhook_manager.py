#!/usr/bin/env python3
"""
🔧 PRODUCTION WEBHOOK MANAGER - POKEMON ARBITRAGE
================================================

Manages Telegram webhook configuration for the production Pokemon arbitrage system.
Sets up HTTPS webhook with SSL certificate support.

Features:
✅ HTTPS webhook setup with SSL certificates
✅ Webhook status checking
✅ Certificate upload to Telegram
✅ Production-ready configuration
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ProductionWebhookManager:
    def __init__(self):
        self.bot_token = os.getenv('TG_TOKEN')
        self.external_ip = "34.74.208.133"  # Your VM's external IP
        self.webhook_port = 8080
        self.cert_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.crt'
        
        if not self.bot_token:
            raise ValueError("TG_TOKEN not found in environment variables")
    
    def set_webhook_with_cert(self):
        """Set webhook with SSL certificate"""
        try:
            webhook_url = f"https://{self.external_ip}:{self.webhook_port}/webhook"
            
            print(f"🔒 Setting HTTPS webhook: {webhook_url}")
            print(f"📋 Using certificate: {self.cert_file}")
            
            # Check if certificate exists
            if not os.path.exists(self.cert_file):
                print(f"❌ Certificate file not found: {self.cert_file}")
                return False
            
            # Prepare the request
            url = f"https://api.telegram.org/bot{self.bot_token}/setWebhook"
            
            with open(self.cert_file, 'rb') as cert:
                files = {'certificate': cert}
                data = {
                    'url': webhook_url,
                    'max_connections': 40,
                    'allowed_updates': ['message', 'callback_query']
                }
                
                response = requests.post(url, data=data, files=files, timeout=30)
            
            if response.ok:
                result = response.json()
                if result.get('ok'):
                    print("✅ Webhook set successfully with SSL certificate!")
                    print(f"📝 Response: {json.dumps(result, indent=2)}")
                    return True
                else:
                    print(f"❌ Telegram API error: {result.get('description', 'Unknown error')}")
                    return False
            else:
                print(f"❌ HTTP error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error setting webhook: {e}")
            return False
    
    def check_webhook_status(self):
        """Check current webhook status"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getWebhookInfo"
            response = requests.get(url, timeout=10)
            
            if response.ok:
                result = response.json()
                if result.get('ok'):
                    webhook_info = result.get('result', {})
                    print("📊 Current Webhook Status:")
                    print(f"   URL: {webhook_info.get('url', 'Not set')}")
                    print(f"   Has Custom Certificate: {webhook_info.get('has_custom_certificate', False)}")
                    print(f"   Pending Updates: {webhook_info.get('pending_update_count', 0)}")
                    print(f"   Max Connections: {webhook_info.get('max_connections', 'Not set')}")
                    print(f"   Allowed Updates: {webhook_info.get('allowed_updates', 'All')}")
                    
                    last_error = webhook_info.get('last_error_message')
                    if last_error:
                        print(f"   ⚠️ Last Error: {last_error}")
                        print(f"   🕒 Error Date: {webhook_info.get('last_error_date', 'Unknown')}")
                    
                    return webhook_info
                else:
                    print(f"❌ API error: {result.get('description', 'Unknown error')}")
                    return None
            else:
                print(f"❌ HTTP error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error checking webhook: {e}")
            return None
    
    def remove_webhook(self):
        """Remove the current webhook"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/deleteWebhook"
            response = requests.post(url, timeout=10)
            
            if response.ok:
                result = response.json()
                if result.get('ok'):
                    print("✅ Webhook removed successfully!")
                    return True
                else:
                    print(f"❌ Error removing webhook: {result.get('description', 'Unknown error')}")
                    return False
            else:
                print(f"❌ HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error removing webhook: {e}")
            return False
    
    def test_webhook_connectivity(self):
        """Test if the webhook server is reachable"""
        try:
            webhook_url = f"https://{self.external_ip}:{self.webhook_port}/health"
            print(f"🔍 Testing webhook server connectivity: {webhook_url}")
            
            response = requests.get(webhook_url, timeout=10, verify=False)  # verify=False for self-signed cert
            
            if response.ok:
                result = response.json()
                print("✅ Webhook server is reachable!")
                print(f"📊 Server status: {json.dumps(result, indent=2)}")
                return True
            else:
                print(f"❌ Server responded with error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Cannot reach webhook server: {e}")
            print("💡 Make sure the production webhook server is running")
            return False

def main():
    """Main interface"""
    try:
        manager = ProductionWebhookManager()
        
        print("🚀 POKEMON ARBITRAGE - PRODUCTION WEBHOOK MANAGER")
        print("=" * 55)
        
        while True:
            print("\nChoose an action:")
            print("1. 🔒 Set HTTPS webhook with SSL certificate")
            print("2. 📊 Check webhook status")
            print("3. 🧪 Test webhook server connectivity")
            print("4. ❌ Remove webhook")
            print("5. 🚪 Exit")
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == '1':
                print("\n🔒 Setting up HTTPS webhook...")
                manager.set_webhook_with_cert()
            elif choice == '2':
                print("\n📊 Checking webhook status...")
                manager.check_webhook_status()
            elif choice == '3':
                print("\n🧪 Testing webhook connectivity...")
                manager.test_webhook_connectivity()
            elif choice == '4':
                print("\n❌ Removing webhook...")
                manager.remove_webhook()
            elif choice == '5':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
