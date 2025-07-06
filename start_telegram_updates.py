#!/usr/bin/env python3
"""
Start Telegram Updates - Ready for Live Arbitrage Notifications!
"""

import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot

async def start_telegram_updates():
    """Initialize and test Telegram notification system"""
    
    print("🎯 POKEMON ARBITRAGE SYSTEM - TELEGRAM UPDATES")
    print("=" * 55)
    
    # Load credentials
    load_dotenv()
    bot_token = os.getenv('TG_TOKEN')
    user_id = os.getenv('TG_ADMIN_ID')
    
    if not bot_token or not user_id:
        print("❌ Missing Telegram credentials!")
        print("   Please set TG_TOKEN and TG_ADMIN_ID in .env file")
        return False
    
    try:
        # Test connection and send startup message
        bot = Bot(token=bot_token)
        
        startup_message = """🚀 **POKEMON ARBITRAGE SYSTEM ONLINE**

✅ **Vault Protection**: Cards guaranteed $250+ even with poor grading
✅ **Smart Filtering**: $400+ profit minimum for realistic deal flow  
✅ **Capital Safety**: Max $600 per deal (30% of bankroll)
✅ **Raw Card Focus**: PSA grading arbitrage through eBay Vault

🎯 **What You'll Get:**
• Real-time deal notifications
• Professional profit analysis
• Timeline and risk assessment
• Direct eBay listing links
• Manual approval workflow

💡 **Next Steps:**
1. System monitors eBay continuously
2. Telegram alerts for high-quality deals
3. Review and approve manually
4. Track through PSA grading
5. Vault storage and automated selling

**Ready to find profitable Pokemon card deals!** 🎴"""

        await bot.send_message(
            chat_id=user_id,
            text=startup_message,
            parse_mode='Markdown'
        )
        
        print("✅ Telegram updates successfully initialized!")
        print("\n🎯 SYSTEM STATUS:")
        print("   📱 Telegram: Connected and ready")
        print("   🛡️ Vault Protection: ACTIVE")
        print("   💰 Profit Minimum: $400 (realistic)")
        print("   🎮 Capital Protection: $600 max per deal")
        print("   ⚡ Real-time Monitoring: Ready")
        
        print("\n🚀 READY TO RECEIVE UPDATES!")
        print("   • Professional deal alerts")
        print("   • Profit and timeline analysis") 
        print("   • Risk assessment")
        print("   • Manual approval workflow")
        print("   • Complete lifecycle tracking")
        
        print("\n💡 TO START MONITORING:")
        print("   python3 background_arbitrage_mvp.py")
        print("   python3 opportunity_ranker.py")
        print("   python3 system_test.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Telegram initialization failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(start_telegram_updates())
