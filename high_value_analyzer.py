#!/usr/bin/env python3
"""
High Value Card Analysis Module
Focuses on cards $250+ and their grading potential
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging
from pokemon_price_system import get_card_market_price
from population_tracker import PopulationTracker

logger = logging.getLogger(__name__)

@dataclass
class GradingPotential:
    """Analysis of a card's grading potential"""
    raw_price: float
    estimated_psa10_price: float
    historical_gem_rate: float  # % of this card that gets PSA 10
    population_psa10: int      # Current PSA 10 population
    monthly_sales: int         # Average monthly sales (liquidity)
    price_stability: float     # 0-1 score of price stability
    confidence: float          # 0-1 confidence in assessment
    should_grade: bool         # Final recommendation
    roi_percentage: float      # Return on investment percentage

class HighValueAnalyzer:
    """Analyzes high-value Pokemon cards for vault potential"""
    
    def __init__(self):
        self.pop_tracker = PopulationTracker()
        self.MIN_PRICE = 250.0  # Focus on $250+ cards
        self.MIN_CONFIDENCE = 0.90  # Higher confidence for expensive cards
        self.MIN_ROI = 0.35  # Minimum 35% ROI for high value cards
        self.MIN_MONTHLY_SALES = 2  # At least 2 sales per month for liquidity
        
    def analyze_raw_card(
        self,
        card_name: str,
        set_name: str,
        condition_desc: str,
        seller_rating: float,
        raw_price: float,
        recent_sales: List[Dict[str, Any]] = []
    ) -> Optional[GradingPotential]:
        """
        Analyze a raw card's potential for grading and vaulting
        
        Returns None if card doesn't meet minimum criteria
        """
        # 1. Quick filters
        if raw_price < self.MIN_PRICE:  # Must be $250+
            return None
        
        # 2. Get market data and population
        psa10_price = get_card_market_price(card_name, set_name, "PSA 10")
        population_data = self.pop_tracker.get_population_data(card_name, set_name)
        
        if not psa10_price or not population_data:
            return None
        
        # 3. Calculate ROI and liquidity
        potential_profit = psa10_price - (raw_price + 25)
        roi = potential_profit / raw_price
        
        if roi < self.MIN_ROI:
            return None
            
        # 4. Analyze recent sales for liquidity
        monthly_sales = len([s for s in (recent_sales or []) if s['grade'] == 'PSA 10']) / 3
        if monthly_sales < self.MIN_MONTHLY_SALES:
            return None
            
        # 5. Calculate price stability
        if recent_sales:
            prices = [s['price'] for s in recent_sales if s['grade'] == 'PSA 10']
            price_stability = 1 - (max(prices) - min(prices)) / psa10_price
        else:
            price_stability = 0.5  # Neutral if no sales data
        
        # 6. Analyze condition hints
        condition_score = self._analyze_condition(condition_desc)
        
        # 7. Calculate final confidence
        confidence = min(
            condition_score,
            seller_rating / 100  # Seller rating as 0-1
        )
        
        # 8. Make recommendation
        should_grade = (
            confidence >= self.MIN_CONFIDENCE and
            psa10_price >= self.MIN_PRICE and
            roi >= self.MIN_ROI and
            monthly_sales >= self.MIN_MONTHLY_SALES
        )
        
        return GradingPotential(
            raw_price=raw_price,
            estimated_psa10_price=psa10_price,
            historical_gem_rate=population_data.get('gem_rate', 0.15),
            population_psa10=population_data.get('psa10_population', 0),
            monthly_sales=monthly_sales,
            price_stability=price_stability,
            confidence=confidence,
            should_grade=should_grade,
            roi_percentage=roi * 100
        )
    
    def _analyze_condition(self, condition_desc: str) -> float:
        """Analyze condition description for grading potential"""
        # Keywords that suggest good condition
        good_indicators = [
            'mint', 'gem', 'perfect',
            'pack fresh', 'nm/m',
            'never played', 'psa ready'
        ]
        
        # Keywords that suggest issues
        bad_indicators = [
            'played', 'wear', 'edge',
            'scratch', 'whitening', 'damage',
            'crease', 'bend'
        ]
        
        desc_lower = condition_desc.lower()
        
        # Count indicators
        good_count = sum(1 for word in good_indicators if word in desc_lower)
        bad_count = sum(1 for word in bad_indicators if word in desc_lower)
        
        # Calculate base score
        if bad_count > 0:
            return 0.3  # Any negative indicator is bad for PSA 10
        
        return min(0.9, 0.7 + (good_count * 0.1))  # Up to 0.9 confidence

    def estimate_profit(
        self,
        raw_price: float,
        analysis: GradingPotential
    ) -> Dict[str, float]:
        """
        Estimate profit potential including all fees
        """
        grading_cost = 25  # Basic PSA through eBay
        total_cost = raw_price + grading_cost
        
        # Expected value based on gem rate
        expected_value = (
            (analysis.historical_gem_rate * analysis.estimated_psa10_price) +
            ((1 - analysis.historical_gem_rate) * (raw_price * 0.8))  # Assume 20% loss if not gem
        )
        
        return {
            'total_cost': total_cost,
            'expected_value': expected_value,
            'potential_profit': expected_value - total_cost,
            'roi_percentage': ((expected_value - total_cost) / total_cost) * 100,
            'confidence': analysis.confidence * 100
        }

if __name__ == "__main__":
    # Example usage
    analyzer = HighValueAnalyzer()
    
    # Test with a hypothetical card
    analysis = analyzer.analyze_raw_card(
        card_name="Charizard VMAX",
        set_name="Champions Path",
        condition_desc="Pack Fresh Mint, PSA Ready",
        seller_rating=99.8,
        raw_price=80.0
    )
    
    if analysis and analysis.should_grade:
        profit = analyzer.estimate_profit(80.0, analysis)
        print("\n💰 High Value Analysis")
        print("=" * 40)
        print(f"PSA 10 Price: ${analysis.estimated_psa10_price:.2f}")
        print(f"Historical Gem Rate: {analysis.historical_gem_rate:.1%}")
        print(f"Current PSA 10 Pop: {analysis.population_psa10}")
        print(f"Monthly Sales: {analysis.monthly_sales}")
        print(f"Price Stability: {analysis.price_stability:.1%}")
        print(f"Confidence: {analysis.confidence:.1%}")
        print("\n📊 Profit Analysis")
        print(f"Total Cost: ${profit['total_cost']:.2f}")
        print(f"Expected Value: ${profit['expected_value']:.2f}")
        print(f"Potential Profit: ${profit['potential_profit']:.2f}")
        print(f"ROI: {profit['roi_percentage']:.1f}%")
