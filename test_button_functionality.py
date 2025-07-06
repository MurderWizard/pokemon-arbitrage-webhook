#!/usr/bin/env python3
"""
Test Button Functionality - Send test deal and start callback handler
"""
import asyncio
import os
from dotenv import load_dotenv
from mvp_telegram_bot import MVPTelegramBot
from telegram.ext import Application, CallbackQueryHandler

async def test_buttons_with_handler():
    """Send test deal and start callback handler"""
    load_dotenv()
    
    print("🧪 Testing Button Functionality")
    print("=" * 40)
    
    # Create bot instance
    bot = MVPTelegramBot()
    
    # Send test deal
    test_deal = {
        'card_name': "Charizard",
        'set_name': "Base Set", 
        'raw_price': 325.00,
        'estimated_psa10_price': 5000.00,
        'potential_profit': 4650.00,
        'condition_notes': "TEST DEAL - Tap buttons to test functionality",
        'listing_url': "https://www.ebay.com/itm/test123"
    }
    
    print("📱 Sending test deal with buttons...")
    await bot.send_deal_alert(test_deal, "TEST_BTN")
    
    # Start callback handler
    print("🤖 Starting callback handler...")
    print("✅ Tap the buttons in Telegram to test!")
    print("   - BUY button should show approval")
    print("   - PASS button should show rejection") 
    print("   - INFO button should show details")
    print("\nPress Ctrl+C to stop the handler\n")
    
    # Create application for handling callbacks
    application = Application.builder().token(bot.token).build()
    
    # Add callback handler
    application.add_handler(CallbackQueryHandler(bot.handle_callback))
    
    # Start polling for callbacks
    try:
        await application.run_polling()
    except KeyboardInterrupt:
        print("\n🛑 Callback handler stopped")
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(test_buttons_with_handler())
