#!/usr/bin/env python3
"""
Simple webhook setup with debugging
"""
import os
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    bot_token = os.getenv('TG_TOKEN')
    webhook_url = "https://34.74.208.133:8080/webhook"
    cert_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.crt'
    
    print("🔗 Setting up Telegram webhook...")
    print(f"Bot token: {'✅ Found' if bot_token else '❌ Missing'}")
    print(f"Webhook URL: {webhook_url}")
    print(f"SSL cert: {'✅ Found' if os.path.exists(cert_file) else '❌ Missing'}")
    
    if not bot_token:
        print("❌ No bot token found!")
        return
    
    try:
        # First, check current webhook status
        print("\n📊 Checking current webhook status...")
        status_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(status_url, timeout=10)
        
        if response.ok:
            result = response.json()
            if result.get('ok'):
                info = result.get('result', {})
                current_url = info.get('url', 'Not set')
                print(f"Current webhook URL: {current_url}")
                
                if info.get('last_error_message'):
                    print(f"🚨 Last error: {info.get('last_error_message')}")
        
        # Now set the webhook
        print(f"\n🔗 Setting webhook to: {webhook_url}")
        set_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        
        if os.path.exists(cert_file):
            print("📄 Using SSL certificate...")
            with open(cert_file, 'rb') as cert:
                files = {'certificate': cert}
                data = {
                    'url': webhook_url,
                    'max_connections': 40,
                    'allowed_updates': ['message', 'callback_query']
                }
                response = requests.post(set_url, data=data, files=files, timeout=30)
        else:
            print("⚠️  No SSL certificate, setting webhook without cert...")
            data = {
                'url': webhook_url,
                'max_connections': 40,
                'allowed_updates': ['message', 'callback_query']
            }
            response = requests.post(set_url, json=data, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.ok:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook set successfully!")
            else:
                print(f"❌ Telegram error: {result.get('description', 'Unknown')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
