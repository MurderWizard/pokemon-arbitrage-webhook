#!/usr/bin/env python3
"""
Quick database status check
"""

from pokemon_price_system import price_db

def main():
    print("🔍 CURRENT DATABASE STATUS")
    print("=" * 40)
    
    try:
        stats = price_db.get_price_statistics()
        print(f"📊 Unique cards: {stats['unique_cards']:,}")
        print(f"💰 Total price entries: {stats['total_prices']:,}")
        print(f"🔄 Fresh prices (24h): {stats['fresh_prices']:,}")
        print(f"📈 Freshness ratio: {stats['freshness_ratio']:.1%}")
        
        if stats['unique_cards'] == 0:
            print("\n⚠️  Database is empty! Ready for massive scaling!")
        elif stats['unique_cards'] < 100:
            print("\n🚀 Small database - perfect for rapid expansion!")
        elif stats['unique_cards'] < 1000:
            print("\n📈 Growing database - ready for comprehensive scaling!")
        else:
            print("\n💎 Substantial database - ready for optimization!")
            
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

if __name__ == "__main__":
    main()
