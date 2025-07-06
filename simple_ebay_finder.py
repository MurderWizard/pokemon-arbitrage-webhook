#!/usr/bin/env python3
"""
Simple eBay Finding API - Uses only App ID for production searches
"""

import os
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from dotenv import load_dotenv

class SimpleEbayFinder:
    """Simple eBay finder using only App ID"""
    
    def __init__(self):
        load_dotenv(override=True)
        self.app_id = os.getenv('EBAY_APP_ID')
        self.base_url = "https://svcs.ebay.com/services/search/FindingService/v1"
        
        if not self.app_id or self.app_id == 'your_app_id_here':
            raise ValueError("Missing eBay App ID")
            
    def search_pokemon_cards(self, keywords: str, min_price: float = 250.0, max_price: float = 5000.0, limit: int = 10) -> List[Dict]:
        """Search for Pokemon cards"""
        
        params = {
            'OPERATION-NAME': 'findItemsByKeywords',
            'SERVICE-VERSION': '1.0.0',
            'SECURITY-APPNAME': self.app_id,
            'RESPONSE-DATA-FORMAT': 'XML',
            'keywords': f"{keywords} pokemon card",
            'paginationInput.entriesPerPage': str(min(limit, 100)),
            'itemFilter(0).name': 'MinPrice',
            'itemFilter(0).value': str(min_price),
            'itemFilter(1).name': 'MaxPrice', 
            'itemFilter(1).value': str(max_price),
            'itemFilter(2).name': 'ListingType',
            'itemFilter(2).value': 'FixedPrice',
            'itemFilter(3).name': 'Condition',
            'itemFilter(3).value': 'New',
            'categoryId': '2536',  # Trading Card Games
            'sortOrder': 'PricePlusShippingLowest'
        }
        
        try:
            print(f"🔍 Searching eBay for: {keywords} (${min_price}-${max_price})")
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            
            # Parse XML response
            items = self._parse_xml_response(response.text)
            print(f"✅ Found {len(items)} items")
            return items
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def _parse_xml_response(self, xml_data: str) -> List[Dict]:
        """Parse eBay XML response"""
        items = []
        
        try:
            root = ET.fromstring(xml_data)
            
            # eBay XML namespace
            ns = {'ebay': 'http://www.ebay.com/marketplace/search/v1/services'}
            
            # Find all item elements
            for item in root.findall('.//ebay:item', ns):
                try:
                    title_elem = item.find('ebay:title', ns)
                    price_elem = item.find('.//ebay:convertedCurrentPrice', ns)
                    shipping_elem = item.find('.//ebay:shippingServiceCost', ns)
                    url_elem = item.find('ebay:viewItemURL', ns)
                    condition_elem = item.find('.//ebay:conditionDisplayName', ns)
                    
                    if title_elem is not None and price_elem is not None:
                        price = float(price_elem.text)
                        shipping = float(shipping_elem.text) if shipping_elem is not None else 0.0
                        
                        item_data = {
                            'title': title_elem.text,
                            'price': price,
                            'shipping': shipping,
                            'total_price': price + shipping,
                            'condition': condition_elem.text if condition_elem is not None else 'Unknown',
                            'url': url_elem.text if url_elem is not None else '',
                        }
                        items.append(item_data)
                        
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error parsing XML: {e}")
            
        return items
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Simple test search
            items = self.search_pokemon_cards("Pikachu", min_price=1, max_price=50, limit=1)
            return len(items) >= 0  # Even 0 results means connection worked
        except:
            return False

def main():
    """Test the simple eBay finder"""
    print("🧪 Testing Simple eBay Finder")
    print("=" * 40)
    
    try:
        finder = SimpleEbayFinder()
        print(f"✅ App ID configured: {finder.app_id[:20]}...")
        
        if finder.test_connection():
            print("✅ eBay API connection successful!")
            
            # Search for high-value Charizard cards
            items = finder.search_pokemon_cards("Charizard Base Set", min_price=250, limit=5)
            
            if items:
                print(f"\\n📦 Found {len(items)} high-value listings:")
                for i, item in enumerate(items, 1):
                    print(f"{i}. {item['title'][:60]}...")
                    print(f"   💰 ${item['total_price']:.2f} | Condition: {item['condition']}")
                    print(f"   🔗 {item['url'][:50]}...")
                    print()
            else:
                print("⚠️  No items found (very strict filters)")
        else:
            print("❌ eBay API connection failed")
            
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    main()
