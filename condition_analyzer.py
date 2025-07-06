#!/usr/bin/env python3
"""
Smart Condition Analyzer
Automatically assess card conditions and values from listings
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ConditionAssessment:
    condition: str
    confidence: float
    multiplier: float
    grading_company: Optional[str] = None
    grade: Optional[str] = None
    notes: List[str] = None

class SmartConditionAnalyzer:
    """Analyze card conditions from listing data"""
    
    def __init__(self, guide_path: str = "condition_guide.json"):
        self.guide_path = guide_path
        self.load_guide()
    
    def load_guide(self):
        """Load the condition guide"""
        with open(self.guide_path, 'r') as f:
            self.guide = json.load(f)
    
    def detect_graded_card(self, title: str, description: str = "") -> Optional[Tuple[str, str]]:
        """Detect if card is graded and by which company"""
        text = f"{title} {description}".lower()
        
        for company, identifiers in self.guide['grading_company_identifiers'].items():
            if any(id.lower() in text for id in identifiers):
                # Look for grade number
                grade_match = re.search(r'(?:' + company + r')\s*(\d+(?:\.\d)?)', text, re.IGNORECASE)
                if grade_match:
                    return company, grade_match.group(1)
                
                # Look for special labels
                for label in self.guide['grading_companies'][company]['special_labels'].keys():
                    if label.lower() in text:
                        return company, label
        
        return None
    
    def assess_raw_condition(self, title: str, description: str = "", 
                           seller_rating: float = None) -> ConditionAssessment:
        """Assess condition of a raw card"""
        text = f"{title} {description}".lower()
        confidence_mods = []
        condition_hints = []
        
        # Start with default condition
        best_condition = "Good"
        base_confidence = 0.5
        
        # Check explicit condition mentions
        for cond, data in self.guide['raw_conditions'].items():
            if any(kw.lower() in text for kw in data['keywords']):
                best_condition = cond
                base_confidence = data['confidence']
                condition_hints.append(f"Explicitly mentioned: {cond}")
                break
        
        # Apply keyword modifiers
        for impact, words in self.guide['automatic_condition_keywords']['negative'].items():
            if any(word in text for word in words):
                if impact == 'heavy_impact':
                    best_condition = "Good"
                    condition_hints.append(f"Heavy negative: {', '.join(w for w in words if w in text)}")
                elif impact == 'medium_impact' and best_condition in ['Near Mint/Mint', 'Near Mint']:
                    best_condition = "Excellent"
                    condition_hints.append(f"Medium negative: {', '.join(w for w in words if w in text)}")
                elif impact == 'light_impact' and best_condition == 'Near Mint/Mint':
                    best_condition = "Near Mint"
                    condition_hints.append(f"Light negative: {', '.join(w for w in words if w in text)}")
        
        # Check positive indicators
        for confidence, words in self.guide['automatic_condition_keywords']['positive'].items():
            if any(word in text for word in words):
                if confidence == 'high_confidence' and 'heavy_impact' not in condition_hints:
                    best_condition = "Near Mint/Mint"
                    base_confidence += 0.1
                    condition_hints.append(f"Strong positive: {', '.join(w for w in words if w in text)}")
                elif confidence == 'medium_confidence' and 'medium_impact' not in condition_hints:
                    best_condition = "Near Mint"
                    base_confidence += 0.05
                    condition_hints.append(f"Medium positive: {', '.join(w for w in words if w in text)}")
        
        # Apply confidence modifiers
        if "clear photos" in text.lower():
            base_confidence += self.guide['listing_confidence_rules']['has_clear_photos']
            confidence_mods.append("Clear photos provided")
            
        if any(flaw in text.lower() for flaw in ['whitening', 'scratch', 'wear', 'damage']):
            base_confidence += self.guide['listing_confidence_rules']['mentions_specific_flaws']
            confidence_mods.append("Specific flaws mentioned")
        
        # Apply seller rating impact
        if seller_rating:
            for threshold, impact in self.guide['listing_confidence_rules']['seller_rating_impact'].items():
                if (threshold == '99+' and seller_rating >= 99) or \
                   (threshold == '98-99' and 98 <= seller_rating < 99) or \
                   (threshold == '95-97' and 95 <= seller_rating < 98) or \
                   (threshold == '<95' and seller_rating < 95):
                    base_confidence += impact
                    confidence_mods.append(f"Seller rating: {seller_rating}%")
                    break
        
        # Get multiplier for condition
        multiplier = self.guide['raw_conditions'][best_condition]['multiplier']
        
        # Cap confidence at 0.95
        final_confidence = min(base_confidence, 0.95)
        
        return ConditionAssessment(
            condition=best_condition,
            confidence=final_confidence,
            multiplier=multiplier,
            notes=condition_hints + confidence_mods
        )
    
    def assess_graded_card(self, company: str, grade: str) -> ConditionAssessment:
        """Assess a graded card"""
        company_data = self.guide['grading_companies'][company]
        
        # Check for special labels first
        if grade in company_data['special_labels']:
            multiplier = company_data['special_labels'][grade]
            confidence = company_data['confidence']
            notes = [f"{company} special label: {grade}"]
        else:
            # Regular numeric grade
            multiplier = company_data['multipliers'].get(str(grade), 0.5)
            confidence = company_data['confidence']
            notes = [f"{company} grade: {grade}"]
        
        return ConditionAssessment(
            condition="Graded",
            grading_company=company,
            grade=grade,
            confidence=confidence,
            multiplier=multiplier,
            notes=notes
        )
    
    def assess_listing(self, title: str, description: str = "", 
                      seller_rating: float = None) -> ConditionAssessment:
        """Assess condition from a full listing"""
        # First check if it's graded
        graded = self.detect_graded_card(title, description)
        if graded:
            company, grade = graded
            return self.assess_graded_card(company, grade)
        
        # If not graded, assess raw condition
        return self.assess_raw_condition(title, description, seller_rating)
    
    def calculate_value(self, base_price: float, assessment: ConditionAssessment) -> float:
        """Calculate actual value based on condition assessment"""
        return round(base_price * assessment.multiplier, 2)

def main():
    """Test the condition analyzer"""
    analyzer = SmartConditionAnalyzer()
    
    # Test cases
    test_listings = [
        {
            "title": "PSA 10 Charizard VMAX Champions Path",
            "description": "Perfect gem mint condition",
            "seller_rating": 99.8
        },
        {
            "title": "Charizard VMAX Champions Path",
            "description": "Pack fresh, mint condition. Never played",
            "seller_rating": 98.5
        },
        {
            "title": "Charizard VMAX Champions Path - Played",
            "description": "Light whitening on corners, some edge wear",
            "seller_rating": 95.0
        }
    ]
    
    print("\n🔍 Smart Condition Analysis")
    print("=" * 50)
    
    for listing in test_listings:
        print(f"\nListing: {listing['title']}")
        assessment = analyzer.assess_listing(
            listing['title'],
            listing['description'],
            listing['seller_rating']
        )
        
        print(f"Condition: {assessment.condition}")
        if assessment.grade:
            print(f"Grade: {assessment.grading_company} {assessment.grade}")
        print(f"Confidence: {assessment.confidence:.1%}")
        print(f"Price Multiplier: {assessment.multiplier}x")
        print("Notes:")
        for note in assessment.notes:
            print(f"  • {note}")
        
        # Example value calculation
        base_price = 100.00
        adjusted_value = analyzer.calculate_value(base_price, assessment)
        print(f"Value: ${adjusted_value:.2f} (from ${base_price:.2f} base)")

if __name__ == "__main__":
    main()
