#!/usr/bin/env python3
"""
Graded Card Arbitrage Module
Handles opportunities in already-graded Pokemon cards (PSA/BGS/CGC)
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from ebay_browse_api_integration import EbayBrowseAPI
from pokemon_price_system import get_card_market_price

logger = logging.getLogger(__name__)

@dataclass
class GradedDealOpportunity:
    """Analysis of a graded card arbitrage opportunity"""
    card_name: str
    current_grade: str  # e.g., "PSA 9", "BGS 9.5" 
    listing_price: float
    market_value: float  # Current market for this grade
    comparable_grade_value: float  # Value of equivalent grade (PSA 10, etc.)
    profit_potential: float
    risk_level: str  # LOW, MEDIUM, HIGH
    turnaround_days: int
    confidence_score: float

class GradedCardAnalyzer:
    """Analyzes arbitrage opportunities in already-graded cards"""
    
    def __init__(self):
        self.ebay_api = EbayBrowseAPI()
        self.min_profit = 200  # Lower than raw cards due to faster turnaround
        self.min_roi = 1.3  # 30% minimum return (lower than raw due to less risk)
        
    def find_graded_opportunities(self, search_terms: List[str], limit: int = 50) -> List[GradedDealOpportunity]:
        """Find arbitrage opportunities in graded cards"""
        opportunities = []
        
        for term in search_terms:
            # Search for graded cards only
            items = self.ebay_api.search_pokemon_cards(
                f"{term} PSA BGS CGC graded",
                min_price=100,  # Lower minimum for graded
                max_price=2000,
                raw_only=False,  # We want graded cards
                limit=limit
            )
            
            for item in items:
                opportunity = self._analyze_graded_item(item)
                if opportunity and opportunity.profit_potential >= self.min_profit:
                    opportunities.append(opportunity)
        
        # Sort by profit potential
        return sorted(opportunities, key=lambda x: x.profit_potential, reverse=True)
    
    def _analyze_graded_item(self, item: Dict) -> Optional[GradedDealOpportunity]:
        """Analyze a single graded card listing"""
        try:
            title = item.get('title', '').upper()
            
            # Extract grade from title
            grade = self._extract_grade(title)
            if not grade:
                return None
            
            # Extract card name (simplified)
            card_name = self._extract_card_name(title)
            if not card_name:
                return None
            
            listing_price = item.get('price', 0)
            
            # Get market values for comparison
            market_value = get_card_market_price(card_name, "", grade)
            if not market_value:
                return None
            
            # Calculate profit potential
            selling_fees = listing_price * 0.13  # eBay + PayPal fees
            net_profit = market_value - listing_price - selling_fees
            roi = net_profit / listing_price if listing_price > 0 else 0
            
            if roi < self.min_roi:
                return None
            
            # Assess risk based on grade and card popularity
            risk_level = self._assess_risk(grade, card_name, roi)
            
            return GradedDealOpportunity(
                card_name=card_name,
                current_grade=grade,
                listing_price=listing_price,
                market_value=market_value,
                comparable_grade_value=market_value,
                profit_potential=net_profit,
                risk_level=risk_level,
                turnaround_days=14,  # Much faster than raw cards
                confidence_score=0.8 if 'PSA 10' in grade else 0.6
            )
            
        except Exception as e:
            logger.warning(f"Error analyzing graded item: {e}")
            return None
    
    def _extract_grade(self, title: str) -> Optional[str]:
        """Extract PSA/BGS/CGC grade from title"""
        title = title.upper()
        
        # PSA grades
        for grade in ['PSA 10', 'PSA 9', 'PSA 8', 'PSA 7']:
            if grade in title:
                return grade
        
        # BGS grades  
        for grade in ['BGS 10', 'BGS 9.5', 'BGS 9', 'BGS 8.5']:
            if grade in title:
                return grade
        
        # CGC grades
        for grade in ['CGC 10', 'CGC 9.5', 'CGC 9']:
            if grade in title:
                return grade
        
        return None
    
    def _extract_card_name(self, title: str) -> Optional[str]:
        """Extract card name from graded card title"""
        # Simplified extraction - in production would be more sophisticated
        common_cards = [
            'CHARIZARD', 'BLASTOISE', 'VENUSAUR', 'PIKACHU', 
            'LUGIA', 'HO-OH', 'RAYQUAZA', 'MEWTWO'
        ]
        
        title_upper = title.upper()
        for card in common_cards:
            if card in title_upper:
                return card.title()
        
        return None
    
    def _assess_risk(self, grade: str, card_name: str, roi: float) -> str:
        """Assess risk level for graded card arbitrage"""
        # PSA 10s are lowest risk
        if 'PSA 10' in grade or 'BGS 10' in grade:
            return 'LOW'
        
        # High ROI on lower grades = higher risk
        if roi > 0.5:  # 50%+ ROI on graded card is suspicious
            return 'HIGH'
        
        # Popular cards are lower risk
        if card_name.upper() in ['CHARIZARD', 'PIKACHU']:
            return 'LOW' if roi < 0.3 else 'MEDIUM'
        
        return 'MEDIUM'

# Example usage and testing
if __name__ == "__main__":
    analyzer = GradedCardAnalyzer()
    
    # Test with popular card searches
    search_terms = [
        "Charizard Base Set",
        "Blastoise Base Set", 
        "Pikachu Illustrator"
    ]
    
    opportunities = analyzer.find_graded_opportunities(search_terms, limit=20)
    
    print(f"\n🏆 Found {len(opportunities)} graded card opportunities:")
    for i, opp in enumerate(opportunities[:5], 1):
        print(f"{i}. {opp.card_name} {opp.current_grade}")
        print(f"   💰 Profit: ${opp.profit_potential:.2f}")
        print(f"   ⚠️ Risk: {opp.risk_level}")
        print(f"   ⏱️ Turnaround: {opp.turnaround_days} days")
        print()
