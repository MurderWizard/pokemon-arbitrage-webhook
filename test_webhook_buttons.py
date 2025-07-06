#!/usr/bin/env python3
"""
Test webhook by sending a deal alert with buttons
"""
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

async def test_webhook_buttons():
    """Send a test deal alert with approve/pass buttons"""
    bot_token = os.getenv('TG_TOKEN')
    chat_id = os.getenv('TG_ADMIN_ID')
    
    bot = Bot(token=bot_token)
    
    # Create test deal message
    deal_message = """🔥 **ENHANCED WEBHOOK TEST** 🔥

🎴 **Card:** Charizard Base Set PSA Ready
💰 **Price:** $325.00
🎯 **Est. PSA 10:** $4,500.00
📈 **Profit:** $4,175.00 (12.8x ROI)
⭐ **Confidence:** 92%

📊 **Enhanced Metrics:**
• Market Depth: High liquidity
• Grading Risk: Low (excellent condition)
• Timeline: 45 days to profit
• Daily ROI: 0.28% per day

🚀 **ACTION REQUIRED:**
Click a button below to test the enhanced feedback system!"""
    
    # Create buttons
    keyboard = [
        [
            InlineKeyboardButton("✅ APPROVE", callback_data="approve_ENHANCED001"),
            InlineKeyboardButton("❌ PASS", callback_data="pass_ENHANCED001")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=deal_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        print("✅ Test webhook message sent with buttons!")
        print("🔘 Click APPROVE or PASS to test webhook functionality")
        
    except Exception as e:
        print(f"❌ Error sending test message: {e}")

if __name__ == "__main__":
    asyncio.run(test_webhook_buttons())
