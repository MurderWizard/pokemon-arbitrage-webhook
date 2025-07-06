import requests
import time
from typing import Dict, List, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class TCGPlayerAPI:
    """TCGPlayer API client for market data and pricing"""
    
    def __init__(self):
        self.base_url = "https://api.tcgplayer.com"
        self.client_id = settings.TCG_CLIENT_ID
        self.client_secret = settings.TCG_CLIENT_SECRET
        self.access_token = None
        self.token_expires_at = 0
        
    def _get_access_token(self) -> str:
        """Get or refresh access token"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
            
        url = f"{self.base_url}/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        self.token_expires_at = time.time() + token_data['expires_in'] - 60  # 60s buffer
        
        return self.access_token
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to TCGPlayer API"""
        token = self._get_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def search_products(self, query: str, category_id: int = 3) -> List[Dict]:
        """Search for Pokemon cards by name"""
        try:
            endpoint = "catalog/products"
            params = {
                'categoryId': category_id,  # 3 = Pokemon
                'productName': query,
                'limit': 50
            }
            
            result = self._make_request(endpoint, params)
            return result.get('results', [])
        except Exception as e:
            logger.error(f"Error searching TCGPlayer products: {e}")
            return []
    
    def get_product_pricing(self, product_ids: List[int]) -> Dict[int, Dict]:
        """Get pricing data for multiple products"""
        try:
            if not product_ids:
                return {}
                
            endpoint = f"pricing/product/{','.join(map(str, product_ids))}"
            result = self._make_request(endpoint)
            
            pricing_data = {}
            for item in result.get('results', []):
                product_id = item.get('productId')
                pricing_data[product_id] = {
                    'market_price': item.get('marketPrice'),
                    'low_price': item.get('lowPrice'),
                    'mid_price': item.get('midPrice'),
                    'high_price': item.get('highPrice'),
                    'direct_low': item.get('directLowPrice'),
                    'sub_type_name': item.get('subTypeName')
                }
            
            return pricing_data
        except Exception as e:
            logger.error(f"Error getting TCGPlayer pricing: {e}")
            return {}
    
    def get_buylist_pricing(self, product_ids: List[int]) -> Dict[int, Dict]:
        """Get buylist pricing for products"""
        try:
            if not product_ids:
                return {}
                
            endpoint = f"pricing/buylist/{','.join(map(str, product_ids))}"
            result = self._make_request(endpoint)
            
            buylist_data = {}
            for item in result.get('results', []):
                product_id = item.get('productId')
                buylist_data[product_id] = {
                    'market_price': item.get('marketPrice'),
                    'listed_median_price': item.get('listedMedianPrice')
                }
            
            return buylist_data
        except Exception as e:
            logger.error(f"Error getting TCGPlayer buylist pricing: {e}")
            return {}

class EbayAPI:
    """eBay API client for searching and buying"""
    
    def __init__(self):
        self.base_url = "https://api.ebay.com"
        if settings.EBAY_ENVIRONMENT == "sandbox":
            self.base_url = "https://api.sandbox.ebay.com"
        
        self.app_id = settings.EBAY_APP_ID
        self.cert_id = settings.EBAY_CERT_ID
        self.user_token = settings.EBAY_USER_TOKEN
    
    def search_items(self, keywords: str, max_price: float = None, condition: str = "1000") -> List[Dict]:
        """Search for items on eBay"""
        try:
            endpoint = "buy/browse/v1/item_summary/search"
            headers = {
                'Authorization': f'Bearer {self.user_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'q': keywords,
                'category_ids': '2536',  # Trading Card Games
                'filter': f'conditionIds:{{{condition}}}',  # 1000 = New
                'limit': 50,
                'sort': 'price'
            }
            
            if max_price:
                params['filter'] += f',price:[..{max_price}]'
            
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            return result.get('itemSummaries', [])
        except Exception as e:
            logger.error(f"Error searching eBay items: {e}")
            return []
    
    def get_item_details(self, item_id: str) -> Optional[Dict]:
        """Get detailed information about a specific item"""
        try:
            endpoint = f"buy/browse/v1/item/{item_id}"
            headers = {
                'Authorization': f'Bearer {self.user_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting eBay item details: {e}")
            return None

class PriceChartingAPI:
    """PriceCharting API client for price data"""
    
    def __init__(self):
        self.base_url = "https://www.pricecharting.com/api"
        self.api_key = settings.PRICECHARTING_API_KEY
    
    def get_price(self, product_name: str, console: str = "pokemon-cards") -> Optional[Dict]:
        """Get price data for a product"""
        try:
            endpoint = "product"
            params = {
                't': self.api_key,
                'q': product_name,
                'console': console
            }
            
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting PriceCharting data: {e}")
            return None

class COMCService:
    """COMC service for inventory management"""
    
    def __init__(self):
        self.base_url = "https://www.comc.com"
        self.username = settings.COMC_USERNAME
        self.password = settings.COMC_PASSWORD
        self.session = requests.Session()
        self._login()
    
    def _login(self):
        """Login to COMC"""
        try:
            # This would need to be implemented based on COMC's actual login process
            # For now, this is a placeholder
            pass
        except Exception as e:
            logger.error(f"Error logging into COMC: {e}")
    
    def get_inventory(self) -> List[Dict]:
        """Get current inventory from COMC"""
        try:
            # This would fetch inventory CSV and parse it
            # Placeholder implementation
            return []
        except Exception as e:
            logger.error(f"Error getting COMC inventory: {e}")
            return []
    
    def update_pricing(self, pricing_data: List[Dict]) -> bool:
        """Update pricing for COMC inventory"""
        try:
            # This would upload repricer CSV
            # Placeholder implementation
            return True
        except Exception as e:
            logger.error(f"Error updating COMC pricing: {e}")
            return False
