#!/usr/bin/env python3
"""
Enhanced Price Verifier
Cross-references multiple sources to verify and update card prices
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from statistics import median, stdev
from pokemon_price_system import PokemonPriceDB, get_card_market_price
from ebay_browse_api_integration import EbayBrowseAPI as EbaySDK

class EnhancedPriceVerifier:
    def __init__(self):
        self.price_db = PokemonPriceDB()
        self.ebay_sdk = EbaySDK()
        self.min_confidence = 0.70  # 70% minimum confidence for updates
        self.price_variance_threshold = 0.20  # 20% max variance between sources
        
    def get_tcgplayer_price(self, card_name: str, set_name: str) -> Optional[float]:
        """Get price from TCGPlayer"""
        try:
            price_data = self.price_db.get_card_price(card_name, set_name)
            if price_data and hasattr(price_data, 'market_price'):
                return price_data.market_price
            return None
        except Exception as e:
            logging.error(f"TCGPlayer error for {card_name}: {e}")
            return None
            
    def get_ebay_sold_price(self, card_name: str, set_name: str) -> Optional[float]:
        """Get average price from recent eBay sales"""
        try:
            search_query = f"{card_name} {set_name}"
            items = self.ebay_sdk.search_pokemon_cards(
                search_query,
                max_price=1000,  # High limit to catch all relevant sales
                limit=10
            )
            
            if not items:
                return None
                
            # Filter out outliers
            prices = [item['total_price'] for item in items]
            if len(prices) < 3:
                return None
                
            med = median(prices)
            std = stdev(prices)
            filtered_prices = [p for p in prices if abs(p - med) <= 2 * std]
            
            return sum(filtered_prices) / len(filtered_prices) if filtered_prices else None
            
        except Exception as e:
            logging.error(f"eBay error for {card_name}: {e}")
            return None
            
    def calculate_verified_price(self, prices: Dict[str, Optional[float]]) -> Tuple[Optional[float], float]:
        """
        Calculate verified price and confidence from multiple sources
        Returns: (verified_price, confidence)
        """
        valid_prices = [p for p in prices.values() if p is not None]
        if not valid_prices:
            return None, 0.0
            
        # Calculate median price
        med_price = median(valid_prices)
        
        # Calculate variance between sources
        max_variance = 0
        for price in valid_prices:
            variance = abs(price - med_price) / med_price
            max_variance = max(max_variance, variance)
        
        # Calculate confidence score
        confidence = 0.5  # Base confidence
        
        # More sources = higher confidence
        confidence += 0.1 * len(valid_prices)
        
        # Lower variance = higher confidence
        if max_variance <= 0.05:  # 5% variance
            confidence += 0.3
        elif max_variance <= 0.10:  # 10% variance
            confidence += 0.2
        elif max_variance <= 0.15:  # 15% variance
            confidence += 0.1
            
        # Cap confidence at 95%
        confidence = min(confidence, 0.95)
        
        return med_price, confidence
        
    def verify_card_price(self, card_name: str, set_name: str) -> Dict:
        """
        Verify price from multiple sources
        Returns verification results
        """
        print(f"\nVerifying {card_name} ({set_name})")
        print("-" * 60)
        
        # Gather prices from different sources
        # Get local DB price first
        db_price = self.price_db.get_card_price(card_name, set_name)
        local_price = db_price.market_price if db_price else None
        
        prices = {
            'tcgplayer': self.get_tcgplayer_price(card_name, set_name),
            'ebay_sold': self.get_ebay_sold_price(card_name, set_name),
            'local_db': local_price
        }
        
        # Calculate verified price and confidence
        verified_price, confidence = self.calculate_verified_price(prices)
        
        if verified_price and confidence >= self.min_confidence:
            # Update database with verified price
            self.price_db.update_price_manually(
                card_name=card_name,
                set_name=set_name,
                market_price=verified_price,
                notes=f"Verified price (confidence: {confidence:.1%})"
            )
            print("✅ Price verified and updated!")
            print(f"New Price: ${verified_price:.2f}")
            print(f"Confidence: {confidence:.1%}\n")
        else:
            print(f"Low confidence price for {card_name}: {confidence:.1%}")
            print(f"⚠️ Low confidence price - not updated")
            print(f"Confidence: {confidence:.1%}\n")
            
        print("Source Prices:")
        for source, price in prices.items():
            if price:
                print(f"  • {source}: ${price:.2f}")
                
        return {
            'card_name': card_name,
            'set_name': set_name,
            'verified_price': verified_price,
            'confidence': confidence,
            'source_prices': prices,
            'updated': confidence >= self.min_confidence
        }
        
    def verify_database_prices(self, min_age_hours: int = 168) -> List[Dict]:
        """
        Verify all prices in database older than min_age_hours
        Returns list of verification results
        """
        print("\n🔍 Running Database Verification")
        print("=" * 60)
        
        cards = self.price_db.get_all_cards()
        results = []
        
        for card in cards:
            last_updated = datetime.fromisoformat(card['last_updated'])
            if datetime.now() - last_updated > timedelta(hours=min_age_hours):
                result = self.verify_card_price(
                    card['card_name'],
                    card['set_name']
                )
                results.append(result)
                
        return results

def test_verified_updater():
    """Test the enhanced price verification system"""
    print("🔍 Testing Verified Price Updates")
    print("=" * 60)
    
    verifier = EnhancedPriceVerifier()
    
    # Test with some popular cards
    test_cards = [
        ("Charizard VMAX", "Champions Path"),
        ("Pikachu V", "Vivid Voltage"),
        ("Lugia V", "Silver Tempest"),
        ("Base Set Charizard", "Base Set")
    ]
    
    for card_name, set_name in test_cards:
        verifier.verify_card_price(card_name, set_name)
        
    # Verify database prices
    results = verifier.verify_database_prices()
    
    # Export results
    with open('price_verification_results.json', 'w') as f:
        json.dump(results, f, indent=2)
        
if __name__ == "__main__":
    test_verified_updater()
