#!/usr/bin/env python3
"""
Set Telegram Webhook - Point Telegram to your webhook server
"""
import os
import requests
from dotenv import load_dotenv

def set_webhook():
    load_dotenv()
    
    bot_token = os.getenv('TG_TOKEN')
    if not bot_token:
        print("❌ Missing TG_TOKEN in .env file")
        return False
    
    # Your server's external IP and port
    webhook_url = "http://34.74.208.133:8080/webhook"
    
    print(f"🌐 Setting Telegram webhook to: {webhook_url}")
    
    # Set the webhook
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    data = {'url': webhook_url}
    
    try:
        response = requests.post(url, data=data)
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook set successfully!")
            print(f"📋 Webhook URL: {webhook_url}")
            print("🎯 Telegram buttons will now work!")
            return True
        else:
            print(f"❌ Failed to set webhook: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False

def check_webhook():
    """Check current webhook status"""
    load_dotenv()
    bot_token = os.getenv('TG_TOKEN')
    
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get('ok'):
            webhook_info = result.get('result', {})
            current_url = webhook_info.get('url', 'None')
            print(f"📋 Current webhook: {current_url}")
            print(f"📊 Pending updates: {webhook_info.get('pending_update_count', 0)}")
            
            if webhook_info.get('last_error_date'):
                print(f"⚠️ Last error: {webhook_info.get('last_error_message', 'Unknown')}")
        else:
            print(f"❌ Failed to get webhook info: {result}")
            
    except Exception as e:
        print(f"❌ Error checking webhook: {e}")

def remove_webhook():
    """Remove webhook (for testing)"""
    load_dotenv()
    bot_token = os.getenv('TG_TOKEN')
    
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    data = {'url': ''}  # Empty URL removes webhook
    
    try:
        response = requests.post(url, data=data)
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook removed successfully!")
        else:
            print(f"❌ Failed to remove webhook: {result}")
            
    except Exception as e:
        print(f"❌ Error removing webhook: {e}")

if __name__ == "__main__":
    print("🎯 Telegram Webhook Manager")
    print("=" * 30)
    print("1. Set webhook")
    print("2. Check webhook status")
    print("3. Remove webhook")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        set_webhook()
    elif choice == "2":
        check_webhook()
    elif choice == "3":
        remove_webhook()
    else:
        print("Invalid choice")
