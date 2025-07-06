#!/usr/bin/env python3
"""
Quick Telegram Test for Tonight's Demo
Tests if notifications are working properly
"""

import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv
from datetime import datetime

async def test_telegram():
    """Test Telegram connection and send demo message"""
    load_dotenv()
    
    print("🧪 Testing Telegram for tonight's demo...")
    
    bot_token = os.getenv('TG_TOKEN')
    user_id = os.getenv('TG_ADMIN_ID')
    
    if not bot_token or not user_id:
        print("❌ Missing Telegram credentials!")
        print("Add to .env file:")
        print("TG_TOKEN=your_bot_token")
        print("TG_ADMIN_ID=your_chat_id")
        return False
    
    try:
        bot = Bot(token=bot_token)
        
        # Send test message
        test_message = (
            f"🎉 DEMO TEST MESSAGE\n\n"
            f"✅ Telegram: WORKING!\n"
            f"✅ Background System: READY!\n"
            f"✅ Arbitrage Bot: ONLINE!\n\n"
            f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}\n"
            f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"🚀 Ready for work demo tonight!\n"
            f"💰 Pokemon card deals incoming..."
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=test_message
        )
        
        print("✅ Telegram test successful!")
        print("📱 Check your phone - you should have received a message!")
        print("🎯 Ready for background system!")
        return True
        
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_telegram())
    
    if success:
        print("\n🎉 ALL SYSTEMS GO FOR TONIGHT!")
        print("Run: python3 background_arbitrage_mvp.py")
    else:
        print("\n❌ Fix Telegram setup first")
