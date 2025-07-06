"""
Pokemon Card Price Database System

This module handles pricing data for accurate deal detection and profit calculation.
Uses multiple sources and maintains a local price database for fast lookups.
Integrates population data to adjust prices based on card scarcity.
"""

import json
import sqlite3
import requests
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from dataclasses import dataclass
import re
import time
from population_tracker import PopulationTracker

logger = logging.getLogger(__name__)

# Initialize population tracker
pop_tracker = PopulationTracker()

@dataclass
class PriceData:
    """Price data structure"""
    card_name: str
    set_name: str
    market_price: float
    condition: str = "raw"  # "raw", "PSA 10", "PSA 9", etc.
    last_updated: Optional[datetime] = None
    confidence: float = 0.0
    recent_sales: List[Dict] = field(default_factory=list)
    
class PokemonPriceDB:
    """Pokemon card price database with multiple sources"""
    
    def __init__(self, db_path: str = "pokemon_prices.db"):
        self.db_path = db_path
        self.setup_database()
        
        # Price sources (free alternatives to paid APIs)
        self.price_sources = {
            'tcgplayer_scrape': self._scrape_tcgplayer_price,
            'pricecharting': self._get_pricecharting_price,
            'sold_listings': self._analyze_sold_listings,
            'manual_updates': self._load_manual_prices
        }
        
        # Popular Pokemon cards with approximate pricing
        self.base_prices = self._load_base_price_data()
    
    def setup_database(self):
        """Setup SQLite database for price storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS card_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_name TEXT NOT NULL,
                set_name TEXT NOT NULL,
                market_price REAL NOT NULL,
                low_price REAL NOT NULL,
                high_price REAL NOT NULL,
                last_updated TIMESTAMP NOT NULL,
                source TEXT NOT NULL,
                condition TEXT DEFAULT 'Near Mint',
                price_trend TEXT DEFAULT 'stable',
                UNIQUE(card_name, set_name, condition, source)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_card_lookup 
            ON card_prices(card_name, set_name, condition)
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_base_price_data(self) -> Dict[str, Dict]:
        """Load base price data for popular Pokemon cards"""
        return {
            # Charizard variants
            'charizard vmax': {
                'Champions Path': 85.00,
                'Darkness Ablaze': 45.00,
                'Shining Fates': 65.00
            },
            'charizard v': {
                'Champions Path': 25.00,
                'Darkness Ablaze': 15.00
            },
            'charizard gx': {
                'Hidden Fates': 35.00,
                'Burning Shadows': 20.00
            },
            'charizard ex': {
                'Flashfire': 30.00,
                'Evolutions': 15.00
            },
            
            # Pikachu variants
            'pikachu vmax': {
                'Vivid Voltage': 25.00,
                'Sword & Shield Promo': 40.00
            },
            'pikachu v': {
                'Vivid Voltage': 12.00,
                'Sword & Shield Promo': 20.00
            },
            
            # Other popular cards
            'rayquaza vmax': {
                'Evolving Skies': 70.00
            },
            'umbreon vmax': {
                'Evolving Skies': 120.00
            },
            'lugia v': {
                'Silver Tempest': 80.00
            },
            'mewtwo gx': {
                'Shining Legends': 25.00
            },
            
            # Vintage cards (higher value)
            'base set charizard': {
                'Base Set': 450.00,
                'Base Set Shadowless': 850.00,
                'Base Set 1st Edition': 2500.00
            },
            'base set blastoise': {
                'Base Set': 120.00,
                'Base Set Shadowless': 250.00
            },
            'base set venusaur': {
                'Base Set': 100.00,
                'Base Set Shadowless': 200.00
            }
        }
    
    def get_card_price(self, card_name: str, set_name: str = None, condition: str = "raw") -> Optional[PriceData]:
        """Get price for a specific card"""
        # First check database
        db_price = self._get_price_from_db(card_name, set_name, condition)
        if db_price and self._is_price_fresh(db_price.last_updated):
            return db_price
        
        # Try to get updated price
        updated_price = self._fetch_updated_price(card_name, set_name, condition)
        if updated_price:
            self._save_price_to_db(updated_price)
            return updated_price
        
        # Fall back to base price estimation
        estimated_price = self._estimate_price_from_base_data(card_name, set_name)
        if estimated_price:
            return estimated_price
        
        return None
    
    def _get_price_from_db(self, card_name: str, set_name: str = None, condition: str = "raw") -> Optional[PriceData]:
        """Get price from local database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if set_name:
            cursor.execute('''
                SELECT * FROM card_prices 
                WHERE LOWER(card_name) LIKE LOWER(?) 
                AND LOWER(set_name) LIKE LOWER(?) 
                AND condition = ?
                ORDER BY last_updated DESC LIMIT 1
            ''', (f'%{card_name}%', f'%{set_name}%', condition))
        else:
            cursor.execute('''
                SELECT * FROM card_prices 
                WHERE LOWER(card_name) LIKE LOWER(?) 
                AND condition = ?
                ORDER BY last_updated DESC LIMIT 1
            ''', (f'%{card_name}%', condition))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return PriceData(
                card_name=row[1],
                set_name=row[2],
                market_price=row[3],
                low_price=row[4],
                high_price=row[5],
                last_updated=datetime.fromisoformat(row[6]),
                source=row[7],
                condition=row[8],
                price_trend=row[9]
            )
        
        return None
    
    def _is_price_fresh(self, last_updated: datetime, hours: int = 24) -> bool:
        """Check if price data is fresh enough"""
        return datetime.now() - last_updated < timedelta(hours=hours)
    
    def _fetch_updated_price(self, card_name: str, set_name: str = None, condition: str = "raw") -> Optional[PriceData]:
        """Fetch updated price from various sources"""
        for source_name, source_func in self.price_sources.items():
            try:
                price_data = source_func(card_name, set_name, condition)
                if price_data:
                    return price_data
            except Exception as e:
                logger.error(f"Error fetching price from {source_name}: {e}")
                continue
        
        return None
    
    def _scrape_tcgplayer_price(self, card_name: str, set_name: str = None, condition: str = "raw") -> Optional[PriceData]:
        """Scrape TCGPlayer for price data (simplified)"""
        try:
            # This is a simplified example - real implementation would need proper scraping
            # For now, return None to avoid rate limiting issues
            return None
        except Exception as e:
            logger.error(f"Error scraping TCGPlayer: {e}")
            return None
    
    def _get_pricecharting_price(self, card_name: str, set_name: str = None, condition: str = "raw") -> Optional[PriceData]:
        """Get price from PriceCharting (if API available)"""
        try:
            # Placeholder for PriceCharting API
            return None
        except Exception as e:
            logger.error(f"Error getting PriceCharting price: {e}")
            return None
    
    def _analyze_sold_listings(self, card_name: str, set_name: str = None, condition: str = "raw") -> Optional[PriceData]:
        """Analyze sold listings for price estimation"""
        try:
            # This would analyze recent eBay sold listings
            # For now, return None
            return None
        except Exception as e:
            logger.error(f"Error analyzing sold listings: {e}")
            return None
    
    def _load_manual_prices(self, card_name: str, set_name: str = None, condition: str = "raw") -> Optional[PriceData]:
        """Load manually updated prices from JSON file"""
        try:
            with open('manual_prices.json', 'r') as f:
                manual_prices = json.load(f)
            
            # Search for matching card
            for entry in manual_prices.get('cards', []):
                if (card_name.lower() in entry['name'].lower() and 
                    (not set_name or set_name.lower() in entry.get('set', '').lower())):
                    
                    return PriceData(
                        card_name=entry['name'],
                        set_name=entry.get('set', 'Unknown'),
                        market_price=entry['market_price'],
                        low_price=entry.get('low_price', entry['market_price'] * 0.8),
                        high_price=entry.get('high_price', entry['market_price'] * 1.2),
                        last_updated=datetime.fromisoformat(entry.get('last_updated', datetime.now().isoformat())),
                        source='manual',
                        condition=condition,
                        price_trend=entry.get('trend', 'stable')
                    )
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.error(f"Error loading manual prices: {e}")
        
        return None
    
    def _estimate_price_from_base_data(self, card_name: str, set_name: str = None) -> Optional[PriceData]:
        """Estimate price from base data"""
        card_name_clean = self._clean_card_name(card_name)
        
        for base_card, sets in self.base_prices.items():
            if base_card in card_name_clean.lower():
                # Find matching set
                if set_name:
                    for base_set, price in sets.items():
                        if base_set.lower() in set_name.lower():
                            return PriceData(
                                card_name=card_name,
                                set_name=set_name,
                                market_price=price,
                                low_price=price * 0.8,
                                high_price=price * 1.2,
                                last_updated=datetime.now(),
                                source='base_estimation',
                                condition="Near Mint",
                                price_trend="stable"
                            )
                
                # If no specific set match, use first available price
                if sets:
                    first_price = list(sets.values())[0]
                    return PriceData(
                        card_name=card_name,
                        set_name=set_name or "Unknown",
                        market_price=first_price,
                        low_price=first_price * 0.8,
                        high_price=first_price * 1.2,
                        last_updated=datetime.now(),
                        source='base_estimation',
                        condition="Near Mint",
                        price_trend="stable"
                    )
        
        return None
    
    def _clean_card_name(self, card_name: str) -> str:
        """Clean card name for matching"""
        # Remove special characters and extra spaces
        cleaned = re.sub(r'[^\w\s]', ' ', card_name)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def _save_price_to_db(self, price_data: PriceData):
        """Save price data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO card_prices 
            (card_name, set_name, market_price, low_price, high_price, 
             last_updated, source, condition, price_trend)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            price_data.card_name,
            price_data.set_name,
            price_data.market_price,
            price_data.low_price,
            price_data.high_price,
            price_data.last_updated.isoformat(),
            price_data.source,
            price_data.condition,
            price_data.price_trend
        ))
        
        conn.commit()
        conn.close()
    
    def update_price_manually(self, card_name: str, set_name: str, market_price: float, 
                             condition: str = "Near Mint", notes: str = ""):
        """Manually update a card price"""
        price_data = PriceData(
            card_name=card_name,
            set_name=set_name,
            market_price=market_price,
            low_price=market_price * 0.85,
            high_price=market_price * 1.15,
            last_updated=datetime.now(),
            source='manual_update',
            condition=condition,
            price_trend="stable"
        )
        
        self._save_price_to_db(price_data)
        logger.info(f"Manually updated price for {card_name} ({set_name}): ${market_price}")
    
    def bulk_update_prices(self, price_file: str):
        """Bulk update prices from CSV or JSON file"""
        try:
            if price_file.endswith('.json'):
                self._bulk_update_from_json(price_file)
            elif price_file.endswith('.csv'):
                self._bulk_update_from_csv(price_file)
            else:
                logger.error("Unsupported file format. Use JSON or CSV.")
        except Exception as e:
            logger.error(f"Error in bulk price update: {e}")
    
    def _bulk_update_from_json(self, json_file: str):
        """Bulk update from JSON file"""
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        for entry in data.get('cards', []):
            self.update_price_manually(
                card_name=entry['name'],
                set_name=entry.get('set', 'Unknown'),
                market_price=entry['market_price'],
                condition=entry.get('condition', 'Near Mint')
            )
    
    def _bulk_update_from_csv(self, csv_file: str):
        """Bulk update from CSV file"""
        import csv
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.update_price_manually(
                    card_name=row['card_name'],
                    set_name=row.get('set_name', 'Unknown'),
                    market_price=float(row['market_price']),
                    condition=row.get('condition', 'Near Mint')
                )
    
    def get_price_statistics(self) -> Dict:
        """Get price database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM card_prices')
        total_prices = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM card_prices 
            WHERE last_updated > datetime('now', '-24 hours')
        ''')
        fresh_prices = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT card_name) FROM card_prices')
        unique_cards = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_prices': total_prices,
            'fresh_prices': fresh_prices,
            'unique_cards': unique_cards,
            'freshness_ratio': fresh_prices / max(total_prices, 1)
        }
    
    def get_population_adjusted_price(self, card_name: str, set_name: Optional[str], condition: str = "Near Mint") -> Tuple[Optional[float], float, Dict]:
        """
        Get card price adjusted for population data
        Returns: (adjusted_price, confidence, population_data)
        """
        # Get base price first
        price_data = self.get_card_price(card_name, set_name, condition)
        if not price_data or not price_data.market_price:
            return None, 0.0, {}
            
        # Get population data and calculate impact
        base_price = price_data.market_price
        adjusted_price, pop_multiplier = pop_tracker.calculate_price_impact(
            card_name, 
            set_name or "Unknown Set",
            base_price
        )
        
        # Get detailed population info
        pop_summary = pop_tracker.get_population_data(card_name, set_name or "Unknown Set")
        
        # Calculate confidence based on both price and population data
        pop_confidence = 1.0 if pop_summary["last_update"] else 0.5
        final_confidence = min(price_data.confidence, pop_confidence)
        
        pop_info = {
            "population_multiplier": pop_multiplier,
            "total_graded": (
                pop_summary["PSA"]["total"] + 
                pop_summary["BGS"]["total"] + 
                pop_summary["CGC"]["total"]
            ),
            "gem_mint_population": (
                pop_summary["PSA"]["10"] + 
                pop_summary["BGS"]["10"] + pop_summary["BGS"]["9.5"] +
                pop_summary["CGC"]["10"] + pop_summary["CGC"]["9.5"]
            ),
            "last_update": pop_summary["last_update"]
        }
        
        return adjusted_price, final_confidence, pop_info
    
    def get_all_cards(self) -> List[Dict]:
        """Get all cards from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT card_name, set_name, market_price, condition, last_updated
            FROM card_prices
            ORDER BY last_updated DESC
        ''')
        
        cards = []
        for row in cursor.fetchall():
            cards.append({
                'card_name': row[0],
                'set_name': row[1],
                'market_price': row[2],
                'condition': row[3],
                'last_updated': row[4]
            })
        
        conn.close()
        return cards

# Global price database instance
price_db = PokemonPriceDB()

def get_card_market_price(card_name: str, set_name: str, condition: str = "raw") -> Tuple[float, float]:
    """
    Get market price and confidence score for a card
    
    Args:
        card_name: Name of the card
        set_name: Name of the set
        condition: Condition/grade of card ("raw", "PSA 10", etc)
        
    Returns:
        (price, confidence)
    """
    price_data = price_db.get_card_price(card_name, set_name, condition)
    
    if price_data:
        # Calculate confidence based on data freshness and source
        confidence = 0.5  # Base confidence
        
        # Boost confidence for fresh data
        hours_old = (datetime.now() - price_data.last_updated).total_seconds() / 3600
        if hours_old < 24:
            confidence += 0.3
        elif hours_old < 168:  # 1 week
            confidence += 0.1
        
        # Boost confidence for reliable sources
        if price_data.source in ['tcgplayer', 'manual_update']:
            confidence += 0.2
        elif price_data.source == 'sold_listings':
            confidence += 0.15
        
        return price_data.market_price, min(confidence, 0.95)
    
    return None, 0.0

if __name__ == "__main__":
    # Example usage
    db = PokemonPriceDB()
    
    # Test price lookup
    price, confidence = get_card_market_price("Charizard VMAX", "Champions Path")
    print(f"Charizard VMAX price: ${price} (confidence: {confidence:.1%})")
    
    # Show database stats
    stats = db.get_price_statistics()
    print(f"Database stats: {stats}")
