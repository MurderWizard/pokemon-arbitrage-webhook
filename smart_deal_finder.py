#!/usr/bin/env python3
"""
Smart Deal Finder - Single deal focus with enhanced metrics
"""
import asyncio
import sqlite3
from ebay_public_search import EbayPublicSearch
from quick_price import get_card_market_price
from deal_logger import DealLogger
from enhanced_mvp_bot import send_enhanced_deal_alert, check_capital_management

async def smart_deal_finder():
    """Smart deal finder with capital management"""
    
    print("🎯 Smart Deal Finder - Single Deal Focus")
    print("=" * 50)
    
    deal_logger = DealLogger()
    searcher = EbayPublicSearch()
    
    # Check current active deals
    active_deals = get_active_deals_count()
    
    if active_deals > 0:
        print(f"⚠️  Capital Management: {active_deals} active deal(s)")
        print("   Scanning for opportunities but won't approve new deals")
        print("   until current investment completes.")
        await check_capital_management(active_deals, get_total_exposure())
        approval_mode = False
    else:
        print("✅ No active deals - Ready to approve new opportunities")
        approval_mode = True
    
    # High-value search terms (focus on proven cards)
    search_terms = [
        'Charizard Base Set',
        'Blastoise Base Set', 
        'Venusaur Base Set'
    ]
    
    deals_found = 0
    total_potential = 0
    
    for search_term in search_terms:
        print(f"\n🔍 Searching: {search_term}")
        
        # Parse card info
        parts = search_term.split()
        card_name = parts[0]
        set_name = ' '.join(parts[1:])
        
        results = searcher.search_pokemon_cards(search_term, min_price=250.0, max_price=1500.0, limit=8)
        
        for item in results:
            listing_price = item.get('price', 0)
            title = item.get('title', '')
            url = item.get('url', '')
            
            # Get price estimates
            raw_price, raw_confidence = get_card_market_price(card_name, set_name, "raw")
            psa10_price, psa10_confidence = get_card_market_price(card_name, set_name, "PSA 10")
            
            if not psa10_price:
                continue
                
            # Calculate deal metrics with enhanced criteria
            grading_cost = 25.0
            total_cost = listing_price + grading_cost
            potential_profit = psa10_price - total_cost
            roi = (potential_profit / total_cost) * 100 if total_cost > 0 else 0
            
            # Enhanced criteria for single deal focus
            is_viable = (
                potential_profit > 500 and  # More realistic minimum for $1k bankroll
                roi > 300 and  # 3x minimum return
                listing_price >= 250 and  # Minimum investment
                listing_price <= 500 and  # Maximum risk per deal (50% of bankroll)
                raw_confidence > 0.85  # High confidence only
            )
            
            if is_viable:
                deal = {
                    'card_name': card_name,
                    'set_name': set_name,
                    'raw_price': listing_price,
                    'estimated_psa10_price': psa10_price,
                    'potential_profit': potential_profit,
                    'profit_margin': roi,
                    'condition_notes': title[:80],
                    'listing_url': url,
                    'total_cost': total_cost,
                    'grading_cost': grading_cost
                }
                
                # Always log the deal
                deal_id = deal_logger.log_deal(deal)
                
                if approval_mode:
                    # Send enhanced alert for approval
                    await send_enhanced_deal_alert(deal, str(deal_id))
                    print(f"✅ DEAL ALERTED: Deal #{deal_id}")
                    print(f"   💰 ${potential_profit:.0f} profit ({roi:.0f}% ROI)")
                    print(f"   🎯 Single deal focus - awaiting approval")
                    
                    # Only alert one deal at a time for single deal strategy
                    deals_found += 1
                    total_potential += potential_profit
                    break  # Stop after first viable deal
                else:
                    # Just log for future reference
                    print(f"📝 LOGGED: Deal #{deal_id} (${potential_profit:.0f} profit)")
                    print(f"   ⏳ Will alert when current deal completes")
                    deals_found += 1
                    total_potential += potential_profit
            else:
                print(f"   ❌ {title[:30]}... - Below enhanced criteria")
        
        if deals_found > 0 and approval_mode:
            break  # Single deal focus - stop after finding one
    
    # Summary
    print(f"\n🎉 Session Complete:")
    if approval_mode:
        print(f"   🎯 {deals_found} deal alerted for approval")
        print(f"   💰 ${total_potential:.0f} profit potential")
        print(f"   🔍 Single deal focus strategy")
    else:
        print(f"   📝 {deals_found} deals logged for future")
        print(f"   ⏳ Waiting for active deal completion")
        
    return deals_found

def get_active_deals_count() -> int:
    """Get count of currently active deals"""
    try:
        conn = sqlite3.connect("deals.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM deals WHERE status = 'APPROVED'")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

def get_total_exposure() -> float:
    """Get total capital exposure from active deals"""
    try:
        conn = sqlite3.connect("deals.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(raw_price) FROM deals WHERE status = 'APPROVED'")
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0.0
    except:
        return 0.0

if __name__ == "__main__":
    asyncio.run(smart_deal_finder())
