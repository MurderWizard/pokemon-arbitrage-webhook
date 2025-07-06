#!/usr/bin/env python3
"""
Price Catalog Manager
Load and work with the base price catalog
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class CardPrice:
    name: str
    set_name: str
    price: float
    priority: str
    notes: str
    tier: str

class PriceCatalog:
    """Manage the base price catalog"""
    
    def __init__(self, catalog_path: str = "base_price_catalog.json"):
        self.catalog_path = catalog_path
        self.load_catalog()
    
    def load_catalog(self):
        """Load the price catalog from JSON"""
        with open(self.catalog_path, 'r') as f:
            self.catalog = json.load(f)
            
        # Quick validation
        if 'meta' not in self.catalog or 'price_tiers' not in self.catalog:
            raise ValueError("Invalid catalog format")
    
    def get_base_price(self, card_name: str, set_name: str) -> Optional[CardPrice]:
        """Get base price info for a card"""
        for tier_name, tier_data in self.catalog['price_tiers'].items():
            for card, card_data in tier_data['cards'].items():
                if card.lower() == card_name.lower():
                    # Check set match
                    for catalog_set, price in card_data['sets'].items():
                        if catalog_set.lower() == set_name.lower() or catalog_set == "Various Sets":
                            return CardPrice(
                                name=card,
                                set_name=set_name,
                                price=price,
                                priority=card_data['priority'],
                                notes=card_data['notes'],
                                tier=tier_name
                            )
        return None
    
    def get_condition_modifier(self, condition: str) -> float:
        """Get price modifier for card condition"""
        return self.catalog['card_conditions'].get(condition, 1.0)
    
    def get_grading_modifier(self, grade: str) -> float:
        """Get price modifier for graded cards"""
        return self.catalog['grading_multipliers'].get(grade, 1.0)
    
    def estimate_price(self, card_name: str, set_name: str, 
                      condition: str = "Near Mint", grade: Optional[str] = None) -> Optional[float]:
        """Estimate current price with modifiers"""
        base = self.get_base_price(card_name, set_name)
        if not base:
            return None
            
        price = base.price
        
        # Apply condition modifier if not graded
        if not grade:
            price *= self.get_condition_modifier(condition)
        # Apply grading modifier if graded
        else:
            price *= self.get_grading_modifier(grade)
            
        return round(price, 2)
    
    def get_priority_sets(self) -> Dict[str, List[str]]:
        """Get sets by priority tier"""
        return self.catalog['set_priorities']
    
    def get_cards_in_range(self, min_price: float = 0, max_price: float = float('inf')) -> List[CardPrice]:
        """Get all cards in a price range"""
        cards = []
        
        for tier_name, tier_data in self.catalog['price_tiers'].items():
            for card_name, card_data in tier_data['cards'].items():
                for set_name, price in card_data['sets'].items():
                    if min_price <= price <= max_price:
                        cards.append(CardPrice(
                            name=card_name,
                            set_name=set_name,
                            price=price,
                            priority=card_data['priority'],
                            notes=card_data['notes'],
                            tier=tier_name
                        ))
        
        return sorted(cards, key=lambda x: x.price, reverse=True)
    
    def display_catalog_summary(self):
        """Display a summary of the catalog"""
        print("\n📊 Price Catalog Summary")
        print("=" * 50)
        
        # Count cards by tier
        total_cards = 0
        for tier_name, tier_data in self.catalog['price_tiers'].items():
            card_count = sum(len(card_data['sets']) for card_data in tier_data['cards'].values())
            total_cards += card_count
            
            print(f"\n{tier_name.replace('_', ' ').title()}:")
            print(f"  • Cards: {card_count}")
            print(f"  • Description: {tier_data['description']}")
            
            # Show sample cards
            print("  • Sample Cards:")
            for card_name, card_data in list(tier_data['cards'].items())[:2]:
                for set_name, price in list(card_data['sets'].items())[:1]:
                    print(f"    - {card_name} ({set_name}): ${price:.2f}")
        
        print("\nSet Priorities:")
        for priority, sets in self.catalog['set_priorities'].items():
            print(f"  • {priority.replace('_', ' ').title()}: {len(sets)} sets")
        
        print(f"\nTotal Cards: {total_cards}")
        print(f"Last Updated: {self.catalog['meta']['last_updated']}")

def main():
    """Test the price catalog"""
    catalog = PriceCatalog()
    
    # Display summary
    catalog.display_catalog_summary()
    
    # Test some lookups
    print("\n🔍 Test Lookups:")
    
    test_cards = [
        ("Charizard VMAX (Secret)", "Champions Path"),
        ("Pikachu V", "Vivid Voltage"),
        ("Base Set Holos", "Base Set")
    ]
    
    for card_name, set_name in test_cards:
        base = catalog.get_base_price(card_name, set_name)
        if base:
            print(f"\n{card_name} ({set_name}):")
            print(f"  • Base Price: ${base.price:.2f}")
            print(f"  • Priority: {base.priority}")
            print(f"  • Tier: {base.tier}")
            print(f"  • Notes: {base.notes}")
            
            # Test condition/grade estimates
            nm_price = catalog.estimate_price(card_name, set_name, "Near Mint")
            lp_price = catalog.estimate_price(card_name, set_name, "Lightly Played")
            psa10_price = catalog.estimate_price(card_name, set_name, grade="PSA 10")
            
            print("  • Estimated Prices:")
            print(f"    - NM: ${nm_price:.2f}")
            print(f"    - LP: ${lp_price:.2f}")
            print(f"    - PSA 10: ${psa10_price:.2f}")

if __name__ == "__main__":
    main()
