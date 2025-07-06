#!/usr/bin/env python3
"""
Raw to Graded Profit Calculator
Calculates potential profit for raw cards being graded through eBay's PSA service
"""

from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class GradingCosts:
    """Standard PSA grading costs through eBay"""
    BASIC_TIER = 25  # Standard PSA through eBay
    FAST_TIER = 50   # Faster turnaround
    VAULT_FEE = 0    # No fee for seller
    BUYER_FEE = 0.03 # 3% paid by buyer

@dataclass
class GradeDistribution:
    """Typical grade probability distribution for NM raw cards"""
    PSA_10 = 0.15  # 15% chance of PSA 10
    PSA_9 = 0.35   # 35% chance of PSA 9
    PSA_8 = 0.35   # 35% chance of PSA 8
    PSA_7 = 0.15   # 15% chance of PSA 7 or lower

def calculate_expected_profit(
    raw_price: float,
    psa10_price: float,
    psa9_price: float,
    psa8_price: float,
    psa7_price: float,
    condition_confidence: float = 0.8,
    grading_tier: str = 'BASIC'
) -> Tuple[float, Dict[str, float], bool]:
    """
    Calculate expected profit for grading a raw card through eBay PSA
    
    Args:
        raw_price: Purchase price of raw card
        psa10_price: Recent PSA 10 sales price
        psa9_price: Recent PSA 9 sales price
        psa8_price: Recent PSA 8 sales price  
        psa7_price: Recent PSA 7 sales price
        condition_confidence: How confident we are in condition (0-1)
        grading_tier: 'BASIC' or 'FAST'
    
    Returns:
        (expected_profit, details, should_grade)
    """
    # Adjust grade distribution based on condition confidence
    dist = GradeDistribution()
    if condition_confidence < 0.8:
        # Lower confidence = shift distribution down
        dist.PSA_10 *= condition_confidence
        dist.PSA_9 = 0.30
        dist.PSA_8 = 0.40
        dist.PSA_7 = 1 - (dist.PSA_10 + dist.PSA_9 + dist.PSA_8)
    
    # Calculate grading costs
    grading_cost = (
        GradingCosts.FAST_TIER 
        if grading_tier == 'FAST' 
        else GradingCosts.BASIC_TIER
    )
    
    # Calculate expected value
    expected_value = (
        (dist.PSA_10 * psa10_price) +
        (dist.PSA_9 * psa9_price) +
        (dist.PSA_8 * psa8_price) +
        (dist.PSA_7 * psa7_price)
    )
    
    # Calculate total costs
    total_cost = raw_price + grading_cost
    
    # Calculate expected profit
    expected_profit = expected_value - total_cost
    
    # Calculate ROI percentage
    roi_percentage = (expected_profit / total_cost) * 100
    
    details = {
        'raw_price': raw_price,
        'grading_cost': grading_cost,
        'expected_value': expected_value,
        'expected_profit': expected_profit,
        'roi_percentage': roi_percentage,
        'psa10_profit': psa10_price - total_cost,
        'psa9_profit': psa9_price - total_cost,
        'psa8_profit': psa8_price - total_cost,
        'psa7_profit': psa7_price - total_cost,
        'psa10_chance': dist.PSA_10 * 100,
        'condition_confidence': condition_confidence * 100
    }
    
    # Recommend grading if:
    # 1. Expected ROI > 30%
    # 2. PSA 9 profit is still positive (safety)
    should_grade = (
        roi_percentage > 30 and
        details['psa9_profit'] > 0
    )
    
    return expected_profit, details, should_grade

def print_grading_analysis(details: Dict[str, float]) -> None:
    """Pretty print the grading analysis"""
    print("\n📊 Raw → Graded Analysis")
    print("=" * 40)
    print(f"Raw Price: ${details['raw_price']:.2f}")
    print(f"Grading Cost: ${details['grading_cost']:.2f}")
    print(f"Condition Confidence: {details['condition_confidence']:.1f}%")
    print("\n💰 Profit Scenarios:")
    print(f"PSA 10 (${details['psa10_chance']:.1f}% chance): ${details['psa10_profit']:.2f}")
    print(f"PSA 9: ${details['psa9_profit']:.2f}")
    print(f"PSA 8: ${details['psa8_profit']:.2f}")
    print(f"PSA 7: ${details['psa7_profit']:.2f}")
    print("\n📈 Summary:")
    print(f"Expected Value: ${details['expected_value']:.2f}")
    print(f"Expected Profit: ${details['expected_profit']:.2f}")
    print(f"ROI: {details['roi_percentage']:.1f}%")
    print("=" * 40)

if __name__ == "__main__":
    # Example usage
    profit, details, should_grade = calculate_expected_profit(
        raw_price=60,
        psa10_price=150,
        psa9_price=100,
        psa8_price=80,
        psa7_price=60,
        condition_confidence=0.9
    )
    
    print_grading_analysis(details)
    print(f"\n🤖 Bot Decision: {'Grade ✅' if should_grade else 'Skip ❌'}")
