#!/usr/bin/env python3
"""
Weekly Price Update Assistant
Makes it easy to update your most important card prices
"""

import os
from datetime import datetime
from pokemon_price_system import price_db, get_card_market_price

class WeeklyPriceUpdater:
    """Assistant for weekly price updates"""
    
    def __init__(self):
        self.db = price_db
        self.updated_count = 0
    
    def get_high_value_cards(self, min_price: float = 50.0):
        """Get cards worth $50+ that need attention"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT card_name, set_name, market_price, last_updated
            FROM card_prices 
            WHERE market_price >= ?
            ORDER BY market_price DESC
        """, (min_price,))
        
        return cursor.fetchall()
    
    def interactive_update_session(self):
        """Interactive session to update important cards"""
        print("🎯 Weekly Price Update Assistant")
        print("=" * 50)
        
        # Get high-value cards
        high_value_cards = self.get_high_value_cards()
        
        if not high_value_cards:
            print("No high-value cards found. Add some expensive cards first!")
            return
        
        print(f"\n📈 Found {len(high_value_cards)} cards worth $50+")
        print("\nCards to consider updating:")
        
        for i, (name, set_name, price, last_updated) in enumerate(high_value_cards[:10], 1):
            print(f"{i:2d}. {name} ({set_name}) - ${price:.2f}")
        
        print("\n" + "=" * 50)
        print("🔍 Let's update some prices!")
        print("For each card, I'll show current price and ask if you want to update it.")
        print("Just research the price on TCGPlayer/eBay and enter the new value.")
        print("\nPress Enter to skip a card, 'q' to quit")
        
        for name, set_name, current_price, last_updated in high_value_cards[:10]:
            print(f"\n💰 {name} ({set_name})")
            print(f"   Current: ${current_price:.2f}")
            print(f"   Last Updated: {last_updated}")
            
            # Ask user for new price
            while True:
                user_input = input(f"   New price (or Enter to skip): $").strip()
                
                if user_input.lower() == 'q':
                    print("\n✅ Update session completed!")
                    self.show_summary()
                    return
                
                if not user_input:
                    print("   ⏭️  Skipped")
                    break
                
                try:
                    new_price = float(user_input)
                    if new_price <= 0:
                        print("   ❌ Price must be positive")
                        continue
                    
                    # Update the price
                    self.db.update_price_manually(name, set_name, new_price)
                    
                    change = new_price - current_price
                    change_pct = (change / current_price) * 100
                    
                    if change > 0:
                        print(f"   ✅ Updated to ${new_price:.2f} (+${change:.2f}, +{change_pct:.1f}%)")
                    else:
                        print(f"   ✅ Updated to ${new_price:.2f} (${change:.2f}, {change_pct:.1f}%)")
                    
                    self.updated_count += 1
                    break
                    
                except ValueError:
                    print("   ❌ Invalid price format")
                    continue
        
        self.show_summary()
    
    def show_summary(self):
        """Show update session summary"""
        print(f"\n🎉 Update Summary:")
        print(f"   Updated {self.updated_count} card prices")
        print(f"   Session completed at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        if self.updated_count > 0:
            print(f"\n💡 Pro tip: Run this weekly to keep prices current!")
            print(f"   Next suggested update: {datetime.now().strftime('%Y-%m-%d')} (7 days)")
    
    def quick_add_new_cards(self):
        """Quick way to add new trending cards"""
        print("\n🆕 Add New Trending Cards")
        print("=" * 30)
        print("Enter new cards you want to track (press Enter with no name to stop):")
        
        added_count = 0
        while True:
            card_name = input("\nCard name: ").strip()
            if not card_name:
                break
            
            set_name = input("Set name: ").strip()
            if not set_name:
                print("Set name required!")
                continue
            
            while True:
                try:
                    price = float(input("Market price: $").strip())
                    if price <= 0:
                        print("Price must be positive!")
                        continue
                    break
                except ValueError:
                    print("Invalid price format!")
                    continue
            
            condition = input("Condition (default: Near Mint): ").strip() or "Near Mint"
            
            # Add the card
            self.db.update_price_manually(card_name, set_name, price, condition)
            print(f"✅ Added {card_name} ({set_name}) - ${price:.2f}")
            added_count += 1
        
        if added_count > 0:
            print(f"\n🎉 Added {added_count} new cards to your database!")

def main():
    """Main function"""
    updater = WeeklyPriceUpdater()
    
    while True:
        print("\n🎴 Weekly Price Update Menu")
        print("=" * 30)
        print("1. Update high-value card prices")
        print("2. Add new trending cards")
        print("3. Show database stats")
        print("4. Quit")
        
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == '1':
            updater.interactive_update_session()
        elif choice == '2':
            updater.quick_add_new_cards()
        elif choice == '3':
            os.system("python3 price_manager.py --stats")
        elif choice == '4':
            print("👋 Happy trading!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
