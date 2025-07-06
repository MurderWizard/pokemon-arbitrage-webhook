#!/usr/bin/env python3
"""
Advanced Repricing Strategy for Pokemon Card Arbitrage
Ready for when we start selling cards - full profit optimization

Features:
- Smart pricing based on market conditions
- Profit margin protection
- Aging discounts and market timing
- Platform integration ready
- Manual approval workflows
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pokemon_price_system import price_db
from ebay_browse_api_integration import EbayBrowseAPI

@dataclass
class InventoryItem:
    """Represents a card in our inventory"""
    sku: str
    card_name: str
    set_name: str
    condition: str
    grade: Optional[int]
    purchase_price: float
    current_list_price: Optional[float]
    platform: str  # 'ebay', 'comc', 'tcgplayer'
    date_listed: datetime
    days_in_stock: int
    is_graded: bool = False
    
@dataclass
class PricingRecommendation:
    """Pricing recommendation with reasoning"""
    sku: str
    current_price: float
    recommended_price: float
    price_change: float
    price_change_percent: float
    reasoning: str
    confidence: str
    market_data: Dict
    profit_margin: float
    min_price: float

class AdvancedRepricingEngine:
    """Advanced repricing engine for maximum profitability"""
    
    def __init__(self):
        self.price_db = price_db
        self.browse_api = EbayBrowseAPI()
        self.inventory_db_path = "inventory.db"
        self._init_inventory_db()
        
        # Pricing rules
        self.MIN_PROFIT_MARGIN = 0.20  # 20% minimum markup
        self.RAW_CARD_DISCOUNT = 0.02   # 2% below market for raw cards
        self.GRADED_PREMIUM = 0.05      # 5% premium for PSA 9/10
        self.AGING_DISCOUNT_30_DAYS = 0.05  # 5% after 30 days
        self.AGING_DISCOUNT_60_DAYS = 0.10  # 10% after 60 days
        self.AGING_DISCOUNT_90_DAYS = 0.15  # 15% after 90 days
        
    def _init_inventory_db(self):
        """Initialize inventory database"""
        conn = sqlite3.connect(self.inventory_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                sku TEXT PRIMARY KEY,
                card_name TEXT NOT NULL,
                set_name TEXT NOT NULL,
                condition TEXT NOT NULL,
                grade INTEGER,
                purchase_price REAL NOT NULL,
                current_list_price REAL,
                platform TEXT NOT NULL,
                date_listed TEXT NOT NULL,
                date_purchased TEXT,
                status TEXT DEFAULT 'listed'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repricing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL,
                old_price REAL,
                new_price REAL,
                reason TEXT,
                timestamp TEXT NOT NULL,
                applied BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_inventory_item(self, item: InventoryItem):
        """Add item to inventory"""
        conn = sqlite3.connect(self.inventory_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO inventory 
            (sku, card_name, set_name, condition, grade, purchase_price, 
             current_list_price, platform, date_listed, date_purchased)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.sku, item.card_name, item.set_name, item.condition,
            item.grade, item.purchase_price, item.current_list_price,
            item.platform, item.date_listed.isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
    def get_inventory_items(self) -> List[InventoryItem]:
        """Get all active inventory items"""
        conn = sqlite3.connect(self.inventory_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sku, card_name, set_name, condition, grade, purchase_price,
                   current_list_price, platform, date_listed
            FROM inventory 
            WHERE status = 'listed'
        ''')
        
        items = []
        for row in cursor.fetchall():
            date_listed = datetime.fromisoformat(row[8])
            days_in_stock = (datetime.now() - date_listed).days
            
            items.append(InventoryItem(
                sku=row[0],
                card_name=row[1],
                set_name=row[2],
                condition=row[3],
                grade=row[4],
                purchase_price=row[5],
                current_list_price=row[6],
                platform=row[7],
                date_listed=date_listed,
                days_in_stock=days_in_stock,
                is_graded=row[4] is not None
            ))
            
        conn.close()
        return items
        
    def generate_repricing_recommendations(self) -> List[PricingRecommendation]:
        """Generate repricing recommendations for all inventory"""
        print("🔄 GENERATING REPRICING RECOMMENDATIONS")
        print("=" * 50)
        
        inventory = self.get_inventory_items()
        recommendations = []
        
        for item in inventory:
            try:
                recommendation = self._calculate_optimal_price(item)
                if recommendation:
                    recommendations.append(recommendation)
                    
            except Exception as e:
                print(f"⚠️ Error pricing {item.sku}: {e}")
                
        # Sort by potential profit impact
        recommendations.sort(key=lambda x: abs(x.price_change), reverse=True)
        
        self._show_recommendations_summary(recommendations)
        return recommendations
        
    def _calculate_optimal_price(self, item: InventoryItem) -> Optional[PricingRecommendation]:
        """Calculate optimal price for an inventory item"""
        
        # Get current market data
        market_data = self._get_market_data(item)
        if not market_data:
            return None
            
        current_market_price = market_data['market_price']
        market_trend = market_data.get('trend', 'stable')
        
        # Base pricing strategy
        if item.is_graded and item.grade >= 9:
            # Premium for high-grade cards
            base_price = current_market_price * (1 + self.GRADED_PREMIUM)
            strategy = "graded_premium"
        elif item.is_graded:
            # Slight discount for lower grades
            base_price = current_market_price * 0.95
            strategy = "graded_discount"
        else:
            # Raw cards: slight below market
            base_price = current_market_price * (1 - self.RAW_CARD_DISCOUNT)
            strategy = "raw_competitive"
            
        # Apply aging discounts
        if item.days_in_stock > 90:
            base_price *= (1 - self.AGING_DISCOUNT_90_DAYS)
            strategy += "_aged_90d"
        elif item.days_in_stock > 60:
            base_price *= (1 - self.AGING_DISCOUNT_60_DAYS)
            strategy += "_aged_60d"
        elif item.days_in_stock > 30:
            base_price *= (1 - self.AGING_DISCOUNT_30_DAYS)
            strategy += "_aged_30d"
            
        # Market trend adjustments
        if market_trend == 'rising':
            base_price *= 1.03  # 3% premium for rising market
            strategy += "_trend_up"
        elif market_trend == 'falling':
            base_price *= 0.97  # 3% discount for falling market
            strategy += "_trend_down"
            
        # Profit protection
        min_price = item.purchase_price * (1 + self.MIN_PROFIT_MARGIN)
        final_price = max(base_price, min_price)
        
        # Calculate changes
        current_price = item.current_list_price or item.purchase_price * 1.3
        price_change = final_price - current_price
        price_change_percent = (price_change / current_price) * 100
        profit_margin = ((final_price - item.purchase_price) / item.purchase_price) * 100
        
        # Generate reasoning
        reasoning = self._generate_pricing_reasoning(
            item, market_data, strategy, final_price, min_price
        )
        
        # Confidence level
        confidence = self._calculate_confidence(market_data, item)
        
        return PricingRecommendation(
            sku=item.sku,
            current_price=current_price,
            recommended_price=final_price,
            price_change=price_change,
            price_change_percent=price_change_percent,
            reasoning=reasoning,
            confidence=confidence,
            market_data=market_data,
            profit_margin=profit_margin,
            min_price=min_price
        )
        
    def _get_market_data(self, item: InventoryItem) -> Optional[Dict]:
        """Get current market data for a card"""
        
        # First try our price database
        price_data = self.price_db.get_card_price(item.card_name, item.set_name)
        
        if price_data:
            # Check if price is fresh (< 48 hours)
            last_updated = datetime.fromisoformat(price_data['last_updated'])
            hours_old = (datetime.now() - last_updated).total_seconds() / 3600
            
            market_data = {
                'market_price': price_data['market_price'],
                'last_updated': price_data['last_updated'],
                'source': 'price_database',
                'freshness_hours': hours_old,
                'trend': price_data.get('price_trend', 'stable')
            }
            
            # If price is stale, try to get fresh data
            if hours_old > 48:
                fresh_data = self._get_fresh_market_data(item)
                if fresh_data:
                    market_data.update(fresh_data)
                    
            return market_data
            
        # Fallback: try to get fresh market data
        return self._get_fresh_market_data(item)
        
    def _get_fresh_market_data(self, item: InventoryItem) -> Optional[Dict]:
        """Get fresh market data using Browse API"""
        try:
            search_query = f"{item.card_name} {item.set_name}"
            items = self.browse_api.search_pokemon_cards(
                search_query,
                min_price=10,
                max_price=1000,
                limit=50
            )
            
            if items:
                # Analyze current listings
                prices = [item.get('price', 0) for item in items if item.get('price', 0) > 0]
                
                if prices:
                    market_price = sorted(prices)[len(prices) // 2]  # Median price
                    
                    return {
                        'market_price': market_price,
                        'source': 'browse_api_fresh',
                        'listing_count': len(prices),
                        'price_range': f"${min(prices):.2f} - ${max(prices):.2f}",
                        'freshness_hours': 0
                    }
                    
        except Exception as e:
            print(f"   ⚠️ Error getting fresh data for {item.card_name}: {e}")
            
        return None
        
    def _generate_pricing_reasoning(self, item: InventoryItem, market_data: Dict, 
                                  strategy: str, final_price: float, min_price: float) -> str:
        """Generate human-readable pricing reasoning"""
        
        reasons = []
        
        # Base strategy
        if 'graded_premium' in strategy:
            reasons.append(f"PSA {item.grade} premium pricing")
        elif 'graded_discount' in strategy:
            reasons.append(f"PSA {item.grade} competitive pricing")
        elif 'raw_competitive' in strategy:
            reasons.append("Raw card competitive pricing")
            
        # Aging
        if 'aged_90d' in strategy:
            reasons.append("90+ day aging discount")
        elif 'aged_60d' in strategy:
            reasons.append("60+ day aging discount")
        elif 'aged_30d' in strategy:
            reasons.append("30+ day aging discount")
            
        # Trend
        if 'trend_up' in strategy:
            reasons.append("rising market premium")
        elif 'trend_down' in strategy:
            reasons.append("falling market adjustment")
            
        # Profit protection
        if final_price == min_price:
            reasons.append("minimum profit protection")
            
        reasoning = f"Market: ${market_data['market_price']:.2f} | Strategy: {', '.join(reasons)}"
        
        return reasoning
        
    def _calculate_confidence(self, market_data: Dict, item: InventoryItem) -> str:
        """Calculate confidence level for pricing recommendation"""
        
        freshness_hours = market_data.get('freshness_hours', 0)
        source = market_data.get('source', 'unknown')
        listing_count = market_data.get('listing_count', 0)
        
        if freshness_hours <= 24 and listing_count >= 10:
            return "HIGH"
        elif freshness_hours <= 48 and listing_count >= 5:
            return "MEDIUM"
        elif source == 'price_database':
            return "MEDIUM"
        else:
            return "LOW"
            
    def _show_recommendations_summary(self, recommendations: List[PricingRecommendation]):
        """Show summary of repricing recommendations"""
        
        if not recommendations:
            print("📊 No repricing recommendations at this time")
            return
            
        print(f"\n📊 REPRICING RECOMMENDATIONS ({len(recommendations)} items)")
        print("-" * 70)
        
        total_impact = sum(rec.price_change for rec in recommendations)
        avg_margin = sum(rec.profit_margin for rec in recommendations) / len(recommendations)
        
        print(f"💰 Total Revenue Impact: ${total_impact:+.2f}")
        print(f"📈 Average Profit Margin: {avg_margin:.1f}%")
        
        print(f"\n🔄 Top Recommendations:")
        for i, rec in enumerate(recommendations[:10], 1):
            action = "📈 INCREASE" if rec.price_change > 0 else "📉 DECREASE"
            print(f"   {i:2d}. {rec.sku}: {action} ${rec.price_change:+.2f} ({rec.price_change_percent:+.1f}%)")
            print(f"       {rec.reasoning}")
            print(f"       Confidence: {rec.confidence} | Margin: {rec.profit_margin:.1f}%")
            print()
            
    def apply_repricing(self, recommendations: List[PricingRecommendation], 
                       auto_apply_threshold: float = 5.0) -> Dict:
        """Apply repricing recommendations"""
        
        print(f"\n🔄 APPLYING REPRICING RECOMMENDATIONS")
        print("=" * 50)
        
        results = {
            'auto_applied': 0,
            'manual_approval': 0,
            'errors': 0,
            'total_revenue_impact': 0.0
        }
        
        for rec in recommendations:
            try:
                # Auto-apply small changes
                if abs(rec.price_change_percent) <= auto_apply_threshold and rec.confidence in ['HIGH', 'MEDIUM']:
                    success = self._update_listing_price(rec.sku, rec.recommended_price)
                    if success:
                        results['auto_applied'] += 1
                        results['total_revenue_impact'] += rec.price_change
                        self._log_repricing(rec, applied=True, method='auto')
                        print(f"   ✅ Auto-applied: {rec.sku} -> ${rec.recommended_price:.2f}")
                    else:
                        results['errors'] += 1
                        
                else:
                    # Queue for manual approval
                    results['manual_approval'] += 1
                    self._log_repricing(rec, applied=False, method='manual_queue')
                    print(f"   📋 Manual review: {rec.sku} ({rec.price_change_percent:+.1f}%)")
                    
            except Exception as e:
                print(f"   ❌ Error processing {rec.sku}: {e}")
                results['errors'] += 1
                
        self._show_repricing_results(results)
        return results
        
    def _update_listing_price(self, sku: str, new_price: float) -> bool:
        """Update listing price on platform"""
        # This would integrate with eBay/COMC/TCGPlayer APIs
        # For now, just update our database
        
        conn = sqlite3.connect(self.inventory_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE inventory 
            SET current_list_price = ? 
            WHERE sku = ?
        ''', (new_price, sku))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
        
    def _log_repricing(self, rec: PricingRecommendation, applied: bool, method: str):
        """Log repricing action"""
        conn = sqlite3.connect(self.inventory_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO repricing_history 
            (sku, old_price, new_price, reason, timestamp, applied)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            rec.sku, rec.current_price, rec.recommended_price,
            f"{method}: {rec.reasoning}", datetime.now().isoformat(), applied
        ))
        
        conn.commit()
        conn.close()
        
    def _show_repricing_results(self, results: Dict):
        """Show repricing results summary"""
        print(f"\n🎉 REPRICING RESULTS")
        print("-" * 30)
        print(f"✅ Auto-applied: {results['auto_applied']}")
        print(f"📋 Manual review: {results['manual_approval']}")
        print(f"❌ Errors: {results['errors']}")
        print(f"💰 Revenue impact: ${results['total_revenue_impact']:+.2f}")
        
        if results['manual_approval'] > 0:
            print(f"\n📝 Next: Review {results['manual_approval']} items manually")
            print("   Use: python3 repricing_engine.py manual_review")
            
    def get_manual_review_queue(self) -> List[Dict]:
        """Get items pending manual review"""
        conn = sqlite3.connect(self.inventory_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sku, old_price, new_price, reason, timestamp
            FROM repricing_history 
            WHERE applied = FALSE AND reason LIKE 'manual_queue:%'
            ORDER BY timestamp DESC
        ''')
        
        queue = []
        for row in cursor.fetchall():
            queue.append({
                'sku': row[0],
                'old_price': row[1],
                'new_price': row[2],
                'reason': row[3],
                'timestamp': row[4]
            })
            
        conn.close()
        return queue
        
    def run_daily_repricing(self):
        """Run daily repricing routine"""
        print("🔄 DAILY REPRICING ROUTINE")
        print("=" * 40)
        
        # Check if we have any inventory
        inventory = self.get_inventory_items()
        
        if not inventory:
            print("📦 No inventory to reprice yet")
            print("💡 Add inventory with: repricing_engine.add_sample_inventory()")
            return
            
        print(f"📦 Found {len(inventory)} items to evaluate")
        
        # Generate recommendations
        recommendations = self.generate_repricing_recommendations()
        
        # Apply safe changes automatically
        if recommendations:
            results = self.apply_repricing(recommendations)
            
            # Show manual review queue if needed
            manual_queue = self.get_manual_review_queue()
            if manual_queue:
                print(f"\n📋 Manual Review Queue ({len(manual_queue)} items):")
                for item in manual_queue[:5]:
                    print(f"   • {item['sku']}: ${item['old_price']:.2f} -> ${item['new_price']:.2f}")
                    
    def add_sample_inventory(self):
        """Add sample inventory for testing"""
        print("🎲 Adding sample inventory for demonstration...")
        
        sample_items = [
            InventoryItem(
                sku="PSA10-CHAR-001",
                card_name="Charizard VMAX",
                set_name="Champions Path",
                condition="Near Mint",
                grade=10,
                purchase_price=65.0,
                current_list_price=95.0,
                platform="ebay",
                date_listed=datetime.now() - timedelta(days=15),
                days_in_stock=15,
                is_graded=True
            ),
            InventoryItem(
                sku="RAW-UMB-002",
                card_name="Umbreon VMAX",
                set_name="Evolving Skies", 
                condition="Near Mint",
                grade=None,
                purchase_price=45.0,
                current_list_price=85.0,
                platform="ebay",
                date_listed=datetime.now() - timedelta(days=35),
                days_in_stock=35,
                is_graded=False
            )
        ]
        
        for item in sample_items:
            self.add_inventory_item(item)
            print(f"   ✅ Added: {item.sku} - {item.card_name}")
            
        print(f"📦 Sample inventory ready for repricing!")

def main():
    """Main function"""
    import sys
    
    engine = AdvancedRepricingEngine()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'add_sample':
            engine.add_sample_inventory()
        elif command == 'manual_review':
            queue = engine.get_manual_review_queue()
            print(f"📋 Manual Review Queue: {len(queue)} items")
            for item in queue:
                print(f"   {item}")
        else:
            print("Unknown command")
    else:
        engine.run_daily_repricing()

if __name__ == "__main__":
    main()
