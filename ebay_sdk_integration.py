#!/usr/bin/env python3
"""
eBay SDK Integration - Official eBay Python SDK
FREE API access for searching listings!
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv
from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError

# Get the directory containing this file
current_dir = Path(__file__).parent.absolute()

# Load the .env file from the same directory
dotenv_path = current_dir / '.env'
load_dotenv(dotenv_path=dotenv_path)

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add a console handler if none exists
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Log environment setup
logger.debug("Environment setup:")
logger.debug(f"Current directory: {current_dir}")
logger.debug(f".env path: {dotenv_path}")
logger.debug(f"APP_ID: {os.getenv('EBAY_APP_ID')}")
logger.debug(f"Environment: {os.getenv('EBAY_ENVIRONMENT')}")

class EbaySDK:
    """Official eBay SDK for searching listings"""
    
    def __init__(self):
        load_dotenv()  # Ensure environment is loaded
        
        # Load credentials
        self.app_id = os.getenv('EBAY_APP_ID')
        self.dev_id = os.getenv('EBAY_DEV_ID')  # Optional for Finding API
        self.cert_id = os.getenv('EBAY_CERT_ID')  # Optional for Finding API
        self.environment = os.getenv('EBAY_ENVIRONMENT', 'production')
        
        # For Finding API, we only need the App ID
        if not self.app_id or self.app_id == 'your_app_id_here':
            raise ValueError("Missing required eBay App ID")
            
        # Set up API configuration - Finding API only needs App ID
        config = {
            'domain': 'svcs.sandbox.ebay.com' if self.environment == 'sandbox' else 'svcs.ebay.com',
            'appid': self.app_id,
            'version': '1.13.0'
        }
        
        # Add optional credentials if available (for future Trading API support)
        if self.dev_id:
            config['devid'] = self.dev_id
        if self.cert_id:
            config['certid'] = self.cert_id
        
        # Initialize the Finding API connection
        self.finding_api = Finding(
            debug=True,  # Enable debug mode to see API requests/responses
            config_file=None,
            **config
        )
        
        logger.info(f"Initialized eBay SDK in {self.environment} mode")
        logger.debug(f"Using domain: {config['domain']}")
    
    def search_pokemon_cards(self, keywords: str, max_price: Optional[float] = None, 
                         min_price: Optional[float] = None, raw_only: bool = True, 
                         limit: int = 50) -> List[Dict]:
        """
        Search for Pokemon cards on eBay
        
        Args:
            keywords: Search terms (e.g., "Charizard VMAX")
            max_price: Maximum price filter
            min_price: Minimum price filter (e.g., 250 for high-value cards)
            raw_only: Only return raw (ungraded) cards
            limit: Max results to return
            
        Returns:
            List of matching items with price, title, URL, etc.
        """
        try:
            # Build search filters
            item_filters = [
                {
                    'name': 'CategoryId',
                    'value': '2536'  # Trading Card Games category
                },
                {
                    'name': 'ListingType',
                    'value': 'FixedPrice'  # Buy It Now listings only
                }
            ]
            
            if max_price:
                item_filters.append({
                    'name': 'MaxPrice',
                    'value': str(max_price),
                    'paramName': 'Currency',
                    'paramValue': 'USD'
                })
                
            if min_price:
                item_filters.append({
                    'name': 'MinPrice',
                    'value': str(min_price),
                    'paramName': 'Currency',
                    'paramValue': 'USD'
                })

            # Base search
            response = self.finding_api.execute('findItemsByKeywords', {
                'keywords': keywords,
                'itemFilter': item_filters,
                'outputSelector': ['SellerInfo', 'StoreInfo', 'UnitPriceInfo'],
                'paginationInput': {
                    'entriesPerPage': limit,
                    'pageNumber': 1
                }
            }).response.dict()

            if 'searchResult' not in response:
                return []

            items = response['searchResult'].get('item', [])
            
            # Post-process results
            processed_items = []
            for item in items:
                try:
                    # Convert price to float
                    price = float(item['sellingStatus']['currentPrice']['value'])
                    
                    # Skip graded cards if raw_only is True
                    if raw_only:
                        title = item['title'].upper()
                        if any(x in title for x in ['PSA', 'BGS', 'CGC', 'GRADED']):
                            continue
                    
                    # Extract key fields with safe gets
                    processed_item = {
                        'id': str(item.get('itemId', '')),
                        'title': str(item.get('title', '')),
                        'price': price,
                        'url': str(item.get('viewItemURL', '')),
                        'condition': str(item.get('condition', {}).get('conditionDisplayName', 'Not Specified')),
                        'seller': str(item.get('sellerInfo', {}).get('sellerUserName', 'Unknown')),
                        'seller_feedback': float(item.get('sellerInfo', {}).get('positiveFeedbackPercent', '0')),
                        'shipping_cost': float(item.get('shippingInfo', {}).get('shippingServiceCost', [{'value': '0.0'}])[0]['value']),
                        'buy_it_now': True,  # We filtered for fixed price listings
                        'listing_time': str(item.get('listingInfo', {}).get('startTime', '')),
                        'watching': int(item.get('listingInfo', {}).get('watchCount', '0')),
                        'raw': True  # Since we filtered out graded cards
                    }
                    processed_items.append(processed_item)
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Error processing item: {e}")
                    continue
            
            return processed_items

        except Exception as e:
            logger.error(f"eBay API error: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test if eBay API is working"""
        try:
            # Simple test search
            response = self.finding_api.execute('findItemsAdvanced', {
                'keywords': 'pokemon',
                'paginationInput': {
                    'entriesPerPage': 1,
                    'pageNumber': 1
                }
            })
            
            if hasattr(response.reply, 'searchResult'):
                logger.info("✅ eBay API connection successful!")
                return True
            else:
                logger.error("❌ eBay API connection failed - no results")
                return False
                
        except Exception as e:
            logger.error(f"❌ eBay API test failed: {e}")
            return False
        
    def is_psa_eligible(self, item_id: str) -> bool:
        """Check if an item is eligible for PSA grading through eBay"""
        try:
            # Get item details
            item = self.get_item_details(item_id)
            if not item:
                return False
            
            # Check eligibility criteria:
            # 1. Raw card (no grading company in title)
            title = item['title'].upper()
            if any(x in title for x in ['PSA', 'BGS', 'CGC', 'GRADED']):
                return False
            
            # 2. Price > $250 (high-value focus for MVP)
            price = float(item['price'])
            if price < 250:
                return False
                
            # 3. Condition check (should be NM or better)
            condition = item.get('condition', '').upper()
            good_conditions = ['NEAR MINT', 'MINT', 'NM', 'NM/M', 'MINT/NM']
            if not any(cond in condition for cond in good_conditions):
                return False
            
            # 4. Seller requirements
            seller_feedback = int(item.get('seller_feedback', 0))
            if seller_feedback < 98:  # 98% positive feedback minimum
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking PSA eligibility: {e}")
            return False
            
    def add_to_cart_with_grading(
        self,
        item_id: str, 
        grading_tier: str = 'BASIC',
        auto_vault: bool = True
    ) -> Dict:
        """
        Add item to cart with PSA grading and vault options
        
        Args:
            item_id: eBay item ID
            grading_tier: 'BASIC' ($25) or 'FAST' ($50)
            auto_vault: Whether to automatically vault after grading
            
        Returns:
            Dict with order details
        """
        try:
            # 1. Verify item is eligible for PSA grading
            if not self.is_psa_eligible(item_id):
                raise ValueError(f"Item {item_id} is not eligible for PSA grading")
            
            # 2. Add to cart with grading option
            cart_request = {
                'Item': {
                    'ItemID': item_id,
                    'Quantity': 1
                },
                'GradingService': {
                    'Provider': 'PSA',
                    'Tier': grading_tier.upper()
                }
            }
            
            if auto_vault:
                cart_request['GradingService']['VaultAfterGrading'] = True
            
            # Use Trading API to add to cart (placeholder - actual API call would go here)
            # This is a mock response for now since eBay's API doesn't directly support this yet
            cart_response = {
                'OrderID': f'PSA-{item_id}',
                'Status': 'Added to cart with grading',
                'GradingDetails': {
                    'Provider': 'PSA',
                    'Tier': grading_tier,
                    'EstimatedCost': 25 if grading_tier == 'BASIC' else 50
                },
                'VaultDetails': {
                    'Enabled': auto_vault,
                    'EstimatedFee': 0  # Free for PSA graded cards
                }
            }
            
            return cart_response
            
        except Exception as e:
            logger.error(f"Error adding item to cart with grading: {e}")
            return {'error': str(e)}
            
    def track_grading_status(self, order_id: str) -> Dict:
        """
        Track PSA grading status for an order
        
        Args:
            order_id: The order ID from add_to_cart_with_grading
            
        Returns:
            Dict with current status
        """
        try:
            # This is a mock implementation since eBay doesn't expose PSA's API directly
            # In production, we'd need to either:
            # 1. Use eBay's API to check order status (once they add grading support)
            # 2. Integrate directly with PSA's API
            # 3. Scrape PSA's website with the submission number
            
            status = {
                'OrderID': order_id,
                'Status': 'In Progress',
                'Stage': 'Grading',
                'EstimatedCompletion': '2-3 weeks',
                'TrackingNumber': f'PSA-{order_id}',
                'Updates': [
                    {'timestamp': '2024-02-14T10:00:00Z', 'status': 'Order Received'},
                    {'timestamp': '2024-02-14T14:30:00Z', 'status': 'In Grading Queue'}
                ]
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error tracking grading status: {e}")
            return {'error': str(e)}
            
    def get_item_details(self, item_id: str) -> Optional[Dict]:
        """Get detailed information about an eBay item"""
        try:
            # Use Shopping API to get detailed item info
            response = self.finding_api.execute('GetSingleItem', {
                'ItemID': item_id,
                'IncludeSelector': 'Details,Description,ItemSpecifics'
            }).response.dict()
            
            if 'Item' not in response:
                return None
                
            item = response['Item']
            
            try:
                price_info = item.get('CurrentPrice', {})
                current_price = float(price_info['Value']) if isinstance(price_info, dict) else 0.0
            except (KeyError, ValueError, TypeError):
                current_price = 0.0
                
            try:
                seller_info = item.get('Seller', {})
                seller_feedback = float(seller_info.get('PositiveFeedbackPercent', 0))
            except (ValueError, TypeError):
                seller_feedback = 0.0
                
            details = {
                'id': str(item.get('ItemID', '')),
                'title': str(item.get('Title', '')),
                'price': current_price,
                'condition': str(item.get('ConditionDisplayName', '')),
                'seller': str(item.get('Seller', {}).get('UserID', '')),
                'seller_feedback': seller_feedback,
                'description': str(item.get('Description', '')),
                'specifics': item.get('ItemSpecifics', {}).get('NameValueList', [])
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting item details: {e}")
            return None
