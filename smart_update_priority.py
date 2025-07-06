#!/usr/bin/env python3
"""
Smart Update Priority System
Determines which cards need price updates most urgently
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from pokemon_price_system import price_db

@dataclass
class UpdatePriority:
    card_name: str
    set_name: str
    current_price: float
    last_updated: datetime
    priority_score: float  # 0-100
    update_frequency: str  # 'daily', 'weekly', 'monthly', 'quarterly'
    reason: str

class SmartUpdatePriority:
    """Smart price update prioritization"""
    
    def __init__(self):
        self.db = price_db
        
        # Price thresholds
        self.CHASE_THRESHOLD = 100.0
        self.STAPLE_THRESHOLD = 20.0
        self.BULK_THRESHOLD = 5.0
        
        # Age thresholds (days)
        self.CRITICAL_AGE = 7
        self.WARN_AGE = 30
        self.MAX_AGE = 90
        
        # High priority cards/sets
        self.PRIORITY_POKEMON = [
            'charizard', 'pikachu', 'mewtwo', 'lugia', 'rayquaza', 'umbreon',
            'mew', 'blastoise', 'venusaur', 'gengar', 'alakazam', 'sylveon'
        ]
        
        self.PRIORITY_SETS = [
            'scarlet', 'violet', 'crown zenith', 'paldea', 'evolving skies',
            'brilliant stars', 'lost origin', 'silver tempest', 'champions path',
            'hidden fates', 'shining fates', 'celebrations'
        ]
    
    def calculate_priority(self, card_name: str, set_name: str, 
                         price: float, last_updated: str) -> UpdatePriority:
        """Calculate update priority for a card"""
        score = 0
        reasons = []
        
        # Base on price tier
        if price >= self.CHASE_THRESHOLD:
            score += 40
            reasons.append("Chase card")
            frequency = 'daily'
        elif price >= self.STAPLE_THRESHOLD:
            score += 25
            reasons.append("Staple card")
            frequency = 'weekly'
        elif price >= self.BULK_THRESHOLD:
            score += 10
            reasons.append("Regular card")
            frequency = 'monthly'
        else:
            score += 5
            reasons.append("Bulk card")
            frequency = 'quarterly'
        
        # Priority cards
        card_lower = card_name.lower()
        if any(p in card_lower for p in self.PRIORITY_POKEMON):
            score += 20
            reasons.append("Priority Pokemon")
            frequency = 'daily' if frequency != 'daily' else frequency
        
        # Priority sets
        set_lower = set_name.lower()
        if any(s in set_lower for s in self.PRIORITY_SETS):
            score += 15
            reasons.append("Priority set")
            frequency = 'weekly' if frequency not in ['daily'] else frequency
        
        # Card types that need frequent updates
        if any(t in card_lower for t in ['vmax', 'vstar', 'v ', 'alt art', 'secret']):
            score += 10
            reasons.append("Special variant")
        
        # Age of price data
        try:
            last_update = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            age_days = (datetime.now() - last_update).days
            
            if age_days > self.MAX_AGE:
                score += 30
                reasons.append(f"Very old price ({age_days} days)")
                frequency = 'daily'  # Force daily if very old
            elif age_days > self.WARN_AGE:
                score += 20
                reasons.append(f"Old price ({age_days} days)")
                frequency = min(frequency, 'weekly')  # At least weekly if old
            elif age_days > self.CRITICAL_AGE:
                score += 10
                reasons.append(f"Aging price ({age_days} days)")
        except:
            score += 25
            reasons.append("Unknown age")
            frequency = 'weekly'
        
        # Cap at 100
        score = min(score, 100)
        
        return UpdatePriority(
            card_name=card_name,
            set_name=set_name,
            current_price=price,
            last_updated=last_update if 'last_update' in locals() else datetime.now(),
            priority_score=score,
            update_frequency=frequency,
            reason=", ".join(reasons)
        )
    
    def get_update_priorities(self, min_score: float = 0) -> List[UpdatePriority]:
        """Get sorted list of cards needing updates"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT card_name, set_name, market_price, last_updated
            FROM card_prices
            ORDER BY last_updated ASC
        ''')
        
        priorities = []
        for row in cursor.fetchall():
            priority = self.calculate_priority(row[0], row[1], row[2], row[3])
            if priority.priority_score >= min_score:
                priorities.append(priority)
        
        conn.close()
        
        # Sort by priority score (highest first)
        priorities.sort(key=lambda x: x.priority_score, reverse=True)
        return priorities
    
    def display_update_summary(self):
        """Show price update summary"""
        priorities = self.get_update_priorities()
        
        print("\n🎯 Price Update Priorities")
        print("=" * 50)
        
        # Group by frequency
        daily = [p for p in priorities if p.update_frequency == 'daily']
        weekly = [p for p in priorities if p.update_frequency == 'weekly']
        monthly = [p for p in priorities if p.update_frequency == 'monthly']
        quarterly = [p for p in priorities if p.update_frequency == 'quarterly']
        
        print(f"\n📅 Daily Updates ({len(daily)} cards):")
        for p in daily[:5]:
            print(f"  • {p.card_name} ({p.set_name})")
            print(f"    ${p.current_price:.2f} | Score: {p.priority_score:.0f} | {p.reason}")
        if len(daily) > 5:
            print(f"    ...and {len(daily)-5} more")
            
        print(f"\n📅 Weekly Updates ({len(weekly)} cards):")
        for p in weekly[:3]:
            print(f"  • {p.card_name} ({p.set_name})")
            print(f"    ${p.current_price:.2f} | Score: {p.priority_score:.0f} | {p.reason}")
        if len(weekly) > 3:
            print(f"    ...and {len(weekly)-3} more")
            
        print(f"\n📊 Update Queue Summary:")
        print(f"  • Critical (Daily): {len(daily)} cards")
        print(f"  • Important (Weekly): {len(weekly)} cards")
        print(f"  • Regular (Monthly): {len(monthly)} cards")
        print(f"  • Low Priority (Quarterly): {len(quarterly)} cards")
        print(f"  Total Cards: {len(priorities)}")

def main():
    """Run priority analysis"""
    priority_system = SmartUpdatePriority()
    priority_system.display_update_summary()

if __name__ == "__main__":
    main()
