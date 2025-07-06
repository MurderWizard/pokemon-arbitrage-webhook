#!/usr/bin/env python3
"""
Button Test - Send test deal and provide testing instructions
"""
import asyncio
from mvp_telegram_bot import send_mvp_deal_alert

async def send_button_test():
    """Send a test deal to verify button layout"""
    
    print("🧪 Sending Button Test Deal")
    print("=" * 30)
    
    test_deal = {
        'card_name': "Test Card",
        'set_name': "Button Test",
        'raw_price': 300.00,
        'estimated_psa10_price': 4000.00,
        'potential_profit': 3675.00,
        'condition_notes': "TEST DEAL - Check if buttons are visible and clickable",
        'listing_url': "https://www.ebay.com/itm/buttontest"
    }
    
    success = await send_mvp_deal_alert(test_deal, "BTN_TEST")
    
    if success:
        print("✅ Test deal sent!")
        print("\n📱 Check Telegram and verify:")
        print("   1. Can you see the buttons?")
        print("   2. Do buttons respond when tapped?")
        print("   3. Is there any visual feedback?")
        print("\n🔧 If buttons don't work:")
        print("   - They may just show the alert but not process")
        print("   - This is expected in MVP mode")
        print("   - Manual action required for now")
    else:
        print("❌ Failed to send test deal")

if __name__ == "__main__":
    asyncio.run(send_button_test())
