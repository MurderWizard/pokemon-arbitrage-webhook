#!/usr/bin/env python3
"""
Safe approval testing - Makes it crystal clear this is just workflow testing
"""
import asyncio
from command_approval_bot import send_command_deal_alert

async def send_safe_test_deal():
    """Send a clearly marked test deal"""
    
    print("🧪 SENDING SAFE TEST DEAL")
    print("=" * 50)
    print("🚨 THIS IS 100% SAFE TESTING")
    print("🚨 NO MONEY WILL BE SPENT")
    print("🚨 NO AUTOMATIC PURCHASES")
    print("🚨 WORKFLOW TESTING ONLY")
    print("=" * 50)
    
    test_deal = {
        'card_name': "TEST Charizard",
        'set_name': "TEST Base Set", 
        'raw_price': 1.00,  # $1 to make it clear this is just testing
        'estimated_psa10_price': 10.00,  # $10 to keep numbers small
        'potential_profit': 9.00,
        'condition_notes': "🧪 TEST DEAL - No real money involved",
        'listing_url': "https://www.example.com/test"  # Fake URL
    }
    
    success = await send_command_deal_alert(test_deal, "SAFE001")
    
    if success:
        print("✅ Safe test deal sent!")
        print("\n🧪 SAFE TESTING COMMANDS:")
        print("   • /pending - See the test deal")
        print("   • /approve SAFE001 - Test approval (NO MONEY)")
        print("   • /pass SAFE001 - Test rejection")
        print("   • /help - See safety information")
        
        print("\n🚨 REMEMBER:")
        print("   ✅ This only logs your decision")
        print("   ✅ No payments are made")
        print("   ✅ No purchases happen")
        print("   ✅ You control everything manually")
        print("   ✅ This is just workflow testing")
        
        print(f"\n🎯 Feel free to test /approve - it's 100% safe!")
        
    else:
        print("❌ Failed to send test deal")

if __name__ == "__main__":
    asyncio.run(send_safe_test_deal())
