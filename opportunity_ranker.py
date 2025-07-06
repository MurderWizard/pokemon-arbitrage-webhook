#!/usr/bin/env python3
"""
Pokemon Card Opportunity Ranker with Images
Advanced opportunity scoring and ranking system using Browse API data
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from ebay_browse_api_integration import EbayBrowseAPI

@dataclass
class OpportunityScore:
    """Detailed opportunity scoring breakdown"""
    card_name: str
    total_score: float
    profit_potential: float
    confidence_score: float
    risk_score: float
    time_to_sell: int  # days
    grading_potential: str
    market_trend: str
    image_url: str
    listing_url: str
    seller_rating: float
    condition: str
    price: float
    estimated_psa10_value: float
    
class OpportunityRanker:
    """Ranks Pokemon card arbitrage opportunities with advanced scoring"""
    
    def __init__(self):
        self.ebay_api = EbayBrowseAPI()
        self.opportunity_cache = []
        
        # Profit thresholds optimized for limited capital ($1K-$2K bankroll)
        self.min_profit_threshold = 400  # $400 minimum profit - realistic for single-deal focus
        self.min_roi_multiple = 3.0  # 3x minimum return
        self.max_deal_size = 600  # Maximum $600 per deal (30% of $2K bankroll)
        
        # Vault safety requirements - CRITICAL for hands-off operation
        self.require_vault_safety = True  # Must remain vault-eligible even with poor grading
        self.vault_minimum = 250.0  # eBay requirement
        self.safety_buffer = 50.0   # Extra buffer for peace of mind
        
        # Future expansion: Consider adding graded deal support for additional opportunities
        # This would require separate logic for already-graded cards vs raw cards
        self.enable_graded_deals = False  # Set to True to expand beyond raw cards
        
    def score_opportunity(self, item: Dict, estimated_psa10_value: float) -> OpportunityScore:
        """Score an individual opportunity with detailed breakdown"""
        
        # Basic calculations
        raw_price = item['price']
        shipping_cost = item.get('shipping_cost', 0)
        total_cost = raw_price + shipping_cost
        
        # 🛡️ CRITICAL: Vault eligibility safety check
        from vault_eligibility_checker import check_deal_vault_safety
        
        card_name = item.get('title', 'Unknown Card')
        # Extract basic info for vault check
        raw_market_value = total_cost * 1.2  # Conservative estimate for vault check
        
        vault_safe, safety_analysis = check_deal_vault_safety(
            card_name=card_name,
            set_name="Unknown",  # Will be improved with better parsing
            listing_price=total_cost,
            raw_market_value=raw_market_value,
            condition_desc=item.get('condition', '')
        )
        
        # 🚨 REJECT ANY DEAL THAT ISN'T VAULT-SAFE IN WORST CASE
        if not vault_safe:
            return OpportunityScore(
                card_name=f"❌ {card_name[:20]}...",
                total_score=0.0,  # Zero score = automatic rejection
                profit_potential=0.0,
                confidence_score=0.0,
                risk_score=100.0,  # Maximum risk
                time_to_sell=999,
                grading_potential=f"⚠️ VAULT RISK: {safety_analysis.recommended_action}",
                market_trend="Rejected - Vault safety",
                image_url=item.get('image_url', ''),
                listing_url=item.get('url', ''),
                seller_rating=0.0,
                condition="VAULT UNSAFE",
                price=total_cost,
                estimated_psa10_value=0.0
            )
        
        # ✅ Only continue scoring if vault-safe
        # Estimated costs
        grading_cost = 50  # PSA grading
        selling_fees = estimated_psa10_value * 0.13  # eBay + PayPal fees
        
        # Net profit calculation
        gross_profit = estimated_psa10_value - total_cost - grading_cost - selling_fees
        roi_multiple = estimated_psa10_value / total_cost if total_cost > 0 else 0
        
        # Scoring factors (0-100 each)
        profit_score = min(100, (gross_profit / 2000) * 100)  # $2000 = 100 points
        roi_score = min(100, ((roi_multiple - 1) / 4) * 100)  # 5x ROI = 100 points
        
        # Seller confidence
        seller_feedback = item.get('seller_feedback', 0)
        seller_score = min(100, seller_feedback) if seller_feedback > 95 else 50
        
        # Condition assessment
        condition = item.get('condition', '').lower()
        condition_score = self._score_condition(condition, item['title'])
        
        # Market trend (simplified - would use historical data in production)
        card_name = self._extract_card_name(item['title'])
        trend_score = self._estimate_market_trend(card_name)
        
        # Risk factors - include vault safety in risk assessment
        risk_factors = []
        if seller_feedback < 98: risk_factors.append("Seller risk")
        if "played" in condition: risk_factors.append("Condition risk")
        if roi_multiple < 3: risk_factors.append("Low ROI")
        if not vault_safe: risk_factors.append("Vault eligibility risk")
        
        risk_score = max(0, 100 - len(risk_factors) * 20)
        
        # Weighted total score
        weights = {
            'profit': 0.3,
            'roi': 0.25,
            'seller': 0.15,
            'condition': 0.15,
            'trend': 0.1,
            'risk': 0.05
        }
        
        total_score = (
            profit_score * weights['profit'] +
            roi_score * weights['roi'] +
            seller_score * weights['seller'] +
            condition_score * weights['condition'] +
            trend_score * weights['trend'] +
            risk_score * weights['risk']
        )
        
        return OpportunityScore(
            card_name=card_name,
            total_score=round(total_score, 1),
            profit_potential=round(gross_profit, 2),
            confidence_score=round((seller_score + condition_score) / 2, 1),
            risk_score=round(100 - risk_score, 1),
            time_to_sell=self._estimate_sell_time(card_name),
            grading_potential=self._assess_grading_potential(condition, item['title']) + 
                             (f" (Vault Safe: {safety_analysis.worst_case_grade} = ${safety_analysis.worst_case_value:.0f})" if vault_safe else " ⚠️ VAULT RISK"),
            market_trend=self._get_trend_description(trend_score),
            image_url=item.get('image_url', ''),
            listing_url=item.get('url', ''),
            seller_rating=seller_feedback,
            condition=condition.title(),
            price=total_cost,
            estimated_psa10_value=estimated_psa10_value
        )
    
    def _score_condition(self, condition: str, title: str) -> float:
        """Score based on condition for grading potential"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['mint', 'nm', 'near mint']):
            return 90
        elif any(word in title_lower for word in ['excellent', 'ex']):
            return 75
        elif any(word in title_lower for word in ['very good', 'vg']):
            return 60
        elif any(word in title_lower for word in ['good', 'played']):
            return 30
        else:
            return 70  # Unknown condition
    
    def _extract_card_name(self, title: str) -> str:
        """Extract the main card name from listing title"""
        # Simplified extraction - would use ML in production
        title_words = title.split()
        
        # Common patterns for Pokemon card names
        if 'charizard' in title.lower():
            return 'Charizard'
        elif 'blastoise' in title.lower():
            return 'Blastoise'
        elif 'venusaur' in title.lower():
            return 'Venusaur'
        elif 'pikachu' in title.lower():
            return 'Pikachu'
        else:
            # Return first two capitalized words
            cap_words = [w for w in title_words if w[0].isupper() and len(w) > 2]
            return ' '.join(cap_words[:2]) if cap_words else 'Unknown Card'
    
    def _estimate_market_trend(self, card_name: str) -> float:
        """Estimate market trend score (would use real data in production)"""
        # High-value cards with strong trends
        hot_cards = {
            'Charizard': 85,
            'Pikachu Illustrator': 95,
            'Trophy Pikachu': 90,
            'Blastoise': 75,
            'Venusaur': 70
        }
        
        for card, score in hot_cards.items():
            if card.lower() in card_name.lower():
                return score
        
        return 60  # Default trend score
    
    def _estimate_sell_time(self, card_name: str) -> int:
        """Estimate days to sell after grading"""
        # High-demand cards sell faster
        if any(name in card_name.lower() for name in ['charizard', 'pikachu']):
            return 30
        else:
            return 45
    
    def _assess_grading_potential(self, condition: str, title: str) -> str:
        """Assess likelihood of PSA 10"""
        if 'mint' in condition or 'mint' in title.lower():
            return "High PSA 10 potential"
        elif 'excellent' in condition:
            return "Moderate PSA 9-10 potential"
        else:
            return "Conservative PSA 8-9 expected"
    
    def _get_trend_description(self, trend_score: float) -> str:
        """Convert trend score to description"""
        if trend_score >= 85:
            return "🚀 Hot market"
        elif trend_score >= 70:
            return "📈 Stable growth"
        else:
            return "📊 Steady demand"
    
    def find_ranked_opportunities(self, limit: int = 20, include_graded: bool = False) -> List[OpportunityScore]:
        """Find and rank the best arbitrage opportunities"""
        
        print(f"🔍 Scanning for Pokemon card arbitrage opportunities...")
        print(f"📊 Using Browse API for up to 10,000 items per search")
        
        if include_graded:
            print(f"🏆 Including both RAW and GRADED card opportunities")
        else:
            print(f"🎯 RAW cards only (for PSA grading strategy)")
        
        # High-value search terms with estimated PSA 10 values
        search_targets = [
            ("Charizard Base Set Shadowless", 4500),
            ("Blastoise Base Set Shadowless", 2800),
            ("Venusaur Base Set Shadowless", 2200),
            ("Charizard Neo Genesis", 3200),
            ("Lugia Neo Genesis", 2600),
            ("Pikachu Illustrator", 45000),
            ("Trophy Pikachu", 8500),
            ("Charizard Team Rocket", 1800)
        ]
        
        all_opportunities = []
        
        # Phase 1: Raw card opportunities (current strategy)
        for search_term, estimated_value in search_targets:
            print(f"   🎯 Searching: {search_term}")
            
            # Use Browse API efficiency
            items = self.ebay_api.search_pokemon_cards(
                search_term,
                min_price=200,  # Minimum for high-value arbitrage
                max_price=estimated_value * 0.6,  # Max 60% of PSA 10 value
                raw_only=True,  # Raw cards for grading
                limit=1000  # Browse API can handle 1000+ items!
            )
            
            print(f"      📦 Found {len(items)} potential RAW opportunities")
            
            for item in items:
                try:
                    score = self.score_opportunity(item, estimated_value)
                    
                    # Filter for high-quality opportunities
                    if (score.profit_potential >= self.min_profit_threshold and 
                        score.total_score >= 70 and
                        score.price <= estimated_value * 0.5):  # Max 50% of PSA 10 value
                        
                        all_opportunities.append(score)
                        
                except Exception as e:
                    print(f"      ⚠️ Error scoring item: {e}")
                    continue
        
        # Phase 2: Graded card opportunities (future expansion)
        if include_graded and self.enable_graded_deals:
            print(f"\n🏆 Searching for GRADED card opportunities...")
            try:
                from graded_card_analyzer import GradedCardAnalyzer
                graded_analyzer = GradedCardAnalyzer()
                
                graded_terms = [term.split()[0] for term, _ in search_targets[:4]]  # Top 4 cards
                graded_opportunities = graded_analyzer.find_graded_opportunities(graded_terms, limit=50)
                
                print(f"      📦 Found {len(graded_opportunities)} graded opportunities")
                
                # Convert graded opportunities to OpportunityScore format
                for graded_opp in graded_opportunities:
                    if graded_opp.profit_potential >= 200:  # Lower threshold for graded
                        score = OpportunityScore(
                            card_name=f"{graded_opp.card_name} {graded_opp.current_grade}",
                            total_score=85.0,  # Base score for graded cards
                            profit_potential=graded_opp.profit_potential,
                            confidence_score=graded_opp.confidence_score * 100,
                            risk_score=100 - (30 if graded_opp.risk_level == 'HIGH' else 15),
                            time_to_sell=graded_opp.turnaround_days,
                            grading_potential="Already graded",
                            market_trend="📊 Steady demand",
                            image_url="",
                            listing_url="",
                            seller_rating=95.0,  # Default for graded
                            condition=graded_opp.current_grade,
                            price=graded_opp.listing_price,
                            estimated_psa10_value=graded_opp.market_value
                        )
                        all_opportunities.append(score)
                        
            except ImportError:
                print(f"      ⚠️ Graded card analyzer not available")
            except Exception as e:
                print(f"      ⚠️ Error analyzing graded cards: {e}")

        # Sort by total score (highest first)
        ranked_opportunities = sorted(all_opportunities, key=lambda x: x.total_score, reverse=True)
        
        print(f"\n✅ Found {len(ranked_opportunities)} high-quality opportunities")
        return ranked_opportunities[:limit]
    
    def format_opportunity_for_telegram(self, opp: OpportunityScore, rank: int) -> str:
        """Format opportunity for Telegram display with image"""
        
        roi_multiple = opp.estimated_psa10_value / opp.price if opp.price > 0 else 0
        
        message = f"""
🏆 #{rank} OPPORTUNITY (Score: {opp.total_score}/100)

🎴 **{opp.card_name}**
💰 **Profit: ${opp.profit_potential:,.0f}** ({roi_multiple:.1f}x ROI)

📊 **Details:**
• Price: ${opp.price:,.0f}
• PSA 10 Est: ${opp.estimated_psa10_value:,.0f}
• Condition: {opp.condition}
• Seller: {opp.seller_rating:.1f}% feedback

🎯 **Assessment:**
• Confidence: {opp.confidence_score}/100
• Risk Level: {opp.risk_score}/100
• {opp.grading_potential}
• {opp.market_trend}
• Est. sell time: {opp.time_to_sell} days

🔗 [View Listing]({opp.listing_url})
{"⚠️ *Demo Mode - Mock eBay URLs*" if "example" in opp.listing_url or "123456" in opp.listing_url else ""}
"""
        
        if opp.image_url:
            message += f"\n📸 [View Image]({opp.image_url})"
            if "example" in opp.image_url:
                message += " ⚠️ *Demo image*"
        
        return message.strip()

def main():
    """Demo the opportunity ranking system"""
    
    print("🚀 Pokemon Card Opportunity Ranker - Browse API Edition")
    print("=" * 60)
    
    ranker = OpportunityRanker()
    
    # Find top opportunities
    opportunities = ranker.find_ranked_opportunities(limit=10)
    
    if opportunities:
        print(f"\n🏆 TOP {len(opportunities)} ARBITRAGE OPPORTUNITIES:")
        print("=" * 50)
        
        for i, opp in enumerate(opportunities, 1):
            print(f"\n{i}. {opp.card_name} - Score: {opp.total_score}/100")
            print(f"   💰 Profit: ${opp.profit_potential:,.0f}")
            print(f"   🎯 Confidence: {opp.confidence_score}/100")
            print(f"   ⚠️ Risk: {opp.risk_score}/100")
            if opp.image_url:
                print(f"   📸 Image: Available")
            print(f"   🔗 {opp.listing_url[:50]}...")
            
        print(f"\n🎉 Ready to implement /pending command with image support!")
        
    else:
        print("❌ No opportunities found matching criteria")
        
    return opportunities

if __name__ == "__main__":
    main()
