#!/usr/bin/env python3
"""Live Deal Finder - Find and alert on real deals"""

import asyncio
from ebay_public_search import EbayPublicSearch
from quick_price import get_card_market_price
from deal_logger import DealLogger
from mvp_telegram_bot import send_mvp_deal_alert, send_mvp_summary
import os
from dotenv import load_dotenv

async def find_and_alert_deals():
    """Find real deals and send alerts"""
    load_dotenv()
    
    deal_logger = DealLogger()
    
    print("🎯 Live Deal Finder - Scanning eBay...")
    print("=" * 50)
    
    searcher = EbayPublicSearch()
    
    # Search terms for high-value cards
    search_terms = [
        'Charizard Base Set',
        'Blastoise Base Set', 
        'Venusaur Base Set',
        'Pikachu Illustrator',
        'Charizard VMAX'
    ]
    
    total_deals = 0
    total_potential_profit = 0
    
    for search_term in search_terms:
        print(f"\n🔍 Searching: {search_term}")
        
        # Parse card info
        parts = search_term.split()
        card_name = parts[0]
        set_name = ' '.join(parts[1:]) if len(parts) > 1 else "Base Set"
        
        results = searcher.search_pokemon_cards(search_term, min_price=250.0, max_price=2000.0, limit=10)
        
        for item in results:
            listing_price = item.get('price', 0)
            title = item.get('title', '')
            url = item.get('url', '')
            
            # Get price estimates
            raw_price, raw_confidence = get_card_market_price(card_name, set_name, "raw")
            psa10_price, psa10_confidence = get_card_market_price(card_name, set_name, "PSA 10")
            
            if not psa10_price:
                continue
                
            # Calculate deal metrics
            grading_cost = 25.0
            total_cost = listing_price + grading_cost
            potential_profit = psa10_price - total_cost
            roi = (potential_profit / total_cost) * 100 if total_cost > 0 else 0
            
            # Check if viable (conservative thresholds for MVP)
            if potential_profit > 1000 and roi > 50 and listing_price >= 250:
                
                deal = {
                    'card_name': card_name,
                    'set_name': set_name,
                    'raw_price': listing_price,
                    'estimated_psa10_price': psa10_price,
                    'potential_profit': potential_profit,
                    'profit_margin': roi,
                    'condition_notes': f"Listed condition from: {title[:60]}",
                    'listing_url': url,
                    'total_cost': total_cost,
                    'grading_cost': grading_cost
                }
                
                # Log the deal
                deal_id = deal_logger.log_deal(deal)
                
                # Send MVP alert
                await send_mvp_deal_alert(deal, str(deal_id))
                
                print(f"✅ DEAL FOUND & ALERTED: Deal #{deal_id}")
                print(f"   💰 ${potential_profit:.2f} profit ({roi:.1f}% ROI)")
                print(f"   📦 {title[:40]}...")
                
                total_deals += 1
                total_potential_profit += potential_profit
            else:
                print(f"   ❌ {title[:30]}... - Not profitable enough")
    
    # Send session summary
    if total_deals > 0:
        await send_mvp_summary(total_deals, total_potential_profit)
    
    print(f"\n🎉 Session Complete: {total_deals} deals found and alerted!")
    print(f"💰 Total potential profit: ${total_potential_profit:.2f}")
    return total_deals

if __name__ == "__main__":
    asyncio.run(find_and_alert_deals())
