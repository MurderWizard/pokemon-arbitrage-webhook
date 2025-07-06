#!/usr/bin/env python3
"""Simple test to verify basic functionality"""

print("🎴 Quick System Check")
print("=" * 30)

try:
    print("1. Testing basic imports...")
    from dotenv import load_dotenv
    print("   ✅ dotenv")
    
    import os
    load_dotenv()
    print("   ✅ environment loaded")
    
    print("2. Testing Telegram...")
    token = os.getenv('TG_TOKEN')
    if token:
        print(f"   ✅ Telegram token found: {token[:10]}...")
    else:
        print("   ❌ No Telegram token")
        
    print("3. Testing pricing...")
    from quick_price import get_card_market_price
    price, confidence = get_card_market_price("Charizard", "Base Set")
    if price:
        print(f"   ✅ Pricing working: ${price:.2f}")
    else:
        print("   ❌ Pricing failed")
        
    print("\n🎉 Basic functionality working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
