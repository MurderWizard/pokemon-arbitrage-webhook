#!/usr/bin/env python3
"""
Price Verification System
Cross-references multiple sources to get accurate card prices
"""

import os
import json
import logging
import requests
import statistics
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VerifiedPrice:
    market_price: float
    confidence: float
    sources: Dict[str, float]
    timestamp: datetime
    outliers_removed: List[Tuple[str, float]]
    variance: float

class PriceVerifier:
    def __init__(self):
        self.sources = {
            'tcgplayer': self._get_tcgplayer_price,
            'ebay_sold': self._get_ebay_sold_prices,
            'cardmarket': self._get_cardmarket_price,
            'price_charting': self._get_pricecharting_price,
            'local_db': self._get_local_db_price
        }
        
        self.source_weights = {
            'tcgplayer': 1.0,      # Most reliable for current market
            'ebay_sold': 0.9,      # Real sales data
            'cardmarket': 0.8,     # Good for international prices
            'price_charting': 0.7, # Historical data
            'local_db': 0.6        # Our cached data
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def verify_price(self, card_name: str, set_name: Optional[str] = None) -> VerifiedPrice:
        """Get verified price from multiple sources"""
        all_prices = {}
        
        # Collect prices from all sources
        for source_name, source_func in self.sources.items():
            try:
                price = source_func(card_name, set_name)
                if price:
                    all_prices[source_name] = price
            except Exception as e:
                logger.error(f"Error getting price from {source_name}: {e}")
                
        if not all_prices:
            raise ValueError(f"Could not get prices for {card_name}")
            
        # Remove outliers (prices that deviate too much)
        cleaned_prices, outliers = self._remove_outliers(all_prices)
        
        if not cleaned_prices:
            # If all prices were outliers, use original prices
            cleaned_prices = all_prices
            outliers = []
            
        # Calculate weighted average
        weighted_sum = 0
        weight_sum = 0
        
        for source, price in cleaned_prices.items():
            weight = self.source_weights.get(source, 0.5)
            weighted_sum += price * weight
            weight_sum += weight
            
        market_price = weighted_sum / weight_sum if weight_sum > 0 else 0
        
        # Calculate variance to measure price stability
        if len(cleaned_prices) > 1:
            variance = statistics.variance(cleaned_prices.values())
        else:
            variance = 0
            
        # Calculate confidence based on:
        # 1. Number of sources
        # 2. Variance between prices
        # 3. Source weights
        base_confidence = min(len(cleaned_prices) / len(self.sources), 1.0)
        variance_penalty = min(variance / market_price, 0.5) if market_price > 0 else 0.5
        weight_bonus = sum(self.source_weights[s] for s in cleaned_prices.keys()) / len(cleaned_prices)
        
        confidence = (base_confidence + weight_bonus - variance_penalty) / 2
        
        return VerifiedPrice(
            market_price=market_price,
            confidence=min(confidence, 0.95),  # Cap at 95%
            sources=cleaned_prices,
            timestamp=datetime.now(),
            outliers_removed=outliers,
            variance=variance
        )
        
    def _remove_outliers(self, prices: Dict[str, float]) -> Tuple[Dict[str, float], List[Tuple[str, float]]]:
        """Remove price outliers using IQR method"""
        if len(prices) < 2:
            return prices, []
            
        values = list(prices.values())
        q1 = statistics.quantiles(values, n=4)[0]
        q3 = statistics.quantiles(values, n=4)[2]
        iqr = q3 - q1
        
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)
        
        cleaned_prices = {}
        outliers = []
        
        for source, price in prices.items():
            if lower_bound <= price <= upper_bound:
                cleaned_prices[source] = price
            else:
                outliers.append((source, price))
                
        return cleaned_prices, outliers
        
    def _get_tcgplayer_price(self, card_name: str, set_name: Optional[str] = None) -> Optional[float]:
        """Get price from TCGPlayer (market price)"""
        from pokemon_price_system import get_card_market_price
        price, confidence = get_card_market_price(card_name, set_name)
        return price if confidence > 0.5 else None
        
    def _get_ebay_sold_prices(self, card_name: str, set_name: Optional[str] = None) -> Optional[float]:
        """Get average of recent eBay sold listings"""
        try:
            search_query = f"pokemon {card_name}"
            if set_name:
                search_query += f" {set_name}"
                
            url = "https://www.ebay.com/sch/i.html"
            params = {
                '_nkw': search_query,
                '_sacat': '2536',
                'LH_Sold': '1',
                'LH_Complete': '1'
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            prices = []
            items = soup.find_all('span', class_='s-item__price')
            
            for item in items[:10]:  # Look at last 10 sales
                try:
                    price_text = item.get_text().replace('$', '').replace(',', '')
                    price = float(price_text)
                    if price > 0:
                        prices.append(price)
                except (ValueError, AttributeError):
                    continue
                    
            if prices:
                # Use median to avoid extreme outliers
                return statistics.median(prices)
                
        except Exception as e:
            logger.error(f"Error getting eBay prices: {e}")
            
        return None
        
    def _get_cardmarket_price(self, card_name: str, set_name: Optional[str] = None) -> Optional[float]:
        """Get price from Cardmarket (European prices)"""
        # Placeholder for Cardmarket integration
        return None
        
    def _get_pricecharting_price(self, card_name: str, set_name: Optional[str] = None) -> Optional[float]:
        """Get price from PriceCharting"""
        # Placeholder for PriceCharting API integration
        return None
        
    def _get_local_db_price(self, card_name: str, set_name: Optional[str] = None) -> Optional[float]:
        """Get price from local database"""
        from pokemon_price_system import get_card_market_price
        price, _ = get_card_market_price(card_name, set_name)
        return price

def test_price_verifier():
    """Test the price verification system"""
    verifier = PriceVerifier()
    
    # Test cases
    test_cards = [
        ("Charizard VMAX", "Champions Path"),
        ("Pikachu V", "Vivid Voltage"),
        ("Base Set Charizard", "Base Set")
    ]
    
    print("🔍 Price Verification Test")
    print("=" * 60)
    
    for card_name, set_name in test_cards:
        try:
            print(f"\nChecking {card_name} ({set_name})")
            print("-" * 60)
            
            result = verifier.verify_price(card_name, set_name)
            
            print(f"Verified Market Price: ${result.market_price:.2f}")
            print(f"Confidence Score: {result.confidence:.1%}")
            print("\nSource Prices:")
            for source, price in result.sources.items():
                print(f"  • {source}: ${price:.2f}")
                
            if result.outliers_removed:
                print("\nOutliers Removed:")
                for source, price in result.outliers_removed:
                    print(f"  • {source}: ${price:.2f}")
                    
            print(f"\nPrice Variance: ${result.variance:.2f}")
            
        except Exception as e:
            print(f"Error verifying {card_name}: {e}")
            continue
            
if __name__ == "__main__":
    test_price_verifier()
