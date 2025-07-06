#!/usr/bin/env python3
"""
eBay Browse API Implementation - Modern search API
Requires OAuth token for authentication
"""

import os
import requests
import base64
from typing import List, Dict, Optional
from dotenv import load_dotenv

class EbayBrowseAPI:
    """eBay Browse API client with OAuth authentication"""
    
    def __init__(self):
        load_dotenv(override=True)
        self.app_id = os.getenv('EBAY_APP_ID')
        self.cert_id = os.getenv('EBAY_CERT_ID')  # For OAuth
        
        if not self.app_id:
            raise ValueError("Missing eBay App ID")
            
        self.base_url = "https://api.ebay.com"
        self.oauth_token = None
        
    def get_oauth_token(self) -> str:
        """Get OAuth token for API access"""
        if self.oauth_token:
            return self.oauth_token
            
        # Create credentials for OAuth
        credentials = f"{self.app_id}:{self.cert_id}" if self.cert_id else self.app_id
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        oauth_url = f"{self.base_url}/identity/v1/oauth2/token"
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
        
        try:
            response = requests.post(oauth_url, headers=headers, data=data, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                self.oauth_token = token_data.get('access_token')
                return self.oauth_token
            else:
                print(f"OAuth error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"OAuth request failed: {e}")
            return None
    
    def search_items(self, query: str, min_price: float = 250.0, max_price: float = 5000.0, limit: int = 10) -> List[Dict]:
        """Search for items using Browse API"""
        
        token = self.get_oauth_token()
        if not token:
            print("❌ Cannot get OAuth token")
            return []
            
        url = f"{self.base_url}/buy/browse/v1/item_summary/search"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
            'Accept': 'application/json'
        }
        
        # Build query parameters
        params = {
            'q': f"{query} pokemon card",
            'filter': f'price:[{min_price}..{max_price}],buyingOptions:{{FIXED_PRICE}},conditions:{{NEW,LIKE_NEW,EXCELLENT,VERY_GOOD,GOOD}}',
            'sort': 'price',
            'limit': str(min(limit, 50)),  # API limit is 50 per request
            'category_ids': '2536'  # Trading Card Games category
        }
        
        try:
            print(f"🔍 Searching eBay Browse API: {query} (${min_price}-${max_price})")
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('itemSummaries', [])
                
                formatted_items = []
                for item in items:
                    try:
                        price_info = item.get('price', {})
                        shipping_info = item.get('shippingOptions', [{}])[0]
                        
                        # Extract price
                        price_value = float(price_info.get('value', 0))
                        shipping_cost = 0.0
                        
                        if shipping_info.get('shippingCost'):
                            shipping_cost = float(shipping_info['shippingCost'].get('value', 0))
                        
                        formatted_item = {
                            'title': item.get('title', ''),
                            'price': price_value,
                            'shipping': shipping_cost,
                            'total_price': price_value + shipping_cost,
                            'condition': item.get('condition', 'Unknown'),
                            'url': item.get('itemWebUrl', ''),
                            'item_id': item.get('itemId', ''),
                            'seller': {
                                'username': item.get('seller', {}).get('username', ''),
                                'feedback_score': item.get('seller', {}).get('feedbackScore', 0)
                            },
                            'location': item.get('itemLocation', {}).get('country', ''),
                            'image_url': item.get('image', {}).get('imageUrl', '')
                        }
                        
                        formatted_items.append(formatted_item)
                        
                    except Exception as e:
                        print(f"Error parsing item: {e}")
                        continue
                
                print(f"✅ Found {len(formatted_items)} items")
                return formatted_items
                
            elif response.status_code == 401:
                print("❌ Authentication failed - token may be invalid")
                return []
            elif response.status_code == 429:
                print("❌ Rate limit exceeded - try again later")
                return []
            else:
                print(f"❌ API error: {response.status_code} - {response.text[:200]}")
                return []
                
        except Exception as e:
            print(f"❌ Search request failed: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test API connection"""
        token = self.get_oauth_token()
        return token is not None

def main():
    """Test the Browse API"""
    print("🧪 Testing eBay Browse API")
    print("=" * 40)
    
    try:
        api = EbayBrowseAPI()
        
        if api.test_connection():
            print("✅ OAuth authentication successful!")
            
            # Test search
            items = api.search_items("Charizard Base Set", min_price=250, limit=3)
            
            if items:
                print(f"\n📦 Found {len(items)} items:")
                for i, item in enumerate(items, 1):
                    print(f"{i}. {item['title'][:60]}...")
                    print(f"   💰 ${item['total_price']:.2f} | Condition: {item['condition']}")
                    print(f"   👤 Seller: {item['seller']['username']} | 📍 {item['location']}")
                    print()
            else:
                print("⚠️  No items found")
        else:
            print("❌ Authentication failed")
            print("📋 Make sure you have EBAY_APP_ID and EBAY_CERT_ID in .env")
            
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    main()
