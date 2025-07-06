#!/usr/bin/env python3
"""
Profit Opportunity Analyzer
Shows the best profit opportunities instead of searching blindly
"""
import json
from quick_price import get_card_market_price

def analyze_profit_opportunities():
    """Analyze and rank the best profit opportunities"""
    
    print("💎 PROFIT OPPORTUNITY ANALYSIS")
    print("=" * 60)
    
    # Strategic target cards (proven winners)
    target_cards = [
        # Vintage powerhouses
        {"name": "Charizard", "set": "Base Set", "priority": "🔥 CRITICAL"},
        {"name": "Blastoise", "set": "Base Set", "priority": "⭐ HIGH"},
        {"name": "Venusaur", "set": "Base Set", "priority": "⭐ HIGH"},
        {"name": "Alakazam", "set": "Base Set", "priority": "📈 MEDIUM"},
        {"name": "Chansey", "set": "Base Set", "priority": "📈 MEDIUM"},
        
        # Team Rocket favorites  
        {"name": "Dark Charizard", "set": "Team Rocket", "priority": "🔥 CRITICAL"},
        {"name": "Dark Blastoise", "set": "Team Rocket", "priority": "⭐ HIGH"},
        
        # Jungle gems
        {"name": "Flareon", "set": "Jungle", "priority": "📈 MEDIUM"},
        {"name": "Jolteon", "set": "Jungle", "priority": "📈 MEDIUM"},
        {"name": "Vaporeon", "set": "Jungle", "priority": "📈 MEDIUM"},
        
        # Fossil finds
        {"name": "Lapras", "set": "Fossil", "priority": "📈 MEDIUM"},
        {"name": "Ditto", "set": "Fossil", "priority": "📈 MEDIUM"},
        
        # Neo series
        {"name": "Lugia", "set": "Neo Genesis", "priority": "⭐ HIGH"},
        {"name": "Ho-oh", "set": "Neo Revelation", "priority": "⭐ HIGH"},
    ]
    
    opportunities = []
    
    print("🔍 Analyzing profit potential for strategic cards...")
    print()
    
    for card in target_cards:
        try:
            # Get pricing data
            raw_price, raw_confidence = get_card_market_price(card["name"], card["set"], "raw")
            psa10_price, psa10_confidence = get_card_market_price(card["name"], card["set"], "PSA 10")
            
            if raw_price and psa10_price and raw_price > 50:  # Only analyze valuable cards
                grading_cost = 25.0
                total_investment = raw_price + grading_cost
                potential_profit = psa10_price - total_investment
                roi_percentage = (potential_profit / total_investment) * 100
                
                opportunities.append({
                    "card": f"{card['name']} ({card['set']})",
                    "priority": card["priority"],
                    "raw_price": raw_price,
                    "psa10_price": psa10_price,
                    "potential_profit": potential_profit,
                    "roi_percentage": roi_percentage,
                    "total_investment": total_investment,
                    "confidence": (raw_confidence + psa10_confidence) / 2
                })
                
        except Exception as e:
            print(f"⚠️ Could not analyze {card['name']} ({card['set']}): {e}")
    
    # Sort by ROI percentage (best opportunities first)
    opportunities.sort(key=lambda x: x["roi_percentage"], reverse=True)
    
    # Display results
    print("🏆 TOP PROFIT OPPORTUNITIES (Ranked by ROI)")
    print("=" * 60)
    
    for i, opp in enumerate(opportunities[:10], 1):  # Top 10
        if opp["potential_profit"] > 500:  # Only show profitable opportunities
            print(f"{i:2}. {opp['priority']} {opp['card']}")
            print(f"    💰 Investment: ${opp['total_investment']:.0f} → Return: ${opp['psa10_price']:.0f}")
            print(f"    🎯 Profit: ${opp['potential_profit']:.0f} ({opp['roi_percentage']:.0f}% ROI)")
            print(f"    📊 Confidence: {opp['confidence']:.1%}")
            
            # ROI quality indicator
            if opp["roi_percentage"] > 300:
                print(f"    ✨ EXCELLENT OPPORTUNITY (3x+ return)")
            elif opp["roi_percentage"] > 200:
                print(f"    ⭐ GREAT OPPORTUNITY (2x+ return)")
            elif opp["roi_percentage"] > 100:
                print(f"    📈 GOOD OPPORTUNITY (100%+ return)")
            
            print()
    
    # Summary
    excellent = len([o for o in opportunities if o["roi_percentage"] > 300])
    great = len([o for o in opportunities if 200 <= o["roi_percentage"] <= 300])
    good = len([o for o in opportunities if 100 <= o["roi_percentage"] < 200])
    
    print("📊 OPPORTUNITY SUMMARY:")
    print(f"   ✨ {excellent} EXCELLENT opportunities (3x+ ROI)")
    print(f"   ⭐ {great} GREAT opportunities (2-3x ROI)")
    print(f"   📈 {good} GOOD opportunities (1-2x ROI)")
    print()
    print("💡 STRATEGY RECOMMENDATION:")
    if excellent > 0:
        print("   🎯 Focus search on EXCELLENT opportunities first")
        print("   💰 These offer the highest profit potential")
    elif great > 0:
        print("   🎯 Focus search on GREAT opportunities")
        print("   📈 Solid 2-3x returns available")
    else:
        print("   🔍 Expand search criteria or wait for better market conditions")
    
    return opportunities

if __name__ == "__main__":
    analyze_profit_opportunities()
