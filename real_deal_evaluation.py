#!/usr/bin/env python3
"""Real Deal Evaluation - Test actual eBay listings against our price database"""

from ebay_public_search import EbayPublicSearch
from quick_price import get_card_market_price

print("🎯 Real Deal Evaluation")
print("=" * 40)

# Search for high-value cards
searcher = EbayPublicSearch()
results = searcher.search_pokemon_cards('Charizard Base Set', min_price=250.0, max_price=1000.0, limit=10)

print(f"Evaluating {len(results)} listings...")
print()

viable_deals = []

for item in results:
    listing_price = item.get('price', 0)
    title = item.get('title', '')
    
    # Get our price estimates
    raw_price, raw_confidence = get_card_market_price("Charizard", "Base Set", "raw")
    psa10_price, psa10_confidence = get_card_market_price("Charizard", "Base Set", "PSA 10")
    
    if not psa10_price:
        continue
        
    # Calculate deal metrics
    grading_cost = 25.0
    total_cost = listing_price + grading_cost
    potential_profit = psa10_price - total_cost
    roi = (potential_profit / total_cost) * 100 if total_cost > 0 else 0
    
    print(f"📊 {title[:40]}...")
    print(f"   Listing: ${listing_price:.2f}")
    print(f"   Our Raw Est: ${raw_price:.2f} ({raw_confidence:.1%})")
    print(f"   PSA 10 Est: ${psa10_price:.2f} ({psa10_confidence:.1%})")
    print(f"   Total Cost: ${total_cost:.2f} (incl. grading)")
    print(f"   Profit: ${potential_profit:.2f}")
    print(f"   ROI: {roi:.1f}%")
    
    # Check if this is a viable deal
    if potential_profit > 1000 and roi > 35:
        print("   🎯 VIABLE DEAL!")
        viable_deals.append({
            'title': title,
            'listing_price': listing_price,
            'potential_profit': potential_profit,
            'roi': roi
        })
    elif listing_price < raw_price * 0.8:
        print("   💎 Below market value!")
    else:
        print("   ❌ Not profitable")
    print()

print("=" * 40)
print(f"🎉 Found {len(viable_deals)} viable deals out of {len(results)} listings")

if viable_deals:
    print("\n🚀 Best deals:")
    for deal in sorted(viable_deals, key=lambda x: x['potential_profit'], reverse=True):
        print(f"💰 ${deal['potential_profit']:.2f} profit ({deal['roi']:.1f}% ROI)")
        print(f"   {deal['title'][:50]}...")
        print()
