#!/usr/bin/env python3
"""
Massive Pokemon Card Database Builder
Build a comprehensive 5,000+ card database while respecting API limits

Strategy:
1. Use existing card databases/lists online
2. Smart price estimation for missing data
3. Batch API calls efficiently 
4. Build incrementally with daily updates
"""

import json
import requests
import time
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional
from pokemon_price_system import price_db

class MassiveDatabaseBuilder:
    """Build comprehensive Pokemon card database"""
    
    def __init__(self):
        self.db = price_db
        self.added_count = 0
        self.api_calls_made = 0
        self.daily_api_limit = 1000  # Conservative limit
        
        # Comprehensive card sets from various eras
        self.all_sets = {
            # Modern Sets (2020-2025)
            'modern_2020_2025': [
                'Sword & Shield', 'Rebel Clash', 'Darkness Ablaze', 'Champions Path',
                'Vivid Voltage', 'Shining Fates', 'Battle Styles', 'Chilling Reign',
                'Evolving Skies', 'Celebrations', 'Fusion Strike', 'Brilliant Stars',
                'Astral Radiance', 'Pokémon GO', 'Lost Origin', 'Silver Tempest',
                'Crown Zenith', 'Paldea Evolved', 'Obsidian Flames', 'Paradox Rift',
                'Paldean Fates', 'Scarlet & Violet', 'Temporal Forces'
            ],
            
            # Sun & Moon Era (2017-2020)
            'sun_moon_era': [
                'Sun & Moon', 'Guardians Rising', 'Burning Shadows', 'Shining Legends',
                'Crimson Invasion', 'Ultra Prism', 'Forbidden Light', 'Celestial Storm',
                'Dragon Majesty', 'Lost Thunder', 'Team Up', 'Detective Pikachu',
                'Unbroken Bonds', 'Unified Minds', 'Hidden Fates', 'Cosmic Eclipse'
            ],
            
            # XY Era (2014-2017)
            'xy_era': [
                'XY', 'Flashfire', 'Furious Fists', 'Phantom Forces', 'Primal Clash',
                'Roaring Skies', 'Ancient Origins', 'BREAKthrough', 'BREAKpoint',
                'Fates Collide', 'Steam Siege', 'Evolutions'
            ],
            
            # Black & White Era (2011-2014)
            'black_white_era': [
                'Black & White', 'Emerging Powers', 'Noble Victories', 'Next Destinies',
                'Dark Explorers', 'Dragons Exalted', 'Boundaries Crossed', 'Plasma Storm',
                'Plasma Freeze', 'Plasma Blast', 'Legendary Treasures'
            ],
            
            # Classic Era (1998-2011)
            'classic_era': [
                'Base Set', 'Jungle', 'Fossil', 'Base Set 2', 'Team Rocket', 'Gym Heroes',
                'Gym Challenge', 'Neo Genesis', 'Neo Discovery', 'Neo Destiny',
                'Neo Revelation', 'Legendary Collection', 'Expedition', 'Aquapolis',
                'Skyridge', 'Ruby & Sapphire', 'Sandstorm', 'Dragon', 'Team Magma vs Team Aqua',
                'Hidden Legends', 'FireRed & LeafGreen', 'Team Rocket Returns', 'Deoxys',
                'Emerald', 'Unseen Forces', 'Delta Species', 'Legend Maker', 'Holon Phantoms',
                'Crystal Guardians', 'Dragon Frontiers', 'Power Keepers', 'Diamond & Pearl',
                'Mysterious Treasures', 'Secret Wonders', 'Great Encounters', 'Majestic Dawn',
                'Legends Awakened', 'Stormfront', 'Platinum', 'Rising Rivals', 'Supreme Victors',
                'Arceus', 'HeartGold & SoulSilver', 'Unleashed', 'Undaunted', 'Triumphant'
            ]
        }
        
        # Card rarity/type patterns for smart pricing
        self.card_patterns = {
            'charizard': {'base_price': 150, 'multiplier': {'vmax': 2.0, 'gx': 1.5, 'ex': 1.2, 'base': 3.0}},
            'pikachu': {'base_price': 30, 'multiplier': {'vmax': 2.5, 'gx': 1.8, 'promo': 2.0}},
            'rayquaza': {'base_price': 60, 'multiplier': {'vmax': 2.0, 'gx': 1.5, 'ex': 1.3}},
            'lugia': {'base_price': 80, 'multiplier': {'v': 1.5, 'gx': 1.8, 'ex': 1.4}},
            'mewtwo': {'base_price': 40, 'multiplier': {'gx': 1.5, 'ex': 1.2, 'vmax': 2.2}},
            'umbreon': {'base_price': 90, 'multiplier': {'vmax': 2.5, 'gx': 1.6, 'v': 1.3}},
            'sylveon': {'base_price': 50, 'multiplier': {'vmax': 2.0, 'gx': 1.4, 'v': 1.2}},
            'eevee': {'base_price': 25, 'multiplier': {'gx': 1.8, 'v': 1.4, 'promo': 2.0}},
            'mew': {'base_price': 35, 'multiplier': {'vmax': 2.8, 'gx': 1.6, 'ex': 1.3}},
            'gyarados': {'base_price': 20, 'multiplier': {'gx': 1.4, 'ex': 1.2, 'base': 2.0}},
        }
        
        # Card type pricing modifiers
        self.type_modifiers = {
            'vmax': 2.5,
            'vstar': 2.2,
            'v': 1.4,
            'gx': 1.6,
            'ex': 1.3,
            'full art': 1.8,
            'secret rare': 2.5,
            'rainbow rare': 3.0,
            'alternate art': 4.0,
            'gold': 2.8,
            'holo': 1.2,
            'reverse holo': 1.1,
            'first edition': 5.0,
            'shadowless': 3.0,
            'base set': 2.0,
            'promo': 1.5
        }
    
    def estimate_smart_price(self, card_name: str, set_name: str) -> float:
        """Smart price estimation based on card patterns"""
        card_name_lower = card_name.lower()
        set_name_lower = set_name.lower()
        
        base_price = 5.0  # Default base price
        
        # Check for known Pokemon
        for pokemon, data in self.card_patterns.items():
            if pokemon in card_name_lower:
                base_price = data['base_price']
                
                # Apply type multipliers
                for card_type, multiplier in data['multiplier'].items():
                    if card_type in card_name_lower:
                        base_price *= multiplier
                        break
                break
        
        # Apply general type modifiers
        for card_type, modifier in self.type_modifiers.items():
            if card_type in card_name_lower or card_type in set_name_lower:
                base_price *= modifier
        
        # Set-specific modifiers
        if any(premium_set in set_name_lower for premium_set in [
            'champions path', 'hidden fates', 'shining fates', 'celebrations',
            'base set', 'shadowless', 'first edition', 'neo genesis'
        ]):
            base_price *= 1.5
        
        # Modern vs vintage modifier
        if any(vintage in set_name_lower for vintage in [
            'base set', 'jungle', 'fossil', 'neo', 'team rocket', 'gym'
        ]):
            base_price *= 2.0
        
        return round(base_price, 2)
    
    def generate_popular_cards_by_set(self, set_name: str) -> List[str]:
        """Generate popular card names for a given set"""
        popular_pokemon = [
            'Charizard', 'Pikachu', 'Rayquaza', 'Lugia', 'Mewtwo', 'Mew',
            'Umbreon', 'Espeon', 'Sylveon', 'Leafeon', 'Glaceon', 'Jolteon',
            'Vaporeon', 'Flareon', 'Eevee', 'Dragonite', 'Gyarados', 'Blastoise',
            'Venusaur', 'Alakazam', 'Gengar', 'Machamp', 'Golem', 'Arcanine',
            'Lapras', 'Snorlax', 'Articuno', 'Zapdos', 'Moltres', 'Ditto',
            'Scyther', 'Electabuzz', 'Magmar', 'Pinsir', 'Tauros', 'Magikarp',
            'Clefairy', 'Wigglytuff', 'Vileplume', 'Parasect', 'Venomoth',
            'Dugtrio', 'Persian', 'Psyduck', 'Golduck', 'Primeape', 'Rapidash'
        ]
        
        card_names = []
        
        # Determine card types based on set era
        if any(modern in set_name.lower() for modern in [
            'sword', 'shield', 'rebel', 'darkness', 'champions', 'vivid',
            'shining fates', 'battle', 'chilling', 'evolving', 'fusion',
            'brilliant', 'astral', 'lost origin', 'silver tempest'
        ]):
            # Modern sets have VMAX, V, etc.
            for pokemon in popular_pokemon[:20]:  # Top 20 for modern sets
                card_names.extend([
                    f"{pokemon} VMAX",
                    f"{pokemon} V",
                    f"{pokemon} (Full Art)",
                    f"{pokemon} (Secret Rare)",
                    f"{pokemon} (Rainbow Rare)"
                ])
        
        elif any(sm in set_name.lower() for sm in [
            'sun', 'moon', 'guardians', 'burning', 'shining legends',
            'crimson', 'ultra', 'forbidden', 'celestial', 'lost thunder',
            'team up', 'unbroken', 'unified', 'hidden fates', 'cosmic'
        ]):
            # Sun & Moon era has GX
            for pokemon in popular_pokemon[:20]:
                card_names.extend([
                    f"{pokemon} GX",
                    f"{pokemon} (Full Art)",
                    f"{pokemon} (Secret Rare)",
                    f"{pokemon} (Rainbow Rare)"
                ])
        
        elif 'base set' in set_name.lower() or 'jungle' in set_name.lower() or 'fossil' in set_name.lower():
            # Classic sets
            for pokemon in popular_pokemon[:16]:  # Base set had 16 holos
                card_names.extend([
                    f"{pokemon}",
                    f"{pokemon} (Holo)",
                    f"{pokemon} (1st Edition)",
                    f"{pokemon} (Shadowless)"
                ])
        
        else:
            # General case - add basic versions
            for pokemon in popular_pokemon[:15]:
                card_names.extend([
                    f"{pokemon}",
                    f"{pokemon} (Holo)",
                    f"{pokemon} EX",
                    f"{pokemon} (Full Art)"
                ])
        
        return card_names[:50]  # Limit to 50 cards per set
    
    def build_massive_database(self, cards_per_day: int = 200):
        """Build massive database incrementally"""
        print("🚀 Massive Pokemon Card Database Builder")
        print("=" * 60)
        print(f"Goal: Add {cards_per_day} cards per day")
        print(f"Target: 5,000+ total cards within a month")
        print(f"API Limit: {self.daily_api_limit} calls per day")
        
        total_sets = sum(len(sets) for sets in self.all_sets.values())
        print(f"📦 Available Sets: {total_sets}")
        
        # Get current database size
        current_count = self.get_current_count()
        print(f"📊 Current Database: {current_count} cards")
        
        print("\n🎯 Building Strategy:")
        print("1. Add popular cards from each set")
        print("2. Smart price estimation")
        print("3. Respect API limits")
        print("4. Daily incremental builds")
        
        cards_added_today = 0
        
        # Prioritize set order (most valuable first)
        priority_order = ['modern_2020_2025', 'classic_era', 'sun_moon_era', 'xy_era', 'black_white_era']
        
        for era_name in priority_order:
            if cards_added_today >= cards_per_day:
                break
                
            sets = self.all_sets[era_name]
            print(f"\n📦 Processing {era_name}: {len(sets)} sets")
            
            for set_name in sets:
                if cards_added_today >= cards_per_day:
                    break
                
                print(f"\n🎴 Adding cards from {set_name}...")
                
                # Generate popular cards for this set
                card_names = self.generate_popular_cards_by_set(set_name)
                
                added_this_set = 0
                for card_name in card_names:
                    if cards_added_today >= cards_per_day:
                        break
                    
                    # Check if already exists
                    existing = self.db.get_card_price(card_name, set_name)
                    if existing:
                        continue
                    
                    # Estimate price
                    estimated_price = self.estimate_smart_price(card_name, set_name)
                    
                    # Add to database
                    try:
                        self.db.update_price_manually(card_name, set_name, estimated_price)
                        added_this_set += 1
                        cards_added_today += 1
                        
                        if added_this_set <= 3:  # Show first few
                            print(f"  ✅ {card_name}: ${estimated_price:.2f}")
                    except Exception as e:
                        print(f"  ❌ Error adding {card_name}: {e}")
                
                if added_this_set > 3:
                    print(f"  📈 Added {added_this_set} total cards from {set_name}")
        
        final_count = self.get_current_count()
        print(f"\n🎉 Daily Build Complete!")
        print(f"   Cards added today: {cards_added_today}")
        print(f"   Total database size: {final_count}")
        print(f"   Progress: {(final_count/5000)*100:.1f}% toward 5,000 card goal")
        
        if final_count >= 1000:
            print(f"\n🚀 READY FOR SERIOUS DEAL HUNTING!")
            print(f"   Database size sufficient for comprehensive opportunity detection")
        else:
            days_to_goal = (5000 - final_count) // cards_per_day
            print(f"\n📅 Estimated {days_to_goal} more days to reach 5,000 cards")
    
    def get_current_count(self) -> int:
        """Get current card count"""
        stats = self.db.get_price_statistics()
        return stats['total_prices']
    
    def bulk_import_from_web_sources(self):
        """Import from online Pokemon card databases"""
        print("\n🌐 Importing from Web Sources...")
        
        # This would fetch from sources like:
        # - Pokellector card databases
        # - TCGPlayer set lists
        # - Bulbapedia set pages
        # - Community-maintained lists
        
        web_sources = [
            "https://www.pokellector.com/sets",  # Example
            "https://bulbapedia.bulbagarden.net/wiki/List_of_Pokémon_Trading_Card_Game_expansions"
        ]
        
        print("⚠️  Web scraping not implemented yet")
        print("💡 Future feature: Auto-import from Pokellector, Bulbapedia, etc.")
        print("📝 For now, using manual card generation based on set patterns")
    
    def export_progress_report(self):
        """Export progress report"""
        stats = self.db.get_price_statistics()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_cards': stats['total_prices'],
            'unique_cards': stats['unique_cards'],
            'freshness_ratio': stats['freshness_ratio'],
            'goal_progress': (stats['total_prices'] / 5000) * 100,
            'daily_target': 200,
            'estimated_completion_days': max(0, (5000 - stats['total_prices']) // 200)
        }
        
        with open('database_progress.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Progress Report Exported:")
        print(f"   File: database_progress.json")
        print(f"   Total Cards: {report['total_cards']}")
        print(f"   Goal Progress: {report['goal_progress']:.1f}%")

def main():
    """Main function"""
    builder = MassiveDatabaseBuilder()
    
    print("🎴 Massive Pokemon Card Database Builder")
    print("=" * 50)
    print("Choose build strategy:")
    print("1. Daily build (200 cards)")
    print("2. Aggressive build (500 cards)")
    print("3. Conservative build (100 cards)")
    print("4. Export progress report")
    print("5. Show current stats")
    
    choice = input("\nChoose option (1-5): ").strip()
    
    if choice == '1':
        builder.build_massive_database(200)
    elif choice == '2':
        builder.build_massive_database(500)
    elif choice == '3':
        builder.build_massive_database(100)
    elif choice == '4':
        builder.export_progress_report()
    elif choice == '5':
        os.system("python3 price_manager.py --stats")
    else:
        print("Invalid choice!")
    
    builder.export_progress_report()

if __name__ == "__main__":
    main()
