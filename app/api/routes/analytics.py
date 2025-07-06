from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.database import get_db
from app.models.schemas import ProfitSummary
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/profit-summary")
async def get_profit_summary(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get profit summary for specified period"""
    try:
        from app.models.database import Sale, Transaction
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get sales revenue
        sales_query = db.query(Sale).filter(Sale.sale_date >= cutoff_date)
        total_revenue = sum(sale.sale_price for sale in sales_query.all())
        total_fees = sum(sale.fees for sale in sales_query.all())
        
        # Get purchase costs
        purchase_costs_query = (
            db.query(Transaction)
            .filter(Transaction.type == 'purchase')
            .filter(Transaction.date >= cutoff_date)
        )
        total_costs = sum(abs(transaction.amount) for transaction in purchase_costs_query.all())
        
        # Calculate metrics
        net_revenue = total_revenue - total_fees
        net_profit = net_revenue - total_costs
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        roi = (net_profit / total_costs * 100) if total_costs > 0 else 0
        
        return {
            "period_days": days,
            "total_revenue": total_revenue,
            "total_fees": total_fees,
            "net_revenue": net_revenue,
            "total_costs": total_costs,
            "net_profit": net_profit,
            "profit_margin": profit_margin,
            "roi": roi
        }
    except Exception as e:
        logger.error(f"Error getting profit summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get profit summary")

@router.get("/performance-metrics")
async def get_performance_metrics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get performance metrics"""
    try:
        from app.models.database import InventoryItem, Sale
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Total inventory items
        total_items = db.query(InventoryItem).count()
        
        # Items sold in period
        items_sold = (
            db.query(Sale)
            .filter(Sale.sale_date >= cutoff_date)
            .count()
        )
        
        # Average days to sell
        sold_items = (
            db.query(InventoryItem)
            .join(Sale)
            .filter(Sale.sale_date >= cutoff_date)
            .all()
        )
        
        avg_days_to_sell = 0
        if sold_items:
            total_days = sum(item.days_in_stock for item in sold_items)
            avg_days_to_sell = total_days / len(sold_items)
        
        # Turnover rate
        turnover_rate = (items_sold / total_items * 100) if total_items > 0 else 0
        
        # Items aged >60 days
        aged_items = (
            db.query(InventoryItem)
            .filter(InventoryItem.days_in_stock > 60)
            .filter(InventoryItem.status != 'sold')
            .count()
        )
        
        return {
            "total_inventory_items": total_items,
            "items_sold_period": items_sold,
            "average_days_to_sell": avg_days_to_sell,
            "turnover_rate": turnover_rate,
            "aged_items_60_plus": aged_items,
            "period_days": days
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")

@router.get("/cashflow")
async def get_cashflow(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get cashflow data"""
    try:
        from app.models.database import Transaction
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all transactions in period
        transactions = (
            db.query(Transaction)
            .filter(Transaction.date >= cutoff_date)
            .order_by(Transaction.date.desc())
            .all()
        )
        
        # Categorize transactions
        inflows = []
        outflows = []
        
        for transaction in transactions:
            if transaction.type in ['sale']:
                inflows.append({
                    'date': transaction.date,
                    'amount': transaction.amount,
                    'description': transaction.description,
                    'platform': transaction.platform
                })
            else:
                outflows.append({
                    'date': transaction.date,
                    'amount': abs(transaction.amount),
                    'description': transaction.description,
                    'platform': transaction.platform
                })
        
        total_inflow = sum(t['amount'] for t in inflows)
        total_outflow = sum(t['amount'] for t in outflows)
        net_cashflow = total_inflow - total_outflow
        
        return {
            "period_days": days,
            "total_inflow": total_inflow,
            "total_outflow": total_outflow,
            "net_cashflow": net_cashflow,
            "inflow_transactions": inflows,
            "outflow_transactions": outflows
        }
    except Exception as e:
        logger.error(f"Error getting cashflow: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cashflow")

@router.get("/top-performers")
async def get_top_performers(
    limit: int = 10,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get top performing cards by profit"""
    try:
        from app.models.database import Sale, InventoryItem, Card
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get sales with profit data
        sales_query = (
            db.query(Sale, InventoryItem, Card)
            .join(InventoryItem, Sale.inventory_item_id == InventoryItem.id)
            .join(Card, InventoryItem.card_id == Card.id)
            .filter(Sale.sale_date >= cutoff_date)
            .order_by(Sale.net_profit.desc())
            .limit(limit)
        )
        
        top_performers = []
        for sale, item, card in sales_query.all():
            profit_margin = (sale.net_profit / sale.sale_price * 100) if sale.sale_price > 0 else 0
            
            top_performers.append({
                'card_name': card.name,
                'set_name': card.set_name,
                'purchase_price': item.purchase_price,
                'sale_price': sale.sale_price,
                'net_profit': sale.net_profit,
                'profit_margin': profit_margin,
                'sale_date': sale.sale_date,
                'days_to_sell': item.days_in_stock
            })
        
        return {
            "period_days": days,
            "top_performers": top_performers
        }
    except Exception as e:
        logger.error(f"Error getting top performers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get top performers")

@router.get("/bankroll-status")
async def get_bankroll_status(db: Session = Depends(get_db)):
    """Get current bankroll status"""
    try:
        from app.models.database import Transaction, InventoryItem
        from app.core.config import settings
        
        # Calculate current cash position
        total_inflow = (
            db.query(Transaction)
            .filter(Transaction.type.in_(['sale', 'deposit']))
            .with_entities(db.func.sum(Transaction.amount))
            .scalar()
        ) or 0
        
        total_outflow = (
            db.query(Transaction)
            .filter(Transaction.type.in_(['purchase', 'fee']))
            .with_entities(db.func.sum(Transaction.amount))
            .scalar()
        ) or 0
        
        current_cash = total_inflow - abs(total_outflow)
        
        # Calculate inventory value
        inventory_value = (
            db.query(InventoryItem)
            .filter(InventoryItem.status != 'sold')
            .with_entities(db.func.sum(InventoryItem.purchase_price))
            .scalar()
        ) or 0
        
        total_bankroll = current_cash + inventory_value
        cash_percentage = (current_cash / total_bankroll * 100) if total_bankroll > 0 else 0
        
        return {
            "starting_bankroll": settings.STARTING_BANKROLL,
            "current_cash": current_cash,
            "inventory_value": inventory_value,
            "total_bankroll": total_bankroll,
            "cash_percentage": cash_percentage,
            "growth": total_bankroll - settings.STARTING_BANKROLL,
            "growth_percentage": ((total_bankroll - settings.STARTING_BANKROLL) / settings.STARTING_BANKROLL * 100) if settings.STARTING_BANKROLL > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error getting bankroll status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bankroll status")
