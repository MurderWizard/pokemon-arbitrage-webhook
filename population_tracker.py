#!/usr/bin/env python3
"""
Population Tracker - Track graded card populations and their impact on prices
Integrates with PSA, BGS, and CGC population reports
"""
import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class PopulationTracker:
    def __init__(self):
        self.pop_data_file = "card_populations.json"
        self.pop_data = self._load_pop_data()
        
    def _load_pop_data(self) -> Dict:
        """Load existing population data"""
        if os.path.exists(self.pop_data_file):
            with open(self.pop_data_file, 'r') as f:
                return json.load(f)
        return {
            "last_update": None,
            "populations": {},
            "price_impacts": {}
        }
    
    def _save_pop_data(self):
        """Save population data to file"""
        with open(self.pop_data_file, 'w') as f:
            json.dump(self.pop_data, f, indent=4)
    
    def get_population_data(self, card_name: str, set_name: str) -> Dict:
        """Get population data for a specific card"""
        key = f"{card_name}|{set_name}"
        return self.pop_data["populations"].get(key, {
            "PSA": {"10": 0, "9": 0, "8": 0, "7": 0, "total": 0},
            "BGS": {"10": 0, "9.5": 0, "9": 0, "8.5": 0, "total": 0},
            "CGC": {"10": 0, "9.5": 0, "9": 0, "8.5": 0, "total": 0},
            "raw_estimate": 0,
            "last_update": None
        })
    
    def update_population(self, card_name: str, set_name: str, 
                         grading_company: str, pop_data: Dict):
        """Update population data for a card"""
        key = f"{card_name}|{set_name}"
        if key not in self.pop_data["populations"]:
            self.pop_data["populations"][key] = {
                "PSA": {"10": 0, "9": 0, "8": 0, "7": 0, "total": 0},
                "BGS": {"10": 0, "9.5": 0, "9": 0, "8.5": 0, "total": 0},
                "CGC": {"10": 0, "9.5": 0, "9": 0, "8.5": 0, "total": 0},
                "raw_estimate": 0,
                "last_update": None
            }
        
        self.pop_data["populations"][key][grading_company] = pop_data
        self.pop_data["populations"][key]["last_update"] = datetime.now().isoformat()
        self._save_pop_data()
    
    def calculate_price_impact(self, card_name: str, set_name: str, 
                             base_price: float) -> Tuple[float, float]:
        """
        Calculate price impact based on population
        Returns: (adjusted_price, population_multiplier)
        """
        pop_data = self.get_population_data(card_name, set_name)
        
        # Total graded population across all companies
        total_graded = (
            pop_data["PSA"]["total"] + 
            pop_data["BGS"]["total"] + 
            pop_data["CGC"]["total"]
        )
        
        # Gem Mint population (PSA 10, BGS 9.5+, CGC 9.5+)
        gem_mint_pop = (
            pop_data["PSA"]["10"] + 
            pop_data["BGS"]["10"] + pop_data["BGS"]["9.5"] +
            pop_data["CGC"]["10"] + pop_data["CGC"]["9.5"]
        )
        
        # Population-based multipliers
        if total_graded == 0:
            return base_price, 1.0  # No population data
            
        if gem_mint_pop < 10:
            multiplier = 2.5  # Ultra rare
        elif gem_mint_pop < 50:
            multiplier = 1.8  # Very rare
        elif gem_mint_pop < 100:
            multiplier = 1.5  # Rare
        elif gem_mint_pop < 500:
            multiplier = 1.2  # Uncommon
        elif gem_mint_pop < 1000:
            multiplier = 1.0  # Common
        else:
            multiplier = 0.8  # Very common
            
        # Additional rarity adjustments
        if total_graded < 100:
            multiplier *= 1.3  # Overall scarce card
        
        adjusted_price = base_price * multiplier
        return adjusted_price, multiplier
    
    def get_population_summary(self, card_name: str, set_name: str) -> str:
        """Get a human-readable population summary"""
        pop_data = self.get_population_data(card_name, set_name)
        
        total_graded = (
            pop_data["PSA"]["total"] + 
            pop_data["BGS"]["total"] + 
            pop_data["CGC"]["total"]
        )
        
        gem_mint = (
            pop_data["PSA"]["10"] + 
            pop_data["BGS"]["10"] + pop_data["BGS"]["9.5"] +
            pop_data["CGC"]["10"] + pop_data["CGC"]["9.5"]
        )
        
        return (
            f"Population Summary for {card_name} ({set_name}):\n"
            f"Total Graded: {total_graded}\n"
            f"Gem Mint: {gem_mint}\n"
            f"PSA 10: {pop_data['PSA']['10']}\n"
            f"BGS 9.5+: {pop_data['BGS']['10'] + pop_data['BGS']['9.5']}\n"
            f"CGC 9.5+: {pop_data['CGC']['10'] + pop_data['CGC']['9.5']}\n"
            f"Raw Estimate: {pop_data['raw_estimate']}\n"
            f"Last Updated: {pop_data['last_update'] or 'Never'}"
        )

def test_population_tracker():
    """Test the population tracker functionality"""
    tracker = PopulationTracker()
    
    # Test card: Charizard VMAX from Champions Path
    card_name = "Charizard VMAX"
    set_name = "Champions Path"
    
    # Sample population data
    psa_data = {
        "10": 250,  # PSA 10
        "9": 150,   # PSA 9
        "8": 50,    # PSA 8
        "7": 25,    # PSA 7
        "total": 475
    }
    
    # Update population
    tracker.update_population(card_name, set_name, "PSA", psa_data)
    
    # Test price impact
    base_price = 500.00
    adjusted_price, multiplier = tracker.calculate_price_impact(card_name, set_name, base_price)
    
    print(f"Population Test Results:")
    print("=" * 50)
    print(tracker.get_population_summary(card_name, set_name))
    print(f"\nPrice Analysis:")
    print(f"Base Price: ${base_price:.2f}")
    print(f"Population Multiplier: {multiplier:.2f}x")
    print(f"Adjusted Price: ${adjusted_price:.2f}")

if __name__ == "__main__":
    test_population_tracker()
