#!/usr/bin/env python3
"""
Get your Telegram User ID for the .env file

Instructions:
1. Message your bot @cardizard_bot first (send any message like "hello")
2. Run this script to get your user ID
3. Add the ID to your .env file
"""

import os
import requests
from dotenv import load_dotenv

def get_telegram_user_id():
    """Get the user ID from Telegram bot updates"""
    load_dotenv()
    
    token = os.getenv('TG_TOKEN')
    if not token:
        print("❌ No TG_TOKEN found in .env file")
        return None
    
    # Get updates from Telegram
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data['ok']:
            print(f"❌ Error from Telegram: {data['description']}")
            return None
        
        updates = data['result']
        
        if not updates:
            print("❌ No messages found!")
            print("📱 Please message your bot @cardizard_bot first, then run this script again")
            return None
        
        # Get the most recent message
        latest_update = updates[-1]
        user_id = latest_update['message']['from']['id']
        username = latest_update['message']['from'].get('username', 'No username')
        first_name = latest_update['message']['from'].get('first_name', 'No name')
        
        print(f"✅ Found your Telegram info:")
        print(f"   User ID: {user_id}")
        print(f"   Username: @{username}")
        print(f"   Name: {first_name}")
        print(f"\n📝 Add this to your .env file:")
        print(f"   TG_ADMIN_ID={user_id}")
        
        return user_id
        
    except Exception as e:
        print(f"❌ Error getting updates: {e}")
        return None

if __name__ == "__main__":
    print("🤖 Getting your Telegram User ID...")
    print("📱 Bot name: @cardizard_bot")
    print()
    
    user_id = get_telegram_user_id()
    
    if user_id:
        print(f"\n🎉 Success! Your user ID is: {user_id}")
        print("\n📋 Next steps:")
        print("1. Copy the user ID above")
        print("2. Edit your .env file")
        print("3. Replace 'your_telegram_user_id_here' with your actual ID")
        print("4. Save the file")
        print("5. Test the bot with: python3 real_deal_finder.py")
    else:
        print("\n❌ Couldn't get your user ID")
        print("📱 Make sure you've messaged @cardizard_bot first!")
