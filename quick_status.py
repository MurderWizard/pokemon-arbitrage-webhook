#!/usr/bin/env python3
"""
Quick opportunity status check without eBay API calls
"""

import sys
import os
sys.path.append('.')

def check_system_status():
    print("🎴 Pokemon Arbitrage System Status")
    print("=" * 50)
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        with open('.env', 'r') as f:
            content = f.read()
            
        if 'TG_TOKEN=' in content and len(content.split('TG_TOKEN=')[1].split('\n')[0]) > 10:
            print("✅ Telegram token configured")
        else:
            print("⚠️ Telegram token missing or invalid")
            
        if 'EBAY_APP_ID=' in content:
            print("✅ eBay credentials configured")
        else:
            print("⚠️ eBay credentials missing")
    else:
        print("❌ .env file not found")
    
    # Check key files
    key_files = [
        'opportunity_ranker.py',
        'ebay_browse_api_integration.py', 
        'enhanced_arbitrage_bot.py',
        'background_arbitrage_mvp.py',
        'vault_eligibility_checker.py'
    ]
    
    print("\n📁 Core files:")
    for file in key_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
    
    # Check if background process should be running
    print("\n🤖 Background Process Status:")
    print("To start monitoring: python background_arbitrage_mvp.py")
    print("To check opportunities: python enhanced_arbitrage_bot.py")
    print("To test system: python system_test.py")
    
    print("\n🎯 Current Configuration:")
    print("• Minimum profit: $400 (configurable in opportunity_ranker.py)")
    print("• Vault eligibility: $250+ required")
    print("• Target: Raw cards for PSA grading arbitrage")
    print("• Rate limiting: Smart Browse API integration")
    
    print("\n💡 Quick Start:")
    print("1. Ensure Telegram token is valid in .env")
    print("2. Start background monitoring: python background_arbitrage_mvp.py")
    print("3. Test manually: python enhanced_arbitrage_bot.py")
    
    return True

if __name__ == "__main__":
    check_system_status()
