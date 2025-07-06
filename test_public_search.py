#!/usr/bin/env python3
"""Test public eBay search for live deals"""

from ebay_public_search import EbayPublicSearch

print("🔍 Testing Public eBay Search")
print("=" * 40)

searcher = EbayPublicSearch()
results = searcher.search_pokemon_cards('Charizard Base Set', min_price=250.0, max_price=1000.0, limit=5)

print(f"Found {len(results)} results:")
for i, item in enumerate(results[:3]):
    title = item.get('title', 'No title')[:50]
    price = item.get('price', 0)
    print(f"{i+1}. {title}...")
    print(f"   Price: ${price:.2f}")
    print()

if results:
    print("✅ Public search working!")
else:
    print("⚠️  No results found (might be search parsing issue)")
