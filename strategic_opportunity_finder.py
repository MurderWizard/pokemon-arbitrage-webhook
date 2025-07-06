#!/usr/bin/env python3
"""
Strategic Opportunity Finder
Focus on highest ROI cards instead of searching everything
"""
import asyncio
import json
from ebay_public_search import EbayPublicSearch
from quick_price import get_card_market_price
from deal_logger import DealLogger
from command_approval_bot import send_command_deal_alert

class StrategicOpportunityFinder:
    """Smart deal finder focusing on highest opportunity cards"""
    
    def __init__(self):
        self.searcher = EbayPublicSearch()
        self.deal_logger = DealLogger()
        
    def get_priority_targets(self):
        """Get prioritized list of highest opportunity cards"""
        
        # Load our strategic targets from price catalog
        try:
            with open('base_price_catalog.json', 'r') as f:
                catalog = json.load(f)
            
            targets = []
            
            # Extract chase cards (highest value)
            chase_cards = catalog.get('price_tiers', {}).get('chase_cards', {}).get('cards', {})
            
            for card_name, card_data in chase_cards.items():
                for set_name, base_price in card_data.get('sets', {}).items():
                    if base_price > 150:  # Focus on high-value cards
                        targets.append({
                            'card_name': card_name.split('(')[0].strip(),
                            'set_name': set_name,
                            'base_price': base_price,
                            'priority': card_data.get('priority', 'medium'),
                            'search_term': f"{card_name.split('(')[0].strip()} {set_name}"
                        })
            
            # Sort by potential (highest first)
            targets.sort(key=lambda x: x['base_price'], reverse=True)
            
            return targets[:8]  # Top 8 opportunities
            
        except Exception as e:
            print(f"⚠️ Could not load catalog: {e}")
            # Fallback to proven winners
            return [
                {'card_name': 'Charizard', 'set_name': 'Base Set', 'search_term': 'Charizard Base Set', 'priority': 'critical'},
                {'card_name': 'Blastoise', 'set_name': 'Base Set', 'search_term': 'Blastoise Base Set', 'priority': 'high'},
                {'card_name': 'Venusaur', 'set_name': 'Base Set', 'search_term': 'Venusaur Base Set', 'priority': 'high'},
                {'card_name': 'Charizard', 'set_name': 'Team Rocket', 'search_term': 'Dark Charizard Team Rocket', 'priority': 'high'}
            ]
    
    async def find_best_opportunity(self):
        """Find the single best deal available right now"""
        
        print("🎯 STRATEGIC OPPORTUNITY FINDER")
        print("=" * 50)
        print("🧠 Smart Strategy: Focus on highest ROI cards only")
        print()
        
        targets = self.get_priority_targets()
        
        print("📋 TARGET CARDS (Priority Order):")
        for i, target in enumerate(targets, 1):
            priority_icon = "🔥" if target.get('priority') == 'critical' else "⭐"
            base = target.get('base_price', 0)
            print(f"   {i}. {priority_icon} {target['search_term']} (${base:.0f}+)")
        print()
        
        best_deal = None
        best_roi = 0
        deals_analyzed = 0
        
        for target in targets:
            print(f"🔍 Analyzing: {target['search_term']}")
            
            # Search eBay for this specific card
            results = self.searcher.search_pokemon_cards(
                target['search_term'], 
                min_price=200.0, 
                max_price=1500.0, 
                limit=5
            )
            
            if not results:
                print(f"   ❌ No listings found")
                continue
            
            for item in results:
                deals_analyzed += 1
                listing_price = item.get('price', 0)
                title = item.get('title', '')
                url = item.get('url', '')
                
                # Get price estimates
                card_name = target['card_name']
                set_name = target['set_name']
                
                raw_price, raw_confidence = get_card_market_price(card_name, set_name, "raw")
                psa10_price, psa10_confidence = get_card_market_price(card_name, set_name, "PSA 10")
                
                if not psa10_price:
                    continue
                
                # Calculate comprehensive deal metrics
                grading_cost = 25.0
                total_cost = listing_price + grading_cost
                potential_profit = psa10_price - total_cost
                roi = (potential_profit / total_cost) * 100 if total_cost > 0 else 0
                
                # Enhanced criteria for best opportunity
                is_excellent = (
                    potential_profit > 250 and  # Minimum $250 profit (lowered for testing)
                    roi > 50 and  # 50% return minimum (lowered for testing)
                    listing_price >= 100 and  # Minimum investment (lowered for testing)
                    listing_price <= 1200 and  # Maximum single risk
                    raw_confidence > 0.7  # Good confidence (lowered for testing)
                )\n                \n                print(f\"   💰 ${listing_price:.0f} → ${psa10_price:.0f} = ${potential_profit:.0f} ({roi:.0f}% ROI)\")\n                \n                if is_excellent and roi > best_roi:\n                    best_deal = {\n                        'card_name': card_name,\n                        'set_name': set_name,\n                        'raw_price': listing_price,\n                        'estimated_psa10_price': psa10_price,\n                        'potential_profit': potential_profit,\n                        'profit_margin': roi,\n                        'condition_notes': title[:80],\n                        'listing_url': url,\n                        'total_cost': total_cost,\n                        'grading_cost': grading_cost,\n                        'confidence': raw_confidence,\n                        'priority': target.get('priority', 'medium')\n                    }\n                    best_roi = roi\n                    print(f\"   🎯 NEW BEST OPPORTUNITY! {roi:.0f}% ROI\")\n                elif is_excellent:\n                    print(f\"   ✅ Excellent deal ({roi:.0f}% ROI)\")\n                else:\n                    print(f\"   ❌ Below criteria\")\n                \n            print()\n        \n        # Results\n        print(\"=\" * 50)\n        print(f\"📊 ANALYSIS COMPLETE:\")\n        print(f\"   🔍 {len(targets)} priority cards searched\")\n        print(f\"   📋 {deals_analyzed} listings analyzed\")\n        \n        if best_deal:\n            print(f\"\\n🏆 BEST OPPORTUNITY FOUND:\")\n            print(f\"   🎴 {best_deal['card_name']} ({best_deal['set_name']})\")\n            print(f\"   💰 ${best_deal['raw_price']:.0f} → ${best_deal['estimated_psa10_price']:.0f}\")\n            print(f\"   🎯 ${best_deal['potential_profit']:.0f} profit ({best_deal['profit_margin']:.0f}% ROI)\")\n            print(f\"   🔒 {best_deal['priority'].upper()} priority card\")\n            print(f\"   📊 {best_deal['confidence']:.1%} confidence\")\n            \n            # Log and alert the best deal\n            deal_id = self.deal_logger.log_deal(best_deal)\n            await send_command_deal_alert(best_deal, str(deal_id))\n            \n            print(f\"\\n📱 DEAL ALERTED: #{deal_id}\")\n            print(f\"   ⚡ Check Telegram for approval\")\n            print(f\"   💸 This could make ${best_deal['potential_profit']:.0f} profit!\")\n            \n            return best_deal\n        else:\n            print(f\"\\n❌ NO QUALIFYING OPPORTUNITIES\")\n            print(f\"   💡 Try again later or lower criteria\")\n            return None\n\nasync def main():\n    \"\"\"Run strategic opportunity finder\"\"\"\n    finder = StrategicOpportunityFinder()\n    await finder.find_best_opportunity()\n\nif __name__ == \"__main__\":\n    asyncio.run(main())
