#!/usr/bin/env python3
"""
Quick test to verify Telegram bot and pricing system
"""
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from pokemon_price_system import get_card_market_price

async def test_telegram_and_pricing():
    """Test both Telegram bot and pricing system"""
    load_dotenv()
    
    # Test Telegram
    print("🤖 Testing Telegram Bot...")
    bot_token = os.getenv('TG_TOKEN')
    user_id = os.getenv('TG_ADMIN_ID')
    
    if not bot_token or not user_id:
        print("❌ Missing Telegram credentials in .env")
        return False
    
    try:
        bot = Bot(token=bot_token)
        await bot.send_message(
            chat_id=user_id,
            text="✅ Test Alert: Telegram integration working!\n\n🎯 Ready for eBay API setup!"
        )
        print("✅ Telegram bot working!")
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False
    
    # Test pricing system
    print("\n💰 Testing Pricing System...")
    try:
        price, confidence = get_card_market_price("Charizard VMAX", "Champions Path")
        if price:
            print(f"✅ Price lookup working: Charizard VMAX = ${price:.2f} (confidence: {confidence:.1%})")
        else:
            print("❌ Price lookup failed")
            return False
    except Exception as e:
        print(f"❌ Pricing error: {e}")
        return False
    
    print("\n🎉 Both systems working! Ready for eBay API setup!")
    return True

if __name__ == "__main__":
    asyncio.run(test_telegram_and_pricing())
