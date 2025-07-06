from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.database import Card, InventoryItem, PriceHistory
from app.services.external_apis import TCGPlayerAPI, COMCService
from app.core.config import settings
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PricingService:
    """Service for managing card pricing and repricing"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tcg_api = TCGPlayerAPI()
        self.comc_service = COMCService()
    
    def update_market_prices(self, card_ids: List[int] = None) -> int:
        """Update market prices for cards"""
        try:
            query = self.db.query(Card)
            if card_ids:
                query = query.filter(Card.id.in_(card_ids))
            
            cards = query.all()
            updated_count = 0
            
            for card in cards:
                try:
                    market_price = self._get_current_market_price(card)
                    if market_price:
                        self._save_price_history(card.id, 'tcgplayer', 'market', market_price)
                        updated_count += 1
                except Exception as e:
                    logger.error(f"Error updating price for card {card.id}: {e}")
                    continue
            
            return updated_count
        except Exception as e:
            logger.error(f"Error updating market prices: {e}")
            return 0
    
    def _get_current_market_price(self, card: Card) -> Optional[float]:
        """Get current market price for a card"""
        try:
            if card.tcg_product_id:
                pricing = self.tcg_api.get_product_pricing([int(card.tcg_product_id)])
                if pricing and int(card.tcg_product_id) in pricing:
                    return pricing[int(card.tcg_product_id)].get('market_price')
            
            # Fallback: search by name
            products = self.tcg_api.search_products(card.name)
            if products:
                product_ids = [p['productId'] for p in products[:3]]
                pricing = self.tcg_api.get_product_pricing(product_ids)
                
                if pricing:
                    prices = [p['market_price'] for p in pricing.values() if p.get('market_price')]
                    if prices:
                        return sorted(prices)[len(prices) // 2]  # Median
            
            return None
        except Exception as e:
            logger.error(f"Error getting market price for card {card.name}: {e}")
            return None
    
    def _save_price_history(self, card_id: int, platform: str, price_type: str, price: float):
        """Save price history record"""
        try:
            price_history = PriceHistory(
                card_id=card_id,
                platform=platform,
                price_type=price_type,
                price=price,
                date=datetime.utcnow()
            )
            
            self.db.add(price_history)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error saving price history: {e}")
            self.db.rollback()
    
    def calculate_optimal_price(self, inventory_item: InventoryItem) -> float:
        """Calculate optimal selling price for inventory item"""
        try:
            # Get latest market price
            latest_price = self._get_latest_market_price(inventory_item.card_id)
            if not latest_price:
                return inventory_item.purchase_price * 1.2  # 20% markup fallback
            
            # Base pricing logic from your plan
            if inventory_item.card.card_type == "raw":
                target_price = latest_price * 0.98  # 2% below market
                
                # Apply aging markdown
                if inventory_item.days_in_stock > settings.RAW_AGING_DAYS:
                    target_price *= 0.95  # 5% markdown
                
            elif inventory_item.card.card_type == "graded":
                # For graded cards, get 7-day average
                avg_price = self._get_average_sold_price(inventory_item.card_id, days=7)
                if avg_price:
                    target_price = avg_price * 1.05  # 5% above recent sales
                else:
                    target_price = latest_price * 1.02  # 2% above market
                
                # Apply aging markdown
                if inventory_item.days_in_stock > settings.SLAB_AGING_DAYS:
                    target_price *= 0.97  # 3% markdown
            
            else:
                target_price = latest_price * 0.98
            
            # Ensure minimum profit margin
            min_price = inventory_item.purchase_price * 1.1  # 10% minimum markup
            return max(target_price, min_price)
            
        except Exception as e:
            logger.error(f"Error calculating optimal price: {e}")
            return inventory_item.purchase_price * 1.2
    
    def _get_latest_market_price(self, card_id: int) -> Optional[float]:
        """Get latest market price for a card"""
        try:
            latest_price = (
                self.db.query(PriceHistory)
                .filter(PriceHistory.card_id == card_id)
                .filter(PriceHistory.price_type == 'market')
                .order_by(PriceHistory.date.desc())
                .first()
            )
            
            return latest_price.price if latest_price else None
        except Exception as e:
            logger.error(f"Error getting latest market price: {e}")
            return None
    
    def _get_average_sold_price(self, card_id: int, days: int = 7) -> Optional[float]:
        """Get average sold price for a card over specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # This would need to be implemented with actual sales data
            # For now, return the latest market price
            return self._get_latest_market_price(card_id)
        except Exception as e:
            logger.error(f"Error getting average sold price: {e}")
            return None
    
    def run_repricing(self) -> Dict[str, int]:
        """Run repricing for all active inventory"""
        try:
            # Get all listed inventory items
            inventory_items = (
                self.db.query(InventoryItem)
                .filter(InventoryItem.status == 'listed')
                .all()
            )
            
            results = {
                'total_items': len(inventory_items),
                'repriced_items': 0,
                'errors': 0
            }
            
            pricing_updates = []
            
            for item in inventory_items:
                try:
                    # Calculate new optimal price
                    new_price = self.calculate_optimal_price(item)
                    
                    # Only update if price changed significantly (>2%)
                    if (item.list_price is None or 
                        abs(new_price - item.list_price) / item.list_price > 0.02):
                        
                        # Update database
                        item.list_price = new_price
                        item.updated_at = datetime.utcnow()
                        
                        # Prepare for platform updates
                        pricing_updates.append({
                            'sku': item.sku,
                            'price': new_price,
                            'platform': item.platform
                        })
                        
                        results['repriced_items'] += 1
                
                except Exception as e:
                    logger.error(f"Error repricing item {item.sku}: {e}")
                    results['errors'] += 1
            
            # Commit database changes
            self.db.commit()
            
            # Update platform pricing
            self._update_platform_pricing(pricing_updates)
            
            return results
        except Exception as e:
            logger.error(f"Error running repricing: {e}")
            self.db.rollback()
            return {'total_items': 0, 'repriced_items': 0, 'errors': 1}
    
    def _update_platform_pricing(self, pricing_updates: List[Dict]):
        """Update pricing on external platforms"""
        try:
            # Group by platform
            comc_updates = [u for u in pricing_updates if u['platform'] == 'comc']
            
            # Update COMC pricing
            if comc_updates:
                comc_data = [
                    {
                        'sku': update['sku'],
                        'price': update['price']
                    }
                    for update in comc_updates
                ]
                
                success = self.comc_service.update_pricing(comc_data)
                if success:
                    logger.info(f"Updated pricing for {len(comc_updates)} COMC items")
                else:
                    logger.error("Failed to update COMC pricing")
            
            # TODO: Add TCGPlayer and eBay pricing updates
            
        except Exception as e:
            logger.error(f"Error updating platform pricing: {e}")
    
    def get_pricing_recommendations(self, limit: int = 20) -> List[Dict]:
        """Get pricing recommendations for inventory"""
        try:
            inventory_items = (
                self.db.query(InventoryItem)
                .filter(InventoryItem.status == 'listed')
                .order_by(InventoryItem.days_in_stock.desc())
                .limit(limit)
                .all()
            )
            
            recommendations = []
            
            for item in inventory_items:
                try:
                    optimal_price = self.calculate_optimal_price(item)
                    current_price = item.list_price or item.purchase_price
                    
                    price_change = optimal_price - current_price
                    price_change_percent = (price_change / current_price) * 100
                    
                    recommendations.append({
                        'sku': item.sku,
                        'card_name': item.card.name,
                        'current_price': current_price,
                        'recommended_price': optimal_price,
                        'price_change': price_change,
                        'price_change_percent': price_change_percent,
                        'days_in_stock': item.days_in_stock,
                        'purchase_price': item.purchase_price
                    })
                except Exception as e:
                    logger.error(f"Error getting recommendation for item {item.sku}: {e}")
                    continue
            
            return recommendations
        except Exception as e:
            logger.error(f"Error getting pricing recommendations: {e}")
            return []
