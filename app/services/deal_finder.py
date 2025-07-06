from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.database import Deal, Card, InventoryItem, PriceHistory
from app.models.schemas import DealCreate
from app.services.external_apis import EbayAPI, TCGPlayerAPI, PriceChartingAPI
from app.core.config import settings
import logging
import re

logger = logging.getLogger(__name__)

class DealFinder:
    """Service for finding profitable card deals"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ebay_api = EbayAPI()
        self.tcg_api = TCGPlayerAPI()
        self.pricecharting_api = PriceChartingAPI()
    
    def find_deals(self, search_terms: List[str] = None) -> List[Dict]:
        """Find deals based on search terms or popular cards"""
        if not search_terms:
            search_terms = self._get_popular_search_terms()
        
        all_deals = []
        
        for term in search_terms:
            try:
                deals = self._find_deals_for_term(term)
                all_deals.extend(deals)
            except Exception as e:
                logger.error(f"Error finding deals for term '{term}': {e}")
                continue
        
        # Sort by profit margin descending
        all_deals.sort(key=lambda x: x.get('profit_margin', 0), reverse=True)
        
        return all_deals[:50]  # Return top 50 deals
    
    def _find_deals_for_term(self, search_term: str) -> List[Dict]:
        """Find deals for a specific search term"""
        deals = []
        
        # Search eBay for items
        ebay_items = self.ebay_api.search_items(
            keywords=f"pokemon card {search_term}",
            condition="1000"  # New condition
        )
        
        for item in ebay_items:
            try:
                deal = self._evaluate_ebay_item(item)
                if deal:
                    deals.append(deal)
            except Exception as e:
                logger.error(f"Error evaluating eBay item {item.get('itemId')}: {e}")
                continue
        
        return deals
    
    def _evaluate_ebay_item(self, item: Dict) -> Optional[Dict]:
        """Evaluate if an eBay item is a good deal"""
        try:
            # Extract card information
            title = item.get('title', '').lower()
            price = float(item.get('price', {}).get('value', 0))
            
            if price == 0:
                return None
            
            # Parse card name and set from title
            card_info = self._parse_card_title(title)
            if not card_info:
                return None
            
            # Get market price from TCGPlayer
            market_price = self._get_market_price(card_info)
            if not market_price:
                return None
            
            # Calculate profit margin
            profit_margin = (market_price - price) / market_price
            
            # Check if it meets our criteria
            if (profit_margin >= settings.MIN_PROFIT_MARGIN and 
                price <= market_price * settings.DEAL_THRESHOLD and
                price <= settings.STARTING_BANKROLL * settings.MAX_POSITION_PERCENT / 100):
                
                return {
                    'card_name': card_info['name'],
                    'set_name': card_info['set'],
                    'condition': card_info.get('condition', 'NM'),
                    'listing_price': price,
                    'market_price': market_price,
                    'profit_margin': profit_margin,
                    'platform': 'ebay',
                    'listing_url': item.get('itemWebUrl'),
                    'item_id': item.get('itemId'),
                    'seller': item.get('seller', {}).get('username'),
                    'ends_at': item.get('listingMarketplaceInfo', {}).get('auctionEndDate')
                }
        
        except Exception as e:
            logger.error(f"Error evaluating eBay item: {e}")
            return None
    
    def _parse_card_title(self, title: str) -> Optional[Dict]:
        """Parse card name and set from eBay title"""
        try:
            # Common Pokemon card title patterns
            patterns = [
                r'(.+?)\s+(\d+/\d+)\s+(.+?)\s+pokemon',
                r'(.+?)\s+pokemon\s+(.+?)\s+(\d+/\d+)',
                r'pokemon\s+(.+?)\s+(\d+/\d+)\s+(.+)',
                r'(.+?)\s+(\w+\s+\w+)\s+pokemon',
                r'(.+?)\s+pokemon\s+card'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, title, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    if len(groups) >= 2:
                        return {
                            'name': groups[0].strip(),
                            'set': groups[1].strip() if len(groups) > 1 else 'Unknown',
                            'number': groups[2].strip() if len(groups) > 2 else None
                        }
            
            # Fallback: just extract the first few words as card name
            words = title.split()
            if len(words) >= 2:
                return {
                    'name': ' '.join(words[:2]),
                    'set': 'Unknown'
                }
            
            return None
        except Exception as e:
            logger.error(f"Error parsing card title '{title}': {e}")
            return None
    
    def _get_market_price(self, card_info: Dict) -> Optional[float]:
        """Get market price from TCGPlayer or PriceCharting"""
        try:
            # First try TCGPlayer
            products = self.tcg_api.search_products(card_info['name'])
            if products:
                product_ids = [p['productId'] for p in products[:5]]  # Take first 5 matches
                pricing = self.tcg_api.get_product_pricing(product_ids)
                
                if pricing:
                    # Take the median market price
                    prices = [p['market_price'] for p in pricing.values() if p.get('market_price')]
                    if prices:
                        return sorted(prices)[len(prices) // 2]  # Median
            
            # Fallback to PriceCharting
            result = self.pricecharting_api.get_price(card_info['name'])
            if result and 'price' in result:
                return float(result['price'])
            
            return None
        except Exception as e:
            logger.error(f"Error getting market price for {card_info}: {e}")
            return None
    
    def _get_popular_search_terms(self) -> List[str]:
        """Get popular Pokemon card search terms"""
        return [
            "charizard",
            "pikachu",
            "lugia",
            "rayquaza",
            "mewtwo",
            "mew",
            "gyarados",
            "dragonite",
            "blastoise",
            "venusaur",
            "alakazam",
            "machamp",
            "gengar",
            "eevee",
            "snorlax",
            "base set",
            "shadowless",
            "first edition",
            "japanese",
            "promo",
            "holo",
            "rainbow rare",
            "secret rare",
            "full art",
            "alternate art"
        ]
    
    def save_deal(self, deal_data: Dict) -> Deal:
        """Save a deal to the database"""
        try:
            deal = Deal(
                card_name=deal_data['card_name'],
                set_name=deal_data['set_name'],
                condition=deal_data['condition'],
                listing_price=deal_data['listing_price'],
                market_price=deal_data['market_price'],
                profit_margin=deal_data['profit_margin'],
                platform=deal_data['platform'],
                listing_url=deal_data['listing_url'],
                status='found'
            )
            
            self.db.add(deal)
            self.db.commit()
            self.db.refresh(deal)
            
            return deal
        except Exception as e:
            logger.error(f"Error saving deal: {e}")
            self.db.rollback()
            raise
    
    def get_recent_deals(self, limit: int = 20) -> List[Deal]:
        """Get recent deals from database"""
        return self.db.query(Deal).order_by(Deal.created_at.desc()).limit(limit).all()
