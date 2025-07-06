#!/usr/bin/env python3
"""
Set Information and Reprint Impact Calculator
Tracks set releases and calculates price modifiers based on reprints
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class SetInfo:
    name: str
    release_date: str
    rotation_status: str
    market_status: str
    total_cards: int
    print_waves: List[Dict]
    special_notes: Optional[str] = None
    expected_rotation: Optional[str] = None

@dataclass
class PrintWave:
    date: str
    type: str
    impact_modifier: float

class SetCatalog:
    """Manage set information and calculate reprint impacts"""
    
    def __init__(self, catalog_path: str = "set_catalog.json"):
        self.catalog_path = catalog_path
        self.load_catalog()
    
    def load_catalog(self):
        """Load the set catalog"""
        with open(self.catalog_path, 'r') as f:
            self.catalog = json.load(f)
    
    def get_set_info(self, set_name: str) -> Optional[SetInfo]:
        """Get information about a specific set"""
        for era in self.catalog['set_info'].values():
            if set_name in era:
                data = era[set_name]
                return SetInfo(
                    name=set_name,
                    release_date=data['release_date'],
                    rotation_status=data['rotation_status'],
                    market_status=data['market_status'],
                    total_cards=data['total_cards'],
                    print_waves=data['print_waves'],
                    special_notes=data.get('special_notes'),
                    expected_rotation=data.get('expected_rotation')
                )
        return None
    
    def get_latest_print_wave(self, set_name: str) -> Optional[PrintWave]:
        """Get the most recent print wave for a set"""
        set_info = self.get_set_info(set_name)
        if not set_info or not set_info.print_waves:
            return None
            
        latest = max(set_info.print_waves, key=lambda x: x['date'])
        
        # Calculate impact modifier
        rules = self.catalog['reprint_impact_rules']['special_set' if set_info.special_notes else 'standard_set']
        modifier = rules.get(latest['type'], 1.0)
        
        return PrintWave(
            date=latest['date'],
            type=latest['type'],
            impact_modifier=modifier
        )
    
    def calculate_price_modifier(self, set_name: str) -> float:
        """Calculate current price modifier based on all factors"""
        set_info = self.get_set_info(set_name)
        if not set_info:
            return 1.0
            
        modifier = 1.0
        
        # 1. Market status impact
        market_mod = self.catalog['market_status_modifiers'].get(set_info.market_status, 1.0)
        modifier *= market_mod
        
        # 2. Rotation status impact
        if set_info.rotation_status == 'standard':
            rotation_rules = self.catalog['rotation_impact']['standard']
            if set_info.expected_rotation and datetime.now().year == int(set_info.expected_rotation):
                modifier *= rotation_rules['pre_rotation']
            else:
                modifier *= rotation_rules['established']
        elif set_info.rotation_status == 'expanded':
            rotation_rules = self.catalog['rotation_impact']['expanded']
            modifier *= rotation_rules['stabilized']
        
        # 3. Latest print wave impact
        latest_wave = self.get_latest_print_wave(set_name)
        if latest_wave:
            modifier *= latest_wave.impact_modifier
        
        return round(modifier, 2)
    
    def should_adjust_price(self, set_name: str) -> Tuple[bool, str, float]:
        """Determine if a set's prices need adjustment"""
        set_info = self.get_set_info(set_name)
        if not set_info:
            return False, "Set not found", 1.0
            
        modifier = self.calculate_price_modifier(set_name)
        latest_wave = self.get_latest_print_wave(set_name)
        
        # Check if recent reprint
        if latest_wave:
            wave_date = datetime.strptime(latest_wave.date, "%Y-%m-%d")
            days_since_wave = (datetime.now() - wave_date).days
            
            if days_since_wave < 30:
                return True, f"Recent {latest_wave.type} ({days_since_wave} days ago)", modifier
        
        # Check rotation status
        if set_info.rotation_status == "standard" and set_info.expected_rotation:
            days_to_rotation = (datetime.strptime(f"{set_info.expected_rotation}-09-01", "%Y-%m-%d") - datetime.now()).days
            if 0 < days_to_rotation < 90:
                return True, f"Approaching rotation ({days_to_rotation} days)", modifier
        
        return False, "No immediate adjustment needed", modifier
    
    def display_set_summary(self, set_name: str):
        """Display detailed summary for a set"""
        set_info = self.get_set_info(set_name)
        if not set_info:
            print(f"Set not found: {set_name}")
            return
            
        print(f"\n📦 {set_name}")
        print("=" * 50)
        print(f"Released: {set_info.release_date}")
        print(f"Status: {set_info.rotation_status} | Market: {set_info.market_status}")
        print(f"Cards: {set_info.total_cards}")
        
        if set_info.special_notes:
            print(f"Notes: {set_info.special_notes}")
        
        print("\nPrint Waves:")
        for wave in set_info.print_waves:
            print(f"  • {wave['date']}: {wave['type']}")
        
        needs_adjustment, reason, modifier = self.should_adjust_price(set_name)
        print(f"\nPrice Modifier: {modifier:.2f}x")
        print(f"Adjustment Needed: {'Yes' if needs_adjustment else 'No'}")
        if needs_adjustment:
            print(f"Reason: {reason}")

def main():
    """Test the set catalog"""
    catalog = SetCatalog()
    
    test_sets = [
        "Scarlet & Violet",
        "Hidden Fates",
        "Base Set"
    ]
    
    for set_name in test_sets:
        catalog.display_set_summary(set_name)

if __name__ == "__main__":
    main()
