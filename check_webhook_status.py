#!/usr/bin/env python3
"""
Check Telegram webhook status
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_webhook_status():
    bot_token = os.getenv('TG_TOKEN')
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    try:
        response = requests.get(url, timeout=10)
        if response.ok:
            result = response.json()
            if result.get('ok'):
                info = result.get('result', {})
                print("📊 Current Telegram Webhook Status:")
                print(f"   URL: {info.get('url', 'Not set')}")
                print(f"   Has Custom Certificate: {info.get('has_custom_certificate', False)}")
                print(f"   Pending Updates: {info.get('pending_update_count', 0)}")
                print(f"   Max Connections: {info.get('max_connections', 'Not set')}")
                print(f"   Allowed Updates: {info.get('allowed_updates', 'All')}")
                
                if info.get('last_error_message'):
                    print(f"   🚨 Last Error: {info.get('last_error_message')}")
                    print(f"   🕒 Error Date: {info.get('last_error_date', 'Unknown')}")
                else:
                    print("   ✅ No errors reported")
                
                return info
            else:
                print(f"❌ API error: {result.get('description', 'Unknown')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    check_webhook_status()
