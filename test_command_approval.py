#!/usr/bin/env python3
"""
Test the command approval system
"""
import asyncio
from command_approval_bot import send_command_deal_alert

async def test_command_system():
    """Test the command-based approval workflow"""
    
    print("🎴 Testing Command-Based Approval System")
    print("=" * 50)
    
    test_deal = {
        'card_name': "Charizard",
        'set_name': "Base Set",
        'raw_price': 325.00,
        'estimated_psa10_price': 4500.00,
        'potential_profit': 4150.00,
        'condition_notes': "Near Mint condition - excellent centering, sharp corners, no whitening",
        'listing_url': "https://www.ebay.com/itm/example"
    }
    
    print("📨 Sending test deal alert...")
    success = await send_command_deal_alert(test_deal, "TEST001")
    
    if success:
        print("✅ Deal alert sent successfully!")
        print("\n🤖 Command Instructions:")
        print("   Go to Telegram and try these commands:")
        print("   • /approve TEST001  (approve specific deal)")
        print("   • /pass TEST001     (reject specific deal)")
        print("   • /approve          (approve latest deal)")
        print("   • /pass             (reject latest deal)")
        print("   • /pending          (show all pending deals)")
        print("   • /status           (bot status)")
        print("   • /help             (help message)")
        
        print("\n✅ ADVANTAGES OF COMMAND SYSTEM:")
        print("   🚀 Instant response (no webhook delays)")
        print("   🔒 Reliable (no SSL/port issues)")  
        print("   📱 Simple (just type commands)")
        print("   🤖 Automated (logged and tracked)")
        print("   💪 MVP-ready (no complex infrastructure)")
        
        print("\n🎯 This replaces button complexity with:")
        print("   • Simple text commands")
        print("   • Immediate feedback")
        print("   • Full automation")
        print("   • Easy debugging")
        print("   • No webhook server needed!")
        
    else:
        print("❌ Failed to send deal alert")

if __name__ == "__main__":
    asyncio.run(test_command_system())
