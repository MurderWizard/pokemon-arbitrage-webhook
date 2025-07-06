#!/usr/bin/env python3
"""
Start Button Handler Service - Run this to make buttons work
"""
import asyncio
from working_deal_bot import MVPDealBotWithCallbacks

async def start_button_service():
    """Start the button handling service"""
    print("🚀 Starting Button Handler Service")
    print("=" * 40)
    print("✅ Telegram buttons will now work!")
    print("🔄 Bot is listening for button taps...")
    print("⚠️  Keep this running for buttons to work")
    print("\nPress Ctrl+C to stop\n")
    
    bot = MVPDealBotWithCallbacks()
    
    try:
        await bot.start_bot_service()
    except KeyboardInterrupt:
        print("\n🛑 Button service stopped")

if __name__ == "__main__":
    asyncio.run(start_button_service())
