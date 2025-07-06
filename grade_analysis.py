#!/usr/bin/env python3
"""
Grade-Specific Analysis System
Tracks and analyzes population data across different grades
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from population_tracker import PopulationTracker

@dataclass
class GradeDistribution:
    total_pop: int
    grade_counts: Dict[str, int]
    gem_ratio: float  # % of PSA 10s
    high_grade_ratio: float  # % of PSA 9+
    
class GradeAnalyzer:
    def __init__(self):
        self.pop_tracker = PopulationTracker()
        
        # Grade-specific price multipliers
        self.GRADE_MULTIPLIERS = {
            'PSA': {
                '10': 5.0,   # Gem Mint
                '9': 2.0,    # Mint
                '8': 1.2,    # Near Mint-Mint
                '7': 0.8,    # Near Mint
                'raw': 0.5   # Ungraded
            },
            'BGS': {
                '10': 7.0,   # Pristine
                '9.5': 4.0,  # Gem Mint
                '9': 2.0,    # Mint
                '8.5': 1.2,  # Near Mint-Mint
                'raw': 0.5
            },
            'CGC': {
                '10': 4.0,
                '9.5': 2.5,
                '9': 1.8,
                '8.5': 1.1,
                'raw': 0.5
            }
        }
        
    def analyze_distribution(self, card_name: str, set_name: str) -> GradeDistribution:
        """Analyze the grade distribution for a card"""
        pop_data = self.pop_tracker.get_population_data(card_name, set_name)
        
        total_graded = 0
        grade_counts = {'10': 0, '9.5': 0, '9': 0, '8.5': 0, '8': 0, '7': 0}
        
        # Combine data from all grading companies
        for company in ['PSA', 'BGS', 'CGC']:
            company_data = pop_data.get(company, {})
            total_graded += company_data.get('total', 0)
            
            for grade, count in company_data.items():
                if grade in grade_counts:
                    grade_counts[grade] += count
        
        # Calculate ratios
        if total_graded > 0:
            gem_ratio = (grade_counts['10'] + grade_counts['9.5']) / total_graded
            high_grade_ratio = (grade_counts['10'] + grade_counts['9.5'] + grade_counts['9']) / total_graded
        else:
            gem_ratio = 0.0
            high_grade_ratio = 0.0
            
        return GradeDistribution(
            total_pop=total_graded,
            grade_counts=grade_counts,
            gem_ratio=gem_ratio,
            high_grade_ratio=high_grade_ratio
        )
    
    def calculate_grade_price(self, base_price: float, grade_data: GradeDistribution, 
                            grade: str, grading_company: str = 'PSA') -> float:
        """Calculate price for a specific grade based on population data"""
        if not grade_data.total_pop:
            # No population data, use standard multipliers
            return base_price * self.GRADE_MULTIPLIERS[grading_company].get(grade, 1.0)
        
        multiplier = self.GRADE_MULTIPLIERS[grading_company].get(grade, 1.0)
        
        # Adjust multiplier based on population scarcity
        if grade in ['10', '9.5']:
            if grade_data.gem_ratio < 0.01:  # Less than 1% gem mint
                multiplier *= 3.0  # Ultra rare
            elif grade_data.gem_ratio < 0.05:  # Less than 5% gem mint
                multiplier *= 2.0  # Very rare
            elif grade_data.gem_ratio < 0.10:  # Less than 10% gem mint
                multiplier *= 1.5  # Rare
                
        # Adjust for total population
        if grade_data.total_pop < 100:
            multiplier *= 1.5  # Very scarce overall
        elif grade_data.total_pop < 500:
            multiplier *= 1.2  # Scarce overall
        elif grade_data.total_pop > 5000:
            multiplier *= 0.8  # Very common
            
        return base_price * multiplier
    
    def get_grade_summary(self, card_name: str, set_name: str, base_price: float) -> Dict:
        """Get a complete grade analysis summary"""
        dist = self.analyze_distribution(card_name, set_name)
        
        summary = {
            "card_name": card_name,
            "set_name": set_name,
            "base_price": base_price,
            "population": {
                "total": dist.total_pop,
                "by_grade": dist.grade_counts,
                "gem_ratio": dist.gem_ratio,
                "high_grade_ratio": dist.high_grade_ratio
            },
            "prices": {
                "raw": base_price * 0.5,  # Ungraded price
                "graded": {}
            },
            "rarity_analysis": {
                "overall_scarcity": "Unknown",
                "gem_mint_scarcity": "Unknown",
                "investment_potential": "Unknown"
            }
        }
        
        # Calculate prices for each grade and company
        for company in ['PSA', 'BGS', 'CGC']:
            summary["prices"]["graded"][company] = {}
            for grade in self.GRADE_MULTIPLIERS[company].keys():
                if grade != 'raw':
                    price = self.calculate_grade_price(base_price, dist, grade, company)
                    summary["prices"]["graded"][company][grade] = price
        
        # Rarity analysis
        if dist.total_pop > 0:
            if dist.total_pop < 100:
                summary["rarity_analysis"]["overall_scarcity"] = "Very Rare"
            elif dist.total_pop < 500:
                summary["rarity_analysis"]["overall_scarcity"] = "Rare"
            elif dist.total_pop < 2000:
                summary["rarity_analysis"]["overall_scarcity"] = "Uncommon"
            else:
                summary["rarity_analysis"]["overall_scarcity"] = "Common"
                
            if dist.gem_ratio < 0.01:
                summary["rarity_analysis"]["gem_mint_scarcity"] = "Ultra Rare"
                summary["rarity_analysis"]["investment_potential"] = "Excellent"
            elif dist.gem_ratio < 0.05:
                summary["rarity_analysis"]["gem_mint_scarcity"] = "Very Rare"
                summary["rarity_analysis"]["investment_potential"] = "Good"
            elif dist.gem_ratio < 0.10:
                summary["rarity_analysis"]["gem_mint_scarcity"] = "Rare"
                summary["rarity_analysis"]["investment_potential"] = "Fair"
            else:
                summary["rarity_analysis"]["gem_mint_scarcity"] = "Common"
                summary["rarity_analysis"]["investment_potential"] = "Limited"
        
        return summary

def main():
    """Test the grade analysis system"""
    analyzer = GradeAnalyzer()
    
    # Test with some example cards
    test_cards = [
        ("Charizard VMAX", "Champions Path", 500.00),
        ("Lugia V", "Silver Tempest", 300.00),
        ("Pikachu VMAX", "Vivid Voltage", 200.00)
    ]
    
    for card_name, set_name, base_price in test_cards:
        print(f"\n🔍 Analyzing: {card_name} ({set_name})")
        print("=" * 60)
        
        summary = analyzer.get_grade_summary(card_name, set_name, base_price)
        
        print(f"Population Analysis:")
        print(f"- Total Graded: {summary['population']['total']}")
        print(f"- Gem Mint Ratio: {summary['population']['gem_ratio']:.1%}")
        print(f"- Overall Scarcity: {summary['rarity_analysis']['overall_scarcity']}")
        print(f"- Gem Mint Scarcity: {summary['rarity_analysis']['gem_mint_scarcity']}")
        print(f"- Investment Potential: {summary['rarity_analysis']['investment_potential']}")
        
        print("\nEstimated Prices:")
        print(f"Raw: ${summary['prices']['raw']:.2f}")
        for company, grades in summary['prices']['graded'].items():
            print(f"\n{company} Grades:")
            for grade, price in grades.items():
                print(f"- {grade}: ${price:.2f}")

if __name__ == "__main__":
    main()
