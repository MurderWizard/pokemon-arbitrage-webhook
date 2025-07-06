"""
Vault Portfolio Manager - Handle multiple asset classes in secure storage
"""
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
import logging
from dataclasses import dataclass
from core.asset_classes import CollectibleAsset, MarketMetrics

logger = logging.getLogger(__name__)

@dataclass
class VaultPosition:
    """Track an asset position in the vault"""
    asset: CollectibleAsset
    purchase_price: Decimal
    purchase_date: datetime
    grading_status: str
    location: str  # e.g., "eBay vault", "PSA vault", etc.
    insurance_value: Decimal
    last_appraisal: datetime
    target_sell_price: Optional[Decimal] = None
    notes: str = ""

class VaultPortfolio:
    """Manage a portfolio of vaulted assets"""
    
    def __init__(self):
        self.positions: Dict[str, VaultPosition] = {}
        self.total_cost_basis = Decimal(0)
        self.total_insurance_value = Decimal(0)
        
    def add_position(self, asset_id: str, position: VaultPosition):
        """Add a new position to the portfolio"""
        self.positions[asset_id] = position
        self.total_cost_basis += position.purchase_price
        self.total_insurance_value += position.insurance_value
        
    def remove_position(self, asset_id: str, sale_price: Decimal):
        """Remove a position (e.g., after sale)"""
        if asset_id in self.positions:
            position = self.positions[asset_id]
            profit = sale_price - position.purchase_price
            roi = (profit / position.purchase_price) * 100
            
            logger.info(f"Sold {asset_id} for ${sale_price}. Profit: ${profit} (ROI: {roi:.1f}%)")
            
            self.total_cost_basis -= position.purchase_price
            self.total_insurance_value -= position.insurance_value
            del self.positions[asset_id]
            
    def get_portfolio_metrics(self) -> Dict:
        """Calculate portfolio-wide metrics"""
        total_value = sum(p.asset.get_market_price("current")[0] for p in self.positions.values())
        unrealized_gains = total_value - self.total_cost_basis
        
        return {
            "total_positions": len(self.positions),
            "cost_basis": self.total_cost_basis,
            "current_value": total_value,
            "unrealized_gains": unrealized_gains,
            "roi_percentage": (unrealized_gains / self.total_cost_basis * 100) if self.total_cost_basis else 0,
            "insurance_value": self.total_insurance_value
        }
        
    def get_portfolio_allocation(self) -> Dict[str, Decimal]:
        """Get allocation by asset class"""
        allocation = {}
        total_value = Decimal(0)
        
        for position in self.positions.values():
            asset_class = position.asset.__class__.__name__
            current_value = position.asset.get_market_price("current")[0]
            allocation[asset_class] = allocation.get(asset_class, Decimal(0)) + current_value
            total_value += current_value
            
        # Convert to percentages
        if total_value > 0:
            allocation = {k: (v/total_value * 100) for k, v in allocation.items()}
            
        return allocation
        
    def get_grading_opportunities(self, min_roi: float = 35.0) -> List[Dict]:
        """Find positions that might benefit from grading"""
        opportunities = []
        
        for asset_id, position in self.positions.items():
            if position.grading_status == "raw":
                roi_data = position.asset.calculate_grading_roi(position.purchase_price, "current")
                if roi_data["expected_roi"] >= min_roi:
                    opportunities.append({
                        "asset_id": asset_id,
                        "current_value": position.asset.get_market_price("current")[0],
                        "grading_cost": roi_data["grading_cost"],
                        "expected_value": roi_data["expected_value"],
                        "expected_roi": roi_data["expected_roi"]
                    })
                    
        return opportunities
        
    def get_rebalancing_suggestions(self, target_allocation: Dict[str, float]) -> List[Dict]:
        """Get suggestions to rebalance the portfolio"""
        current_allocation = self.get_portfolio_allocation()
        suggestions = []
        
        for asset_class, target_pct in target_allocation.items():
            current_pct = current_allocation.get(asset_class, Decimal(0))
            diff = target_pct - current_pct
            
            if abs(diff) >= 5:  # 5% threshold for rebalancing
                suggestions.append({
                    "asset_class": asset_class,
                    "current_allocation": current_pct,
                    "target_allocation": target_pct,
                    "difference": diff,
                    "action": "buy" if diff > 0 else "sell",
                    "amount": abs(diff / 100 * self.total_insurance_value)
                })
                
        return suggestions
        
    def export_portfolio_report(self) -> Dict:
        """Generate a detailed portfolio report"""
        metrics = self.get_portfolio_metrics()
        allocation = self.get_portfolio_allocation()
        
        report = {
            "summary": metrics,
            "allocation": allocation,
            "positions": {},
            "grading_opportunities": self.get_grading_opportunities(),
            "timestamp": datetime.now().isoformat()
        }
        
        for asset_id, position in self.positions.items():
            market_data = position.asset.market_data
            report["positions"][asset_id] = {
                "asset_class": position.asset.__class__.__name__,
                "purchase_info": {
                    "date": position.purchase_date.isoformat(),
                    "price": float(position.purchase_price),
                    "location": position.location
                },
                "current_value": float(position.asset.get_market_price("current")[0]),
                "market_metrics": market_data.__dict__ if market_data else None,
                "grading_status": position.grading_status,
                "unrealized_gain": float(
                    position.asset.get_market_price("current")[0] - position.purchase_price
                )
            }
            
        return report
