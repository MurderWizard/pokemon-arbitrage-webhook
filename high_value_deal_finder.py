#!/usr/bin/env python3
"""
High Value Deal Finder ($250+)
Integrates all components for finding and evaluating high-value deals
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

from high_value_analyzer import HighValueAnalyzer
from deal_logger import DealLogger
from raw_to_graded_calculator import calculate_expected_profit
from pokemon_price_system import get_card_market_price
from app.services.external_apis import get_recent_sales

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HighValueDealFinder:
    """Find and evaluate high-value Pokemon card deals"""
    
    def __init__(self):
        self.analyzer = HighValueAnalyzer()
        self.deal_logger = DealLogger()
        self.min_price = 250.0
        self.min_roi = 0.35  # 35% minimum ROI
        
    def evaluate_listing(self, listing: Dict) -> Optional[Dict]:
        """
        Evaluate a card listing for high-value potential
        Returns deal data if promising, None otherwise
        """
        # Quick price filter
        if listing['price'] < self.min_price:
            return None
            
        # Get recent sales data for liquidity analysis
        recent_sales = get_recent_sales(listing['card_name'], listing['set_name'])
        
        # Analyze grading potential
        potential = self.analyzer.analyze_raw_card(
            card_name=listing['card_name'],
            set_name=listing['set_name'],
            condition_desc=listing.get('condition', ''),
            seller_rating=listing.get('seller_rating', 0.0),
            raw_price=listing['price'],
            recent_sales=recent_sales
        )
        
        if not potential or not potential.should_grade:
            return None
            
        # Calculate detailed profit metrics
        profit_details = calculate_expected_profit(
            raw_price=listing['price'],
            psa10_price=potential.estimated_psa10_price,
            psa9_price=potential.estimated_psa10_price * 0.6,  # Estimate PSA 9 at 60% of PSA 10
            psa8_price=potential.estimated_psa10_price * 0.4,  # Estimate PSA 8 at 40% of PSA 10
            psa7_price=potential.estimated_psa10_price * 0.25, # Estimate PSA 7 at 25% of PSA 10
            condition_confidence=potential.confidence
        )
        
        expected_profit, details, should_grade = profit_details
        if not should_grade or (expected_profit / listing['price']) < self.min_roi:
            return None
            
        # Prepare deal data
        deal_data = {
            'card_name': listing['card_name'],
            'set_name': listing['set_name'],
            'raw_price': listing['price'],
            'estimated_psa10_price': potential.estimated_psa10_price,
            'potential_profit': expected_profit,
            'profit_margin': expected_profit / listing['price'],
            'monthly_sales': potential.monthly_sales,
            'price_stability': potential.price_stability,
            'population_psa10': potential.population_psa10,
            'condition_notes': listing.get('condition', ''),
            'listing_url': listing.get('url', ''),
            'price_trend_30d': details.get('price_trend_30d', 0.0),
            'sales_velocity_30d': len(recent_sales) if recent_sales else 0,
            'market_competition': len([s for s in recent_sales if s['status'] == 'active']) if recent_sales else 0,
            'price_volatility': 1 - potential.price_stability
        }
        
        return deal_data
        
    def process_listing(self, listing: Dict) -> Optional[int]:
        """
        Process a listing and log if it's a good deal
        Returns deal_id if logged, None otherwise
        """
        deal_data = self.evaluate_listing(listing)
        if not deal_data:
            return None
            
        try:
            deal_id = self.deal_logger.log_high_value_deal(deal_data)
            logger.info(f"Found high-value deal: {deal_data['card_name']} - ${deal_data['raw_price']:.2f}")
            return deal_id
        except Exception as e:
            logger.error(f"Error processing listing: {e}")
            return None
            
    def get_deal_summary(self, days: int = 30) -> Dict:
        """Get summary of recent high-value deals"""
        return self.deal_logger.get_deal_stats(min_price=self.min_price, days=days)

def main():
    finder = HighValueDealFinder()
    # Example usage:
    sample_listing = {
        'card_name': 'Charizard',
        'set_name': 'Base Set',
        'price': 500.0,
        'condition': 'Near Mint',
        'seller_rating': 99.8,
        'url': 'https://example.com/listing'
    }
    
    deal_id = finder.process_listing(sample_listing)
    if deal_id:
        stats = finder.get_deal_summary()
        logger.info(f"Deal stats for last 30 days: {stats}")

if __name__ == '__main__':
    main()
