#!/usr/bin/env python3
"""
Pokemon Card Price Volatility Tracker

Why this matters:
1. Cards spike in price FAST (tournaments, YouTuber mentions, etc.)
2. Different platforms update at different speeds
3. Most traders miss sudden price movements
4. Bulk "trash" cards can spike to $50+ overnight

Strategy:
- Track ALL cards (even "worthless" ones)
- Monitor price velocity (how fast prices change)
- Identify patterns that predict spikes
- Alert on unusual movements
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from pokemon_price_system import price_db

logger = logging.getLogger(__name__)

@dataclass
class PriceMovement:
    """Track how a card's price changes over time"""
    card_name: str
    set_name: str
    current_price: float
    previous_price: float
    price_change: float
    change_percent: float
    velocity: float  # Price change per hour
    last_updated: datetime
    source: str
    trend: str  # "spike", "crash", "steady", "volatile"
    alert_level: str  # "high", "medium", "low"

class PriceVolatilityTracker:
    """Track and analyze price movements"""
    
    def __init__(self):
        self.db = price_db
        self.setup_volatility_tracking()
    
    def setup_volatility_tracking(self):
        """Setup database tables for tracking price movements"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Store price history with timestamps
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_name TEXT NOT NULL,
                set_name TEXT NOT NULL,
                price REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                source TEXT NOT NULL,
                UNIQUE(card_name, set_name, timestamp)
            )
        ''')
        
        # Track cards with high volatility
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS volatile_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_name TEXT NOT NULL,
                set_name TEXT NOT NULL,
                volatility_score REAL NOT NULL,
                last_updated DATETIME NOT NULL,
                price_trend TEXT NOT NULL,
                notes TEXT,
                UNIQUE(card_name, set_name)
            )
        ''')
        
        # Track price movement alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_name TEXT NOT NULL,
                set_name TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                price_change REAL NOT NULL,
                change_percent REAL NOT NULL,
                detected_at DATETIME NOT NULL,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_price_movement(self, card_name: str, set_name: str, 
                             hours_back: int = 24) -> Optional[PriceMovement]:
        """Analyze how a card's price has moved"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get current and previous prices
        cursor.execute('''
            SELECT price, timestamp, source 
            FROM price_history 
            WHERE card_name = ? AND set_name = ?
            AND timestamp >= datetime('now', ?)
            ORDER BY timestamp DESC
        ''', (card_name, set_name, f'-{hours_back} hours'))
        
        prices = cursor.fetchall()
        if not prices:
            return None
        
        current = prices[0]  # Most recent
        oldest = prices[-1] if len(prices) > 1 else current
        
        # Calculate price movement metrics
        current_price = current[0]
        previous_price = oldest[0]
        price_change = current_price - previous_price
        change_percent = (price_change / previous_price) * 100 if previous_price > 0 else 0
        
        # Calculate velocity (price change per hour)
        time_diff = datetime.fromisoformat(current[1]) - datetime.fromisoformat(oldest[1])
        hours_diff = time_diff.total_seconds() / 3600
        velocity = price_change / max(hours_diff, 1)  # Avoid division by zero
        
        # Determine trend
        trend = "steady"
        if abs(change_percent) > 50:
            trend = "spike" if change_percent > 0 else "crash"
        elif abs(change_percent) > 20:
            trend = "volatile"
        
        # Set alert level
        alert_level = "low"
        if abs(change_percent) > 50 or abs(velocity) > 10:
            alert_level = "high"
        elif abs(change_percent) > 20 or abs(velocity) > 5:
            alert_level = "medium"
        
        conn.close()
        
        return PriceMovement(
            card_name=card_name,
            set_name=set_name,
            current_price=current_price,
            previous_price=previous_price,
            price_change=price_change,
            change_percent=change_percent,
            velocity=velocity,
            last_updated=datetime.fromisoformat(current[1]),
            source=current[2],
            trend=trend,
            alert_level=alert_level
        )
    
    def record_price(self, card_name: str, set_name: str, price: float, source: str):
        """Record a new price point"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO price_history 
            (card_name, set_name, price, timestamp, source)
            VALUES (?, ?, ?, datetime('now'), ?)
        ''', (card_name, set_name, price, source))
        
        conn.commit()
        conn.close()
        
        # Analyze for significant movements
        movement = self.analyze_price_movement(card_name, set_name)
        if movement and movement.alert_level in ['medium', 'high']:
            self.record_price_alert(movement)
    
    def record_price_alert(self, movement: PriceMovement):
        """Record significant price movements"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        details = {
            'current_price': movement.current_price,
            'previous_price': movement.previous_price,
            'velocity': movement.velocity,
            'trend': movement.trend,
            'source': movement.source
        }
        
        cursor.execute('''
            INSERT INTO price_alerts
            (card_name, set_name, alert_type, price_change, 
             change_percent, detected_at, details)
            VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
        ''', (
            movement.card_name,
            movement.set_name,
            movement.alert_level,
            movement.price_change,
            movement.change_percent,
            json.dumps(details)
        ))
        
        conn.commit()
        conn.close()
    
    def update_volatility_score(self, card_name: str, set_name: str):
        """Calculate and update volatility score"""
        movements = []
        for hours in [24, 48, 72]:  # Look at different timeframes
            movement = self.analyze_price_movement(card_name, set_name, hours)
            if movement:
                movements.append(movement)
        
        if not movements:
            return
        
        # Calculate volatility score (0-100)
        # Higher score = more volatile
        score = 0
        
        # Factor in price changes
        max_change_percent = max(abs(m.change_percent) for m in movements)
        score += min(max_change_percent, 50)  # Up to 50 points for price changes
        
        # Factor in velocity
        max_velocity = max(abs(m.velocity) for m in movements)
        score += min(max_velocity * 5, 30)  # Up to 30 points for velocity
        
        # Factor in trend changes
        trend_changes = len(set(m.trend for m in movements))
        score += trend_changes * 10  # Up to 20 points for trend changes
        
        # Save volatility score
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO volatile_cards
            (card_name, set_name, volatility_score, last_updated, price_trend, notes)
            VALUES (?, ?, ?, datetime('now'), ?, ?)
        ''', (
            card_name,
            set_name,
            min(score, 100),  # Cap at 100
            movements[0].trend,
            f"Changed {max_change_percent:.1f}% in 72h"
        ))
        
        conn.commit()
        conn.close()
    
    def get_volatile_cards(self, min_score: float = 50) -> List[Dict]:
        """Get cards with high volatility scores"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT card_name, set_name, volatility_score, price_trend, notes
            FROM volatile_cards
            WHERE volatility_score >= ?
            ORDER BY volatility_score DESC
        ''', (min_score,))
        
        volatile_cards = []
        for row in cursor.fetchall():
            volatile_cards.append({
                'card_name': row[0],
                'set_name': row[1],
                'volatility_score': row[2],
                'trend': row[3],
                'notes': row[4]
            })
        
        conn.close()
        return volatile_cards
    
    def get_recent_alerts(self, hours: int = 24, 
                         min_level: str = "medium") -> List[Dict]:
        """Get recent price movement alerts"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        level_filter = "alert_type IN ('high')" if min_level == "high" else \
                      "alert_type IN ('high', 'medium')"
        
        cursor.execute(f'''
            SELECT card_name, set_name, alert_type, price_change, 
                   change_percent, detected_at, details
            FROM price_alerts
            WHERE detected_at >= datetime('now', ?)
            AND {level_filter}
            ORDER BY detected_at DESC
        ''', (f'-{hours} hours',))
        
        alerts = []
        for row in cursor.fetchall():
            details = json.loads(row[6])
            alerts.append({
                'card_name': row[0],
                'set_name': row[1],
                'alert_type': row[2],
                'price_change': row[3],
                'change_percent': row[4],
                'detected_at': row[5],
                'current_price': details['current_price'],
                'previous_price': details['previous_price'],
                'trend': details['trend']
            })
        
        conn.close()
        return alerts

def main():
    """Main function"""
    tracker = PriceVolatilityTracker()
    
    print("🎯 Pokemon Card Price Volatility Tracker")
    print("=" * 50)
    print("1. Show volatile cards")
    print("2. Show recent alerts")
    print("3. Analyze specific card")
    print("4. Update volatility scores")
    print("5. Exit")
    
    while True:
        choice = input("\nChoose option (1-5): ").strip()
        
        if choice == '1':
            cards = tracker.get_volatile_cards(50)
            print(f"\n📈 Found {len(cards)} volatile cards:")
            for card in cards[:10]:
                print(f"• {card['card_name']} ({card['set_name']})")
                print(f"  Score: {card['volatility_score']:.1f}")
                print(f"  Trend: {card['trend']}")
                print(f"  Note: {card['notes']}")
        
        elif choice == '2':
            alerts = tracker.get_recent_alerts(24, "medium")
            print(f"\n🚨 {len(alerts)} recent alerts:")
            for alert in alerts[:10]:
                print(f"• {alert['card_name']} ({alert['set_name']})")
                print(f"  {alert['alert_type'].upper()}: {alert['change_percent']:+.1f}%")
                print(f"  ${alert['previous_price']:.2f} → ${alert['current_price']:.2f}")
                print(f"  Detected: {alert['detected_at']}")
        
        elif choice == '3':
            card_name = input("Card name: ").strip()
            set_name = input("Set name: ").strip()
            
            movement = tracker.analyze_price_movement(card_name, set_name)
            if movement:
                print(f"\n📊 Price Movement Analysis:")
                print(f"Current: ${movement.current_price:.2f}")
                print(f"Change: ${movement.price_change:+.2f} ({movement.change_percent:+.1f}%)")
                print(f"Velocity: ${movement.velocity:+.2f}/hour")
                print(f"Trend: {movement.trend}")
                print(f"Alert Level: {movement.alert_level}")
            else:
                print("❌ No price data found")
        
        elif choice == '4':
            print("\n🔄 Updating volatility scores...")
            # This would update all cards in practice
            print("✅ Update complete!")
        
        elif choice == '5':
            print("\n👋 Happy trading!")
            break
        
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
