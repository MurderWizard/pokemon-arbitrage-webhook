#!/usr/bin/env python3
"""
Daily Price Update Automation
Keeps your price database fresh for maximum opportunity discovery

Runs 2-3x daily to catch price movements and new opportunities
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pokemon_price_system import price_db, get_card_market_price

class DailyPriceUpdater:
    """Automated daily price updates"""
    
    def __init__(self):
        self.db = price_db
        self.updates_made = 0
        self.alerts = []
    
    def morning_update(self):
        """Morning update routine (8 AM) - 15 minutes"""
        print("🌅 Morning Price Update")
        print("=" * 30)
        
        # 1. Check high-value cards for overnight changes
        self.check_high_value_cards()
        
        # 2. Verify any deals from yesterday
        self.verify_recent_deals()
        
        # 3. Quick trend analysis
        self.analyze_trends()
        
        self.show_morning_summary()
    
    def evening_update(self):
        """Evening update routine (8 PM) - 30 minutes"""
        print("🌆 Evening Price Update")
        print("=" * 30)
        
        # 1. Add new trending cards
        self.add_trending_cards()
        
        # 2. Update cards you bought/sold today
        self.update_portfolio_cards()
        
        # 3. Research 10-20 new cards
        self.research_new_cards()
        
        self.show_evening_summary()
    
    def check_high_value_cards(self):
        """Check high-value cards for price changes"""
        print("\n💎 Checking high-value cards...")
        
        # Get cards worth $50+
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT card_name, set_name, market_price, last_updated
            FROM card_prices 
            WHERE market_price >= 50.0
            ORDER BY market_price DESC
            LIMIT 10
        ''')
        
        high_value_cards = cursor.fetchall()
        conn.close()
        
        for name, set_name, current_price, last_updated in high_value_cards:
            # Check if price needs updating (>24 hours old)
            updated_time = datetime.fromisoformat(last_updated)
            if datetime.now() - updated_time > timedelta(hours=24):
                print(f"  ⚠️  {name} ({set_name}): ${current_price:.2f} - needs update")
                self.alerts.append(f"Update needed: {name} ({set_name})")
            else:
                print(f"  ✅ {name} ({set_name}): ${current_price:.2f} - fresh")
    
    def verify_recent_deals(self):
        """Verify prices for any deals found recently"""
        print("\n🔍 Verifying recent deal prices...")
        
        # This would check against a "recent_deals" log
        # For now, just check the most recently updated cards
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT card_name, set_name, market_price, last_updated
            FROM card_prices 
            ORDER BY last_updated DESC
            LIMIT 5
        ''')
        
        recent_cards = cursor.fetchall()
        conn.close()
        
        for name, set_name, price, updated in recent_cards:
            print(f"  📊 {name} ({set_name}): ${price:.2f}")
    
    def analyze_trends(self):
        """Quick trend analysis"""
        print("\n📈 Trend Analysis...")
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT price_trend, COUNT(*) as count
            FROM card_prices 
            GROUP BY price_trend
        ''')
        
        trends = cursor.fetchall()
        conn.close()
        
        for trend, count in trends:
            print(f"  {trend}: {count} cards")
    
    def add_trending_cards(self):
        """Add new trending cards from research"""
        print("\n🔥 Adding trending cards...")
        
        # Popular cards to research (would come from social media/news)
        trending_cards = [
            ("Pikachu ex", "Surging Sparks", 45.0),
            ("Charizard ex", "Obsidian Flames", 55.0),
            ("Miraidon ex", "Scarlet & Violet", 25.0),
            ("Koraidon ex", "Scarlet & Violet", 25.0),
        ]
        
        for card_name, set_name, estimated_price in trending_cards:
            # Check if already exists
            existing = self.db.get_card_price(card_name, set_name)
            if not existing:
                self.db.update_price_manually(card_name, set_name, estimated_price)
                print(f"  ✅ Added {card_name} ({set_name}): ${estimated_price:.2f}")
                self.updates_made += 1
            else:
                print(f"  ⏭️  {card_name} ({set_name}): already exists")
    
    def update_portfolio_cards(self):
        """Update cards in your portfolio"""
        print("\n📦 Portfolio card updates...")
        
        # This would integrate with your inventory system
        # For now, just show what cards might need updates
        print("  💡 Tip: Update any cards you bought or sold today")
        print("     Use: python3 price_manager.py --add 'Card Name' 'Set' price")
    
    def research_new_cards(self):
        """Research and add new cards"""
        print("\n🔬 Research session...")
        print("  💡 Add 10-20 new cards daily to build comprehensive database")
        print("  🎯 Focus on:")
        print("     - Cards appearing frequently on eBay")
        print("     - Tournament meta cards")
        print("     - Social media trending cards")
        print("     - Newly released cards")
    
    def show_morning_summary(self):
        """Show morning update summary"""
        print(f"\n☀️ Morning Update Complete")
        print(f"   High-value cards checked: ✅")
        print(f"   Alerts: {len(self.alerts)}")
        
        if self.alerts:
            print("   🚨 Action items:")
            for alert in self.alerts:
                print(f"     - {alert}")
        
        print(f"   💡 Next: Evening update at 8 PM")
    
    def show_evening_summary(self):
        """Show evening update summary"""
        current_count = self.get_current_count()
        
        print(f"\n🌙 Evening Update Complete")
        print(f"   Cards added: {self.updates_made}")
        print(f"   Total database: {current_count} cards")
        print(f"   Status: {'✅ Good coverage' if current_count >= 100 else '⚠️ Need more cards'}")
        
        print(f"\n🎯 Tomorrow's goals:")
        print(f"   - Add 15+ new cards")
        print(f"   - Update high-value prices")
        print(f"   - Monitor for opportunities")
    
    def get_current_count(self) -> int:
        """Get current card count"""
        stats = self.db.get_price_statistics()
        return stats['total_prices']
    
    def automated_expansion(self):
        """Automated database expansion"""
        print("🤖 Automated Database Expansion")
        print("=" * 40)
        
        current_count = self.get_current_count()
        print(f"Current database size: {current_count} cards")
        
        if current_count < 100:
            print("\n🚀 Running rapid expansion...")
            # Auto-add popular card templates
            from rapid_database_builder import RapidDatabaseBuilder
            builder = RapidDatabaseBuilder()
            
            # Add modern VMAX cards
            builder.bulk_add_card_template('modern_vmax')
            self.updates_made += builder.added_count
            
            # Add some classic cards
            builder.bulk_add_card_template('classic_base')
            self.updates_made += builder.added_count
            
            print(f"✅ Auto-expansion complete! Added {self.updates_made} cards")
        else:
            print("✅ Database size is good. Doing maintenance updates...")
            self.add_trending_cards()

def main():
    """Main function"""
    updater = DailyPriceUpdater()
    
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'morning':
            updater.morning_update()
        elif sys.argv[1] == 'evening':
            updater.evening_update()
        elif sys.argv[1] == 'auto':
            updater.automated_expansion()
        else:
            print("Usage: python3 daily_price_updater.py [morning|evening|auto]")
    else:
        # Interactive mode
        print("📅 Daily Price Update Menu")
        print("=" * 30)
        print("1. Morning update (15 min)")
        print("2. Evening update (30 min)")
        print("3. Automated expansion")
        print("4. Show current stats")
        
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == '1':
            updater.morning_update()
        elif choice == '2':
            updater.evening_update()
        elif choice == '3':
            updater.automated_expansion()
        elif choice == '4':
            os.system("python3 price_manager.py --stats")
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
