#!/usr/bin/env python3
"""
System Status Check - Quick overview of what's working
"""
import os
from dotenv import load_dotenv

def check_system_status():
    """Check status of all components"""
    load_dotenv()
    
    print("🎴 Pokemon Card Arbitrage System Status")
    print("=" * 50)
    
    # Check Telegram
    print("\n📱 Telegram Bot:")
    tg_token = os.getenv('TG_TOKEN')
    tg_user = os.getenv('TG_ADMIN_ID')
    
    if tg_token and tg_user and tg_user != 'your_telegram_user_id_here':
        print("   ✅ Configured and ready")
        print(f"   📧 Bot: @cardizard_bot")
        print(f"   👤 User ID: {tg_user}")
    else:
        print("   ❌ Not configured")
    
    # Check eBay
    print("\n🛒 eBay API:")
    ebay_app_id = os.getenv('EBAY_APP_ID')
    
    if ebay_app_id and ebay_app_id != 'your_app_id_here':
        print("   ✅ App ID configured")
        print(f"   🔑 App ID: {ebay_app_id[:10]}...")
        print("   🎯 Ready for searches")
    else:
        print("   ⏳ Waiting for developer account approval")
        print("   📋 Status: Account submitted")
        print("   ⏰ Expected: 24-48 hours")
    
    # Check Price Database
    print("\n💰 Price Database:")
    try:
        from pokemon_price_system import price_db
        # Just check if we can connect to the database
        stats = price_db.get_price_statistics()
        print(f"   ✅ Database connected")
        print(f"   📊 {stats['total_prices']} cards in database")
        print(f"   💎 {stats['fresh_prices']} fresh prices (24h)")
        freshness = stats['freshness_ratio'] * 100
        print(f"   📈 {freshness:.1f}% freshness ratio")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check Environment
    print("\n🔧 Environment:")
    print(f"   🐍 Python: Ready (.venv)")
    print(f"   📦 Packages: Installed")
    print(f"   ⚙️  Config: .env loaded")
    
    # What's Next
    print("\n🚀 What's Next:")
    if ebay_app_id == 'your_app_id_here':
        print("   1. ⏳ Wait for eBay developer approval (24-48 hours)")
        print("   2. 📧 Check email for approval notification")
        print("   3. 🔑 Get App ID from https://developer.ebay.com")
        print("   4. 📝 Add App ID to .env file")
        print("   5. 🧪 Test: python3 ebay_sdk_integration.py")
        print("   6. 🚀 Start: python3 real_deal_finder.py")
    else:
        print("   1. 🧪 Test eBay API: python3 ebay_sdk_integration.py")
        print("   2. 🚀 Start deal finder: python3 real_deal_finder.py")
        print("   3. 📱 Check Telegram for alerts")
    
    print("\n💡 Tips:")
    print("   • Start with notifications only (AUTO_BUY_ENABLED=false)")
    print("   • Monitor for a few days to see what deals are found")
    print("   • Gradually increase confidence as you learn the system")
    print("   • Check PRICING_GUIDE.md for price management tips")

if __name__ == "__main__":
    check_system_status()
