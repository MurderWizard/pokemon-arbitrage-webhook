#!/usr/bin/env python3
"""
Universal Card Coverage Expander
Systematically expand to 10,000+ cards for 100% market coverage
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
from ebay_browse_api_integration import EbayBrowseAPI
from pokemon_price_system import price_db
import logging

class UniversalCardCoverageExpander:
    """Professional-grade card coverage expansion system"""
    
    def __init__(self):
        self.browse_api = EbayBrowseAPI()
        self.price_db = price_db
        self.target_coverage = 10000  # Professional level
        self.cards_added_today = 0
        self.max_cards_per_day = 500  # Rate limiting
        
        # Comprehensive card universe definition
        self.card_universe = {
            'modern_era': {
                'sets': [
                    'Sword & Shield Base', 'Rebel Clash', 'Darkness Ablaze',
                    'Champions Path', 'Vivid Voltage', 'Shining Fates',
                    'Battle Styles', 'Chilling Reign', 'Evolving Skies',
                    'Celebrations', 'Fusion Strike', 'Brilliant Stars',
                    'Astral Radiance', 'Pokemon Go', 'Lost Origin',
                    'Silver Tempest', 'Crown Zenith', 'Scarlet & Violet Base',
                    'Paldea Evolved', 'Obsidian Flames', 'Paradox Rift'
                ],
                'card_types': ['V', 'VMAX', 'VSTAR', 'ex', 'Full Art', 'Secret Rare', 'Alternate Art'],
                'estimated_cards': 2500,
                'priority': 'HIGH'
            },
            'classic_era': {
                'sets': [
                    'Base Set', 'Jungle', 'Fossil', 'Base Set 2',
                    'Team Rocket', 'Gym Heroes', 'Gym Challenge',
                    'Neo Genesis', 'Neo Discovery', 'Neo Destiny', 'Neo Revelation'
                ],
                'card_types': ['Holo', 'First Edition', 'Shadowless', '1st Edition'],
                'estimated_cards': 1500,
                'priority': 'HIGH'
            },
            'vintage_era': {
                'sets': [
                    'Japanese Base Set', 'Trophy Cards', 'Promo Cards',
                    'Southern Islands', 'Vending Series', 'E-Card Series'
                ],
                'card_types': ['PSA Graded', 'BGS Graded', 'CGC Graded'],
                'estimated_cards': 3000,
                'priority': 'MEDIUM'
            },
            'trending_modern': {
                'sets': ['Latest releases', 'Popular reprints', 'Special collections'],
                'card_types': ['Chase cards', 'Meta cards', 'Influencer cards'],
                'estimated_cards': 1000,
                'priority': 'DYNAMIC'
            }
        }
        
        # High-value Pokemon for targeted expansion
        self.priority_pokemon = [
            'Charizard', 'Pikachu', 'Lugia', 'Rayquaza', 'Umbreon', 'Espeon',
            'Mew', 'Mewtwo', 'Dragonite', 'Gyarados', 'Blastoise', 'Venusaur',
            'Alakazam', 'Machamp', 'Gengar', 'Lapras', 'Snorlax', 'Eevee',
            'Vaporeon', 'Jolteon', 'Flareon', 'Leafeon', 'Glaceon', 'Sylveon'
        ]
        
    def systematic_universe_expansion(self):
        """Systematically expand coverage across the entire card universe"""
        
        print("🚀 UNIVERSAL CARD COVERAGE EXPANSION")
        print("=" * 50)
        print(f"Target: {self.target_coverage:,} cards for professional coverage")
        
        expansion_summary = {
            'total_added': 0,
            'by_era': {},
            'by_priority': {},
            'time_taken': 0
        }
        
        start_time = time.time()
        
        # Process each era systematically
        for era_name, era_data in self.card_universe.items():
            if self.cards_added_today >= self.max_cards_per_day:
                print(f"⚠️ Daily limit reached ({self.max_cards_per_day} cards)")
                break
                
            print(f"\n📦 Processing {era_name.replace('_', ' ').title()}")
            print(f"   Sets: {len(era_data['sets'])}")
            print(f"   Priority: {era_data['priority']}")
            
            era_added = self.process_era(era_name, era_data)
            expansion_summary['by_era'][era_name] = era_added
            expansion_summary['total_added'] += era_added
            
        expansion_summary['time_taken'] = time.time() - start_time
        
        # Generate completion report
        self.generate_expansion_report(expansion_summary)
        
        return expansion_summary
    
    def process_era(self, era_name: str, era_data: Dict) -> int:
        """Process all cards for a specific era"""
        
        cards_added = 0
        
        # Process each set in the era
        for set_name in era_data['sets']:
            if self.cards_added_today >= self.max_cards_per_day:
                break
                
            print(f"   🔍 Processing set: {set_name}")
            
            # Process each card type
            for card_type in era_data['card_types']:
                if self.cards_added_today >= self.max_cards_per_day:
                    break
                    
                set_cards_added = self.process_set_and_type(set_name, card_type)
                cards_added += set_cards_added
                
                # Rate limiting
                time.sleep(0.5)  # Respectful API usage
                
        return cards_added
    
    def process_set_and_type(self, set_name: str, card_type: str) -> int:
        """Process all cards for a specific set and card type combination"""
        
        cards_added = 0
        
        # Generate search queries for this combination
        search_queries = self.generate_search_queries(set_name, card_type)
        
        for query in search_queries:
            if self.cards_added_today >= self.max_cards_per_day:
                break
                
            try:
                # Search using Browse API
                items = self.browse_api.search_pokemon_cards(
                    query,
                    min_price=1,
                    max_price=10000,
                    limit=100
                )
                
                print(f"      📋 Query '{query}': {len(items)} listings found")
                
                # Process found items
                for item in items[:20]:  # Process top 20 per query
                    if self.cards_added_today >= self.max_cards_per_day:
                        break
                        
                    card_data = self.extract_card_data(item, set_name, card_type)
                    if card_data and self.should_add_card(card_data):
                        self.add_card_to_database(card_data)
                        cards_added += 1
                        self.cards_added_today += 1
                        
            except Exception as e:
                print(f"      ⚠️ Error processing query '{query}': {e}")
                continue
                
        return cards_added
    
    def generate_search_queries(self, set_name: str, card_type: str) -> List[str]:
        """Generate comprehensive search queries for set and card type"""
        
        queries = []
        
        # Basic set + type combinations
        queries.append(f"pokemon {set_name} {card_type}")
        
        # Add priority Pokemon to the search
        for pokemon in self.priority_pokemon[:5]:  # Top 5 for each query
            queries.append(f"{pokemon} {set_name} {card_type}")
            
        # Special variations
        if 'First Edition' in card_type or '1st Edition' in card_type:
            queries.append(f"pokemon {set_name} first edition")
            
        if 'PSA' in card_type or 'BGS' in card_type:
            queries.append(f"pokemon {set_name} graded PSA BGS")
            
        return queries[:3]  # Limit to prevent API overuse
    
    def extract_card_data(self, item: Dict, set_name: str, card_type: str) -> Optional[Dict]:
        """Extract standardized card data from eBay item"""
        
        try:
            title = item.get('title', '')
            price = item.get('total_price', 0)
            
            # Parse card name from title
            card_name = self.parse_card_name_from_title(title)
            if not card_name:
                return None
                
            # Create standardized card data
            card_data = {
                'name': card_name,
                'set': set_name,
                'type': card_type,
                'market_price': price,
                'condition': self.parse_condition_from_title(title),
                'grading': self.parse_grading_from_title(title),
                'source': 'eBay_Browse_API',
                'timestamp': datetime.now().isoformat(),
                'ebay_item_id': item.get('item_id'),
                'confidence': self.calculate_confidence(title, price)
            }
            
            return card_data
            
        except Exception as e:
            print(f"      ⚠️ Error extracting card data: {e}")
            return None
    
    def parse_card_name_from_title(self, title: str) -> Optional[str]:
        """Parse Pokemon card name from eBay title"""
        
        # Remove common noise words
        noise_words = ['pokemon', 'card', 'tcg', 'holo', 'rare', 'mint', 'nm', 'lp']
        title_words = title.lower().split()
        
        # Look for Pokemon names
        for pokemon in self.priority_pokemon:
            if pokemon.lower() in title.lower():
                return pokemon
                
        # Fallback: try to extract card name
        for word in title_words:
            if len(word) > 3 and word not in noise_words:
                return word.title()
                
        return None
    
    def parse_condition_from_title(self, title: str) -> str:
        """Parse card condition from title"""
        
        title_lower = title.lower()
        
        if 'mint' in title_lower or 'nm' in title_lower:
            return 'Near Mint'
        elif 'lightly played' in title_lower or 'lp' in title_lower:
            return 'Lightly Played'
        elif 'moderately played' in title_lower or 'mp' in title_lower:
            return 'Moderately Played'
        elif 'heavily played' in title_lower or 'hp' in title_lower:
            return 'Heavily Played'
        elif 'damaged' in title_lower:
            return 'Damaged'
        else:
            return 'Unknown'
    
    def parse_grading_from_title(self, title: str) -> Optional[str]:
        """Parse grading information from title"""
        
        title_upper = title.upper()
        
        if 'PSA' in title_upper:
            # Look for PSA grade
            import re
            psa_match = re.search(r'PSA\s*(\d+)', title_upper)
            if psa_match:
                return f"PSA {psa_match.group(1)}"
            return "PSA"
            
        elif 'BGS' in title_upper:
            bgs_match = re.search(r'BGS\s*(\d+)', title_upper)
            if bgs_match:
                return f"BGS {bgs_match.group(1)}"
            return "BGS"
            
        elif 'CGC' in title_upper:
            cgc_match = re.search(r'CGC\s*(\d+)', title_upper)
            if cgc_match:
                return f"CGC {cgc_match.group(1)}"
            return "CGC"
            
        return None
    
    def calculate_confidence(self, title: str, price: float) -> float:
        """Calculate confidence score for extracted data"""
        
        confidence = 0.5  # Base confidence
        
        # Title quality indicators
        if len(title.split()) >= 4:
            confidence += 0.1
            
        # Price reasonableness
        if 1 <= price <= 10000:
            confidence += 0.2
            
        # Pokemon name found
        for pokemon in self.priority_pokemon:
            if pokemon.lower() in title.lower():
                confidence += 0.2
                break
                
        return min(confidence, 1.0)
    
    def should_add_card(self, card_data: Dict) -> bool:
        """Determine if card should be added to database"""
        
        # Quality checks
        if card_data['confidence'] < 0.6:
            return False
            
        if card_data['market_price'] < 1:
            return False
            
        # Check if card already exists
        existing_price = self.price_db.get_card_price(
            card_data['name'], 
            card_data['set']
        )
        
        if existing_price:
            return False  # Already have this card
            
        return True
    
    def add_card_to_database(self, card_data: Dict):
        """Add card to price database"""
        
        try:
            self.price_db.add_card_price(
                card_name=card_data['name'],
                set_name=card_data['set'],
                market_price=card_data['market_price'],
                condition=card_data['condition'],
                source='Universal_Expansion',
                metadata={
                    'card_type': card_data['type'],
                    'grading': card_data['grading'],
                    'confidence': card_data['confidence'],
                    'ebay_item_id': card_data['ebay_item_id']
                }
            )
            
            print(f"        ✅ Added: {card_data['name']} ({card_data['set']}) - ${card_data['market_price']:.2f}")
            
        except Exception as e:
            print(f"        ❌ Failed to add card: {e}")
    
    def generate_expansion_report(self, summary: Dict):
        """Generate comprehensive expansion report"""
        
        print(f"\n📊 EXPANSION COMPLETE")
        print("=" * 40)
        print(f"🎯 Total cards added: {summary['total_added']}")
        print(f"⏱️ Time taken: {summary['time_taken']:.1f} seconds")
        print(f"⚡ Cards per minute: {summary['total_added'] / (summary['time_taken'] / 60):.1f}")
        
        print(f"\n📦 BY ERA:")
        for era, count in summary['by_era'].items():
            print(f"   {era.replace('_', ' ').title()}: {count} cards")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'expansion_summary': summary,
            'target_coverage': self.target_coverage,
            'daily_progress': self.cards_added_today
        }
        
        with open('expansion_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"\n💾 Detailed report saved to: expansion_report.json")

def main():
    """Run universal card coverage expansion"""
    
    expander = UniversalCardCoverageExpander()
    
    # Check current coverage
    current_stats = expander.price_db.get_price_statistics()
    print(f"📊 Current coverage: {current_stats.get('unique_cards', 0)} cards")
    
    # Run expansion
    results = expander.systematic_universe_expansion()
    
    # Show final status
    final_stats = expander.price_db.get_price_statistics()
    print(f"🎉 Final coverage: {final_stats.get('unique_cards', 0)} cards")
    print(f"📈 Improvement: +{results['total_added']} cards")

if __name__ == "__main__":
    main()
