#!/usr/bin/env python3
"""
Quick Telegram Setup for Tonight's Demo
Gets you set up with notifications in 2 minutes!
"""

print("🎯 QUICK TELEGRAM SETUP FOR TONIGHT'S DEMO")
print("=" * 50)
print()
print("You need 2 things for Telegram notifications:")
print()
print("1️⃣  BOT TOKEN from @BotFather")
print("   - Open Telegram")
print("   - Search for @BotFather")
print("   - Send: /newbot")
print("   - Follow prompts to create your bot")
print("   - Copy the token (looks like: 123456789:ABCdef...)")
print()
print("2️⃣  YOUR CHAT ID")
print("   - Send a message to your bot")
print("   - Then run: python3 get_telegram_id.py")
print("   - Or visit: https://api.telegram.org/bot<TOKEN>/getUpdates")
print()
print("📝 Then add to .env file:")
print("TG_TOKEN=your_bot_token_here")
print("TG_ADMIN_ID=your_chat_id_here")
print()
print("⚡ QUICK METHOD:")
print("1. Create bot with @BotFather")
print("2. Get your token")
print("3. Run: ./add_telegram_to_env.sh TOKEN CHAT_ID")
print()
print("🎉 Then run: python3 test_telegram_demo.py")

# Check if credentials are already set
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TG_TOKEN')
user_id = os.getenv('TG_ADMIN_ID')

if token and user_id:
    print("\n✅ TELEGRAM ALREADY CONFIGURED!")
    print("Run: python3 test_telegram_demo.py")
else:
    print("\n❌ Missing Telegram credentials")
    print("Add them to .env file to continue")
