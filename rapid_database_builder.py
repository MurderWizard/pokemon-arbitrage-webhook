#!/usr/bin/env python3
"""
Rapid Price Database Builder
Quickly build a comprehensive Pokemon card price database

This tool helps you go from 14 cards to 500+ cards efficiently by:
- Importing popular card lists
- Auto-estimating prices for similar cards
- Bulk adding trending cards
- Strategic card selection
"""

import json
import csv
import requests
from datetime import datetime
from pokemon_price_system import price_db

class RapidDatabaseBuilder:
    """Tool to rapidly expand the price database"""
    
    def __init__(self):
        self.db = price_db
        self.added_count = 0
        
        # Popular Pokemon card lists for rapid expansion
        self.card_templates = {
            'modern_vmax': [
                ('Charizard VMAX', ['Champions Path', 'Darkness Ablaze', 'Shining Fates']),
                ('Pikachu VMAX', ['Vivid Voltage', 'Sword & Shield Promo']),
                ('Rayquaza VMAX', ['Evolving Skies']),
                ('Umbreon VMAX', ['Evolving Skies']),
                ('Sylveon VMAX', ['Evolving Skies']),
                ('Leafeon VMAX', ['Evolving Skies']),
                ('Glaceon VMAX', ['Evolving Skies']),
                ('Duraludon VMAX', ['Evolving Skies']),
                ('Dragapult VMAX', ['Rebel Clash']),
                ('Centiskorch VMAX', ['Darkness Ablaze']),
                ('Lapras VMAX', ['Sword & Shield']),
                ('Snorlax VMAX', ['Sword & Shield']),
                ('Toxapex VMAX', ['Rebel Clash']),
                ('Coalossal VMAX', ['Rebel Clash']),
                ('Copperajah VMAX', ['Rebel Clash']),
            ],
            
            'modern_v': [
                ('Charizard V', ['Champions Path', 'Darkness Ablaze']),
                ('Pikachu V', ['Vivid Voltage', 'Sword & Shield Promo']),
                ('Rayquaza V', ['Evolving Skies']),
                ('Umbreon V', ['Evolving Skies']),
                ('Sylveon V', ['Evolving Skies']),
                ('Leafeon V', ['Evolving Skies']),
                ('Glaceon V', ['Evolving Skies']),
                ('Duraludon V', ['Evolving Skies']),
                ('Dragapult V', ['Rebel Clash']),
                ('Centiskorch V', ['Darkness Ablaze']),
                ('Lapras V', ['Sword & Shield']),
                ('Snorlax V', ['Sword & Shield']),
                ('Crobat V', ['Darkness Ablaze']),
                ('Dedenne GX', ['Unbroken Bonds']),
                ('Crobat V', ['Shining Fates']),
            ],
            
            'classic_base': [
                ('Charizard', ['Base Set', 'Base Set Shadowless', 'Base Set 1st Edition']),
                ('Blastoise', ['Base Set', 'Base Set Shadowless', 'Base Set 1st Edition']),
                ('Venusaur', ['Base Set', 'Base Set Shadowless', 'Base Set 1st Edition']),
                ('Alakazam', ['Base Set', 'Base Set Shadowless']),
                ('Chansey', ['Base Set', 'Base Set Shadowless']),
                ('Clefairy', ['Base Set', 'Base Set Shadowless']),
                ('Gyarados', ['Base Set', 'Base Set Shadowless']),
                ('Hitmonchan', ['Base Set', 'Base Set Shadowless']),
                ('Machamp', ['Base Set', 'Base Set Shadowless']),
                ('Magneton', ['Base Set', 'Base Set Shadowless']),
                ('Mewtwo', ['Base Set', 'Base Set Shadowless']),
                ('Nidoking', ['Base Set', 'Base Set Shadowless']),
                ('Ninetales', ['Base Set', 'Base Set Shadowless']),
                ('Poliwrath', ['Base Set', 'Base Set Shadowless']),
                ('Raichu', ['Base Set', 'Base Set Shadowless']),
                ('Zapdos', ['Base Set', 'Base Set Shadowless']),
            ],
            
            'gx_cards': [
                ('Charizard GX', ['Hidden Fates', 'Burning Shadows']),
                ('Mewtwo GX', ['Shining Legends']),
                ('Pikachu GX', ['SM Promos']),
                ('Rayquaza GX', ['Celestial Storm']),
                ('Umbreon GX', ['Sun & Moon']),
                ('Espeon GX', ['Sun & Moon']),
                ('Sylveon GX', ['Guardians Rising']),
                ('Leafeon GX', ['Ultra Prism']),
                ('Glaceon GX', ['Ultra Prism']),
                ('Lycanroc GX', ['Guardians Rising']),
                ('Drampa GX', ['Guardians Rising']),
                ('Tapu Lele GX', ['Guardians Rising']),
                ('Gardevoir GX', ['Burning Shadows']),
                ('Golisopod GX', ['Burning Shadows']),
                ('Necrozma GX', ['Burning Shadows']),
            ]
        }
        
        # Price estimation rules
        self.price_estimates = {
            'VMAX': {
                'Champions Path': 85.0,  # Premium set
                'Evolving Skies': 70.0,  # Popular set
                'Darkness Ablaze': 45.0,  # Common set
                'default': 35.0
            },
            'V': {
                'Champions Path': 25.0,
                'Evolving Skies': 20.0,
                'default': 12.0
            },
            'GX': {
                'Hidden Fates': 35.0,
                'Shining Legends': 25.0,
                'default': 15.0
            },
            'Base Set': {
                'Base Set 1st Edition': 2500.0,  # Charizard price
                'Base Set Shadowless': 850.0,
                'Base Set': 450.0
            }
        }
    
    def estimate_card_price(self, card_name: str, set_name: str) -> float:
        """Estimate card price based on patterns"""
        
        # Special cases for high-value cards
        if 'charizard' in card_name.lower():
            if 'vmax' in card_name.lower():
                return self.price_estimates['VMAX'].get(set_name, 85.0)
            elif 'gx' in card_name.lower():
                return self.price_estimates['GX'].get(set_name, 35.0)
            elif 'base set' in set_name.lower():
                return self.price_estimates['Base Set'].get(set_name, 450.0)
        
        # VMAX cards
        if 'vmax' in card_name.lower():
            return self.price_estimates['VMAX'].get(set_name, 35.0)
        
        # V cards
        if ' v' in card_name.lower() and 'vmax' not in card_name.lower():
            return self.price_estimates['V'].get(set_name, 12.0)
        
        # GX cards
        if 'gx' in card_name.lower():
            return self.price_estimates['GX'].get(set_name, 15.0)
        
        # EX cards
        if 'ex' in card_name.lower():
            return 10.0
        
        # Base set cards
        if 'base set' in set_name.lower():
            if '1st edition' in set_name.lower():
                return 150.0
            elif 'shadowless' in set_name.lower():
                return 75.0
            else:
                return 35.0
        
        # Default estimate
        return 8.0
    
    def bulk_add_card_template(self, template_name: str):
        """Add cards from a predefined template"""
        if template_name not in self.card_templates:
            print(f"❌ Template '{template_name}' not found")
            return
        
        cards = self.card_templates[template_name]
        print(f"\n📦 Adding {template_name} cards...")
        
        for card_name, sets in cards:
            for set_name in sets:
                # Check if already exists
                existing = self.db.get_card_price(card_name, set_name)
                if existing:
                    continue
                
                # Estimate price
                estimated_price = self.estimate_card_price(card_name, set_name)
                
                # Add to database
                self.db.update_price_manually(card_name, set_name, estimated_price)
                print(f"  ✅ {card_name} ({set_name}): ${estimated_price:.2f}")
                self.added_count += 1
        
        print(f"📈 Added {len([card for card, sets in cards for set_name in sets])} cards from {template_name}")
    
    def rapid_expansion_session(self):
        """Interactive session to rapidly expand database"""
        print("🚀 Rapid Database Expansion")
        print("=" * 50)
        print("Goal: Build comprehensive price database quickly")
        print("Strategy: Add popular card templates with smart price estimation")
        
        templates = list(self.card_templates.keys())
        
        print(f"\n📋 Available Templates:")
        for i, template in enumerate(templates, 1):
            count = sum(len(sets) for _, sets in self.card_templates[template])
            print(f"{i}. {template}: {count} cards")
        
        print("\n🎯 Recommended build order:")
        print("1. modern_vmax (high-value current cards)")
        print("2. classic_base (vintage valuable cards)")
        print("3. modern_v (popular tournament cards)")
        print("4. gx_cards (stable value cards)")
        
        while True:
            print(f"\n📊 Current database: {self.get_current_count()} cards")
            print("\nOptions:")
            print("1. Add specific template")
            print("2. Add ALL templates (fast build)")
            print("3. Add custom cards")
            print("4. Show current stats")
            print("5. Quit")
            
            choice = input("\nChoose option (1-5): ").strip()
            
            if choice == '1':
                self.add_specific_template()
            elif choice == '2':
                self.add_all_templates()
            elif choice == '3':
                self.add_custom_cards()
            elif choice == '4':
                self.show_current_stats()
            elif choice == '5':
                self.show_final_summary()
                break
            else:
                print("Invalid choice!")
    
    def add_specific_template(self):
        """Add a specific template"""
        templates = list(self.card_templates.keys())
        
        print("\nTemplates:")
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template}")
        
        try:
            choice = int(input(f"\nChoose template (1-{len(templates)}): "))
            if 1 <= choice <= len(templates):
                template_name = templates[choice - 1]
                self.bulk_add_card_template(template_name)
            else:
                print("Invalid choice!")
        except ValueError:
            print("Invalid input!")
    
    def add_all_templates(self):
        """Add all templates at once"""
        print("\n🚀 Adding ALL templates (this will add 100+ cards)")
        confirm = input("Continue? (y/n): ").strip().lower()
        
        if confirm == 'y':
            for template_name in self.card_templates.keys():
                self.bulk_add_card_template(template_name)
            print(f"\n🎉 Rapid expansion complete! Added {self.added_count} cards")
        else:
            print("Cancelled")
    
    def add_custom_cards(self):
        """Add custom cards manually"""
        print("\n🆕 Add Custom Cards")
        print("Enter cards one by one (press Enter with no name to stop):")
        
        while True:
            card_name = input("\nCard name: ").strip()
            if not card_name:
                break
            
            set_name = input("Set name: ").strip()
            if not set_name:
                print("Set name required!")
                continue
            
            # Auto-estimate price
            estimated_price = self.estimate_card_price(card_name, set_name)
            
            price_input = input(f"Price (estimated ${estimated_price:.2f}): $").strip()
            if price_input:
                try:
                    price = float(price_input)
                except ValueError:
                    print("Invalid price!")
                    continue
            else:
                price = estimated_price
            
            # Add the card
            self.db.update_price_manually(card_name, set_name, price)
            print(f"✅ Added {card_name} ({set_name}): ${price:.2f}")
            self.added_count += 1
    
    def get_current_count(self) -> int:
        """Get current card count"""
        stats = self.db.get_price_statistics()
        return stats['total_prices']
    
    def show_current_stats(self):
        """Show current database statistics"""
        import os
        os.system("python3 price_manager.py --stats")
    
    def show_final_summary(self):
        """Show final expansion summary"""
        final_count = self.get_current_count()
        
        print(f"\n🎉 Rapid Expansion Summary:")
        print(f"   Cards added this session: {self.added_count}")
        print(f"   Total database size: {final_count}")
        print(f"   Ready for deal discovery: {'✅' if final_count >= 100 else '⚠️ Need more cards'}")
        
        if final_count >= 100:
            print(f"\n🚀 Next steps:")
            print(f"   1. Test deal finding: python3 real_deal_finder.py")
            print(f"   2. Set up price updates: python3 weekly_price_updater.py")
            print(f"   3. Monitor opportunities daily")

def main():
    """Main function"""
    builder = RapidDatabaseBuilder()
    builder.rapid_expansion_session()

if __name__ == "__main__":
    main()
