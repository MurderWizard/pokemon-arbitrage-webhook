#!/usr/bin/env python3
"""
Quick webhook setup script
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def set_webhook():
    bot_token = os.getenv('TG_TOKEN')
    webhook_url = "https://34.74.208.133:8443/webhook"
    cert_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.crt'
    
    print(f"🔗 Setting Telegram webhook to: {webhook_url}")
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        
        with open(cert_file, 'rb') as cert:
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
                print("✅ Webhook set successfully!")
                print(f"📝 Response: {result}")
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

if __name__ == "__main__":
    set_webhook()
