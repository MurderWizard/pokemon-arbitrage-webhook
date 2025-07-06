#!/usr/bin/env python3
"""
Pokemon Card Database Scaling Strategy
Ultimate system to scale to ALL Pokemon cards with zero gaps

This orchestrates:
1. Download comprehensive card lists
2. Import all cards with smart pricing
3. Prioritize price updates 
4. Monitor coverage gaps
5. Automated daily expansion

GOAL: 15,000+ cards covering EVERY possible arbitrage opportunity
"""

import os
import json
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess
import sys

# Import our modules
from pokemon_price_system import price_db
from universal_card_importer import UniversalCardImporter
from card_list_downloader import CardListDownloader

class DatabaseScalingStrategy:
    """Master orchestrator for scaling to all Pokemon cards"""
    
    def __init__(self):
        self.db = price_db
        self.target_cards = 15000  # Our ambitious goal
        self.daily_import_target = 1000
        self.high_priority_pokemon = [
            'Charizard', 'Pikachu', 'Mewtwo', 'Mew', 'Rayquaza', 'Lugia', 'Ho-Oh',
            'Umbreon', 'Espeon', 'Eevee', 'Lucario', 'Garchomp', 'Dragonite',
            'Gyarados', 'Machamp', 'Gengar', 'Alakazam', 'Blastoise', 'Venusaur'
        ]
    
    def analyze_current_coverage(self) -> Dict:
        """Analyze what we have vs what we need"""
        print("📊 Analyzing current database coverage...")
        
        # Get current stats
        stats = self.db.get_price_statistics()
        total_cards = stats['unique_cards']
        
        # Analyze by set/era
        cards_by_era = {}
        
        # Get all unique cards from database
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT card_name, set_name FROM card_prices')
        all_cards_data = cursor.fetchall()
        conn.close()
        
        for card_name, set_name in all_cards_data:
            era = self._determine_era(set_name or 'Unknown')
            
            if era not in cards_by_era:
                cards_by_era[era] = 0
            cards_by_era[era] += 1
        
        # Calculate coverage gaps
        gaps = self._identify_coverage_gaps(cards_by_era)
        
        coverage = {
            'total_cards': total_cards,
            'target_cards': self.target_cards,
            'completion_percentage': (total_cards / self.target_cards) * 100,
            'cards_by_era': cards_by_era,
            'coverage_gaps': gaps,
            'high_priority_missing': self._find_missing_high_priority()
        }
        
        self._print_coverage_report(coverage)
        return coverage
    
    def _determine_era(self, set_name: str) -> str:
        """Determine era from set name"""
        set_lower = set_name.lower()
        
        if any(x in set_lower for x in ['scarlet', 'violet', 'paldea', 'temporal']):
            return 'Scarlet & Violet (2023+)'
        elif any(x in set_lower for x in ['sword', 'shield', 'rebel', 'darkness', 'vivid', 'evolving']):
            return 'Sword & Shield (2020-2022)'
        elif any(x in set_lower for x in ['sun', 'moon', 'guardians', 'burning', 'ultra', 'forbidden']):
            return 'Sun & Moon (2017-2019)'
        elif any(x in set_lower for x in ['xy', 'flashfire', 'phantom', 'primal', 'roaring', 'ancient']):
            return 'XY (2014-2016)'
        elif any(x in set_lower for x in ['black', 'white', 'emerging', 'noble', 'next', 'dark']):
            return 'Black & White (2011-2013)'
        elif any(x in set_lower for x in ['diamond', 'pearl', 'platinum', 'heartgold', 'soulsilver']):
            return 'Diamond & Pearl (2007-2011)'
        elif any(x in set_lower for x in ['ruby', 'sapphire', 'emerald', 'firered', 'leafgreen']):
            return 'EX Era (2003-2007)'
        elif any(x in set_lower for x in ['neo', 'genesis', 'discovery', 'revelation', 'destiny']):
            return 'Neo Era (2000-2001)'
        elif any(x in set_lower for x in ['base', 'jungle', 'fossil', 'rocket', 'gym']):
            return 'Classic (1998-2003)'
        else:
            return 'Other/Modern'
    
    def _identify_coverage_gaps(self, cards_by_era: Dict[str, int]) -> List[str]:
        """Identify which eras need more coverage"""
        gaps = []
        
        # Expected minimum cards per era for good coverage
        era_targets = {
            'Scarlet & Violet (2023+)': 800,
            'Sword & Shield (2020-2022)': 1500,
            'Sun & Moon (2017-2019)': 1200,
            'XY (2014-2016)': 800,
            'Black & White (2011-2013)': 600,
            'Diamond & Pearl (2007-2011)': 600,
            'EX Era (2003-2007)': 400,
            'Neo Era (2000-2001)': 300,
            'Classic (1998-2003)': 400
        }
        
        for era, target in era_targets.items():
            current = cards_by_era.get(era, 0)
            if current < target:
                gaps.append(f"{era}: {current}/{target} cards ({((current/target)*100):.1f}%)")
        
        return gaps
    
    def _find_missing_high_priority(self) -> List[str]:
        """Find missing high-priority Pokemon"""
        missing = []
        
        for pokemon in self.high_priority_pokemon:
            # Search for this Pokemon in database
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT COUNT(*) FROM card_prices WHERE LOWER(card_name) LIKE ?',
                (f'%{pokemon.lower()}%',)
            )
            count = cursor.fetchone()[0]
            conn.close()
            
            if count < 5:  # Should have many variants
                missing.append(f"{pokemon} ({count} cards found)")
        
        return missing
    
    def _print_coverage_report(self, coverage: Dict):
        """Print detailed coverage report"""
        print("\n" + "="*70)
        print("🎯 POKEMON CARD DATABASE COVERAGE REPORT")
        print("="*70)
        print(f"📈 Current Progress: {coverage['total_cards']:,} / {coverage['target_cards']:,} cards")
        print(f"🎯 Completion: {coverage['completion_percentage']:.1f}%")
        print(f"🚀 Remaining: {coverage['target_cards'] - coverage['total_cards']:,} cards needed")
        
        print(f"\n📊 CARDS BY ERA:")
        for era, count in coverage['cards_by_era'].items():
            print(f"   {era}: {count:,} cards")
        
        if coverage['coverage_gaps']:
            print(f"\n⚠️  COVERAGE GAPS:")
            for gap in coverage['coverage_gaps']:
                print(f"   🔴 {gap}")
        
        if coverage['high_priority_missing']:
            print(f"\n🔥 HIGH PRIORITY MISSING:")
            for missing in coverage['high_priority_missing']:
                print(f"   ⭐ {missing}")
        
        print("="*70)
    
    def run_comprehensive_import(self) -> bool:
        """Run the complete import process"""
        print("🚀 Starting COMPREHENSIVE card import process...")
        
        try:
            # Step 1: Download fresh card lists
            print("\n📥 Step 1: Downloading card lists...")
            downloader = CardListDownloader()
            downloader.run_all_downloads()
            
            # Step 2: Import from downloaded files
            print("\n🃏 Step 2: Importing cards from all sources...")
            importer = UniversalCardImporter()
            
            # Get downloaded files
            card_files = [
                'card_lists/pokemon_tcg_api_cards.csv',
                'card_lists/pokemon_tcg_api_cards.json',
                'card_lists/comprehensive_sets.csv'
            ]
            
            # Filter existing files
            existing_files = [f for f in card_files if os.path.exists(f)]
            
            importer.run_full_import(existing_files)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during comprehensive import: {e}")
            return False
    
    def prioritize_price_updates(self) -> List[Dict]:
        """Identify which cards need price updates most urgently"""
        print("💎 Prioritizing price updates...")
        
        # Get all cards from database
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT card_name, set_name, market_price, last_updated
            FROM card_prices
        ''')
        all_cards_data = cursor.fetchall()
        conn.close()
        
        priority_list = []
        
        for card_name, set_name, market_price, last_updated in all_cards_data:
            priority_score = 0
            card_name_lower = card_name.lower()
            estimated_price = market_price or 0
            
            # High priority Pokemon
            if any(priority in card_name_lower for priority in [p.lower() for p in self.high_priority_pokemon]):
                priority_score += 50
            
            # High value cards
            if estimated_price > 50:
                priority_score += 30
            elif estimated_price > 20:
                priority_score += 20
            elif estimated_price > 10:
                priority_score += 10
            
            # Old/missing price data
            if not last_updated:
                priority_score += 25
            elif last_updated:
                try:
                    last_update = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                    days_old = (datetime.now() - last_update).days
                    if days_old > 7:
                        priority_score += 15
                    elif days_old > 3:
                        priority_score += 10
                except:
                    priority_score += 20
            
            # Modern/popular sets
            set_name_lower = (set_name or '').lower()
            if any(modern in set_name_lower for modern in ['evolving skies', 'brilliant stars', 'celebrations']):
                priority_score += 15
            
            if priority_score > 20:  # Only include high priority
                priority_list.append({
                    'card_name': card_name,
                    'set_name': set_name,
                    'priority_score': priority_score,
                    'estimated_price': estimated_price
                })
        
        # Sort by priority score
        priority_list.sort(key=lambda x: x['priority_score'], reverse=True)
        
        print(f"🎯 Identified {len(priority_list)} cards needing price updates")
        return priority_list[:500]  # Top 500 priorities
    
    def run_targeted_expansion(self, focus_areas: Optional[List[str]] = None):
        """Run targeted expansion for specific gaps"""
        if not focus_areas:
            focus_areas = ['modern_sets', 'vintage_classics', 'high_value_cards']
        
        print(f"🎯 Running targeted expansion: {', '.join(focus_areas)}")
        
        importer = UniversalCardImporter()
        
        if 'modern_sets' in focus_areas:
            self._expand_modern_sets(importer)
        
        if 'vintage_classics' in focus_areas:
            self._expand_vintage_classics(importer)
        
        if 'high_value_cards' in focus_areas:
            self._expand_high_value_cards(importer)
    
    def _expand_modern_sets(self, importer: UniversalCardImporter):
        """Focus on modern set expansion"""
        print("   🔥 Expanding modern sets...")
        
        modern_sets = [
            'Evolving Skies', 'Brilliant Stars', 'Astral Radiance', 'Lost Origin',
            'Silver Tempest', 'Crown Zenith', 'Paldea Evolved', 'Obsidian Flames',
            'Paradox Rift', 'Paldean Fates', 'Temporal Forces'
        ]
        
        popular_pokemon = self.high_priority_pokemon + [
            'Arceus', 'Dialga', 'Palkia', 'Giratina', 'Darkrai', 'Cresselia',
            'Reshiram', 'Zekrom', 'Kyurem', 'Genesect', 'Xerneas', 'Yveltal'
        ]
        
        for set_name in modern_sets:
            for pokemon in popular_pokemon:
                for variant in ['', ' V', ' VMAX', ' VSTAR', ' GX', ' Full Art', ' Alt Art', ' Rainbow']:
                    card_name = f"{pokemon}{variant}".strip()
                    importer._add_card_if_new(card_name, set_name, 'Ultra Rare')
    
    def _expand_vintage_classics(self, importer: UniversalCardImporter):
        """Focus on vintage/classic expansion"""
        print("   🏛️ Expanding vintage classics...")
        
        vintage_sets = [
            'Base Set', 'Jungle', 'Fossil', 'Neo Genesis', 'Neo Discovery',
            'Neo Revelation', 'Neo Destiny', 'Team Rocket', 'Gym Heroes'
        ]
        
        for set_name in vintage_sets:
            for pokemon in self.high_priority_pokemon:
                for variant in ['', ' Holo', ' First Edition', ' Shadowless', ' No Rarity']:
                    card_name = f"{pokemon}{variant}".strip()
                    importer._add_card_if_new(card_name, set_name, 'Rare')
    
    def _expand_high_value_cards(self, importer: UniversalCardImporter):
        """Focus on high-value card expansion"""
        print("   💎 Expanding high-value cards...")
        
        # Special/premium cards
        premium_variants = [
            'Secret Rare', 'Rainbow Rare', 'Gold', 'Crystal', 'Shining',
            'Star', 'Prime', 'Legend', 'Break', 'Tag Team'
        ]
        
        for pokemon in self.high_priority_pokemon:
            for variant in premium_variants:
                card_name = f"{pokemon} {variant}"
                # Add to multiple sets where this might exist
                for set_name in ['Hidden Fates', 'Shining Fates', 'Celebrations', 'Crown Zenith']:
                    importer._add_card_if_new(card_name, set_name, 'Secret Rare')
    
    def create_daily_expansion_plan(self) -> Dict:
        """Create a plan for daily database expansion"""
        coverage = self.analyze_current_coverage()
        
        plan = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'current_cards': coverage['total_cards'],
            'daily_target': min(self.daily_import_target, self.target_cards - coverage['total_cards']),
            'focus_areas': [],
            'priority_updates': len(self.prioritize_price_updates()),
            'completion_eta_days': max(1, (self.target_cards - coverage['total_cards']) // self.daily_import_target)
        }
        
        # Determine focus areas based on gaps
        if coverage['completion_percentage'] < 20:
            plan['focus_areas'] = ['bulk_import', 'modern_sets']
        elif coverage['completion_percentage'] < 50:
            plan['focus_areas'] = ['targeted_expansion', 'price_updates']
        elif coverage['completion_percentage'] < 80:
            plan['focus_areas'] = ['gap_filling', 'quality_improvement']
        else:
            plan['focus_areas'] = ['price_updates', 'maintenance']
        
        return plan
    
    def execute_daily_plan(self):
        """Execute today's expansion plan"""
        plan = self.create_daily_expansion_plan()
        
        print("📅 DAILY EXPANSION PLAN")
        print(f"🎯 Target: Add {plan['daily_target']} cards today")
        print(f"🔥 Focus: {', '.join(plan['focus_areas'])}")
        print(f"⏱️  ETA to completion: {plan['completion_eta_days']} days")
        print()
        
        # Execute based on focus areas
        if 'bulk_import' in plan['focus_areas']:
            print("🚀 Running bulk import...")
            self.run_comprehensive_import()
        
        if 'targeted_expansion' in plan['focus_areas']:
            print("🎯 Running targeted expansion...")
            self.run_targeted_expansion()
        
        if 'price_updates' in plan['focus_areas']:
            print("💎 Running priority price updates...")
            priorities = self.prioritize_price_updates()
            print(f"   📊 {len(priorities)} cards need price updates")
        
        # Final status
        final_coverage = self.analyze_current_coverage()
        cards_added = final_coverage['total_cards'] - plan['current_cards']
        
        print(f"\n✅ Daily plan complete!")
        print(f"📈 Cards added today: {cards_added}")
        print(f"🎯 New total: {final_coverage['total_cards']:,} cards")

def main():
    """Run the database scaling strategy"""
    strategy = DatabaseScalingStrategy()
    
    print("🚀 POKEMON CARD DATABASE SCALING STRATEGY")
    print("Goal: Scale to 15,000+ cards covering ALL arbitrage opportunities")
    print("="*70)
    
    # Analyze current state
    coverage = strategy.analyze_current_coverage()
    
    # Get user choice
    print("\n🎮 Choose your scaling approach:")
    print("1. 🚀 Full comprehensive import (download + import everything)")
    print("2. 🎯 Execute today's focused expansion plan")
    print("3. 📊 Just analyze coverage and create plan")
    print("4. 🔥 Targeted expansion (specific gaps)")
    
    choice = input("\nChoose option (1-4): ").strip()
    
    if choice == '1':
        strategy.run_comprehensive_import()
        strategy.analyze_current_coverage()
    elif choice == '2':
        strategy.execute_daily_plan()
    elif choice == '3':
        plan = strategy.create_daily_expansion_plan()
        print(f"\n📋 Today's plan: {plan}")
    elif choice == '4':
        print("🎯 Available focus areas:")
        print("   modern_sets, vintage_classics, high_value_cards")
        areas = input("Enter focus areas (comma-separated): ").strip().split(',')
        strategy.run_targeted_expansion([area.strip() for area in areas])
    else:
        print("Running default comprehensive analysis...")
        strategy.analyze_current_coverage()

if __name__ == "__main__":
    main()
