#!/usr/bin/env python3
"""
Vault Eligibility Safety Checker
Ensures cards maintain $250+ value even with poor grading outcomes
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class VaultSafetyAnalysis:
    """Analysis of vault safety for a potential deal"""
    raw_purchase_price: float
    worst_case_grade: str
    worst_case_value: float
    vault_eligible_worst_case: bool
    safety_margin: float
    recommended_action: str
    risk_level: str

class VaultEligibilityChecker:
    """Ensures cards remain vault-eligible even with poor grading outcomes"""
    
    def __init__(self):
        self.VAULT_MINIMUM = 250.0  # eBay Vault requirement
        self.SAFETY_BUFFER = 50.0   # Additional buffer for peace of mind
        self.MIN_SAFE_VALUE = self.VAULT_MINIMUM + self.SAFETY_BUFFER  # $300 minimum
        
        # Conservative grade multipliers (raw card base = 1.0)
        self.GRADE_MULTIPLIERS = {
            'PSA 10': 4.0,   # Best case
            'PSA 9': 2.2,    # Good case
            'PSA 8': 1.4,    # Okay case  
            'PSA 7': 0.9,    # Poor case (often BELOW raw value!)
            'PSA 6': 0.6,    # Bad case
            'PSA 5': 0.4,    # Terrible case
        }
    
    def check_vault_safety(
        self,
        card_name: str,
        set_name: str,
        raw_purchase_price: float,
        raw_market_value: float,
        condition_confidence: float = 0.8
    ) -> VaultSafetyAnalysis:
        """
        Check if a card purchase is safe for vault storage even with poor grading
        
        Args:
            card_name: Name of the card
            set_name: Set name
            raw_purchase_price: What you're paying for the raw card
            raw_market_value: Current market value of raw card
            condition_confidence: How confident you are in condition (0-1)
            
        Returns:
            VaultSafetyAnalysis with safety assessment
        """
        
        # Determine worst-case grade based on condition confidence
        if condition_confidence >= 0.9:
            worst_case_grade = 'PSA 8'  # Even excellent cards can grade PSA 8
        elif condition_confidence >= 0.7:
            worst_case_grade = 'PSA 7'  # Good cards might grade PSA 7
        else:
            worst_case_grade = 'PSA 6'  # Risky cards could grade PSA 6
        
        # Calculate worst-case value
        multiplier = self.GRADE_MULTIPLIERS[worst_case_grade]
        worst_case_value = raw_market_value * multiplier
        
        # Check vault eligibility
        vault_eligible = worst_case_value >= self.VAULT_MINIMUM
        safety_margin = worst_case_value - self.VAULT_MINIMUM
        
        # Determine risk level and recommendation
        if worst_case_value >= self.MIN_SAFE_VALUE:
            risk_level = "LOW"
            recommendation = "SAFE - Vault eligible even in worst case"
        elif vault_eligible:
            risk_level = "MEDIUM" 
            recommendation = "CAUTION - Barely vault eligible in worst case"
        else:
            risk_level = "HIGH"
            recommendation = "DANGEROUS - May not be vault eligible if grades poorly"
        
        return VaultSafetyAnalysis(
            raw_purchase_price=raw_purchase_price,
            worst_case_grade=worst_case_grade,
            worst_case_value=worst_case_value,
            vault_eligible_worst_case=vault_eligible,
            safety_margin=safety_margin,
            recommended_action=recommendation,
            risk_level=risk_level
        )
    
    def get_minimum_safe_raw_value(self, condition_confidence: float = 0.8) -> float:
        """
        Calculate minimum raw card value needed to ensure vault eligibility
        """
        # Determine worst-case multiplier
        if condition_confidence >= 0.9:
            worst_multiplier = self.GRADE_MULTIPLIERS['PSA 8']
        elif condition_confidence >= 0.7:
            worst_multiplier = self.GRADE_MULTIPLIERS['PSA 7']
        else:
            worst_multiplier = self.GRADE_MULTIPLIERS['PSA 6']
        
        # Calculate minimum raw value needed
        min_raw_value = self.MIN_SAFE_VALUE / worst_multiplier
        
        return min_raw_value
    
    def analyze_grade_scenario_risk(self, raw_market_value: float) -> Dict[str, Dict]:
        """Analyze vault eligibility across all possible grades"""
        scenarios = {}
        
        for grade, multiplier in self.GRADE_MULTIPLIERS.items():
            graded_value = raw_market_value * multiplier
            vault_eligible = graded_value >= self.VAULT_MINIMUM
            
            scenarios[grade] = {
                'graded_value': graded_value,
                'vault_eligible': vault_eligible,
                'safety_margin': graded_value - self.VAULT_MINIMUM,
                'probability': self._get_grade_probability(grade)
            }
        
        return scenarios
    
    def _get_grade_probability(self, grade: str) -> float:
        """Estimate probability of each grade (simplified)"""
        probabilities = {
            'PSA 10': 0.15,
            'PSA 9': 0.35, 
            'PSA 8': 0.30,
            'PSA 7': 0.15,
            'PSA 6': 0.04,
            'PSA 5': 0.01
        }
        return probabilities.get(grade, 0.0)

# Integration with existing opportunity ranker
def check_deal_vault_safety(
    card_name: str,
    set_name: str, 
    listing_price: float,
    raw_market_value: float,
    condition_desc: str = ""
) -> Tuple[bool, VaultSafetyAnalysis]:
    """
    Quick vault safety check for deal evaluation
    
    Returns:
        (is_safe, safety_analysis)
    """
    checker = VaultEligibilityChecker()
    
    # Estimate condition confidence from description
    condition_confidence = estimate_condition_confidence(condition_desc)
    
    analysis = checker.check_vault_safety(
        card_name=card_name,
        set_name=set_name,
        raw_purchase_price=listing_price,
        raw_market_value=raw_market_value,
        condition_confidence=condition_confidence
    )
    
    is_safe = analysis.risk_level in ['LOW', 'MEDIUM'] and analysis.vault_eligible_worst_case
    
    return is_safe, analysis

def estimate_condition_confidence(condition_desc: str) -> float:
    """Estimate condition confidence from listing description"""
    desc_lower = condition_desc.lower()
    
    # High confidence indicators
    if any(word in desc_lower for word in ['mint', 'gem', 'perfect', 'pack fresh']):
        return 0.9
    
    # Medium confidence indicators  
    elif any(word in desc_lower for word in ['near mint', 'nm', 'excellent']):
        return 0.8
    
    # Lower confidence indicators
    elif any(word in desc_lower for word in ['very good', 'vg']):
        return 0.6
    
    # Risk indicators
    elif any(word in desc_lower for word in ['played', 'wear', 'edge', 'crease']):
        return 0.4
    
    # Unknown condition
    else:
        return 0.7

# Example usage and testing
if __name__ == "__main__":
    checker = VaultEligibilityChecker()
    
    print("🏦 Vault Eligibility Safety Checker")
    print("=" * 50)
    
    # Test scenarios
    test_cards = [
        {
            'name': 'Charizard Base Set',
            'set': 'Base Set Shadowless',
            'purchase_price': 350.0,
            'raw_market_value': 450.0,
            'condition': 'Near Mint - pack fresh',
        },
        {
            'name': 'Blastoise Base Set', 
            'set': 'Base Set Shadowless',
            'purchase_price': 280.0,
            'raw_market_value': 320.0,
            'condition': 'Very Good - some edge wear',
        },
        {
            'name': 'Pikachu VMAX',
            'set': 'Vivid Voltage', 
            'purchase_price': 180.0,
            'raw_market_value': 220.0,
            'condition': 'Near Mint',
        }
    ]
    
    for card in test_cards:
        print(f"\n🎴 {card['name']} - ${card['purchase_price']}")
        print("-" * 40)
        
        condition_confidence = estimate_condition_confidence(card['condition'])
        analysis = checker.check_vault_safety(
            card['name'],
            card['set'],
            card['purchase_price'],
            card['raw_market_value'],
            condition_confidence
        )
        
        print(f"Condition Confidence: {condition_confidence:.1%}")
        print(f"Worst Case Grade: {analysis.worst_case_grade}")
        print(f"Worst Case Value: ${analysis.worst_case_value:.2f}")
        print(f"Vault Eligible (Worst): {'✅ YES' if analysis.vault_eligible_worst_case else '❌ NO'}")
        print(f"Safety Margin: ${analysis.safety_margin:.2f}")
        print(f"Risk Level: {analysis.risk_level}")
        print(f"Recommendation: {analysis.recommended_action}")
        
        # Show grade scenarios
        scenarios = checker.analyze_grade_scenario_risk(card['raw_market_value'])
        print(f"\n📊 Grade Scenarios:")
        for grade, scenario in scenarios.items():
            eligible = "✅" if scenario['vault_eligible'] else "❌"
            print(f"  {grade}: ${scenario['graded_value']:.0f} {eligible} ({scenario['probability']:.1%} chance)")
    
    print(f"\n💡 Minimum Safe Raw Values:")
    for confidence in [0.9, 0.8, 0.7, 0.6]:
        min_value = checker.get_minimum_safe_raw_value(confidence)
        print(f"  {confidence:.0%} confidence: ${min_value:.0f}+ raw value needed")
