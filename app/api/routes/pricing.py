from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.database import get_db
from app.services.pricing import PricingService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/recommendations")
async def get_pricing_recommendations(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get pricing recommendations for inventory"""
    try:
        pricing_service = PricingService(db)
        recommendations = pricing_service.get_pricing_recommendations(limit)
        return recommendations
    except Exception as e:
        logger.error(f"Error getting pricing recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pricing recommendations")

@router.post("/update-market-prices")
async def update_market_prices(
    card_ids: Optional[List[int]] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Update market prices for cards"""
    try:
        background_tasks.add_task(update_market_prices_task, db, card_ids)
        return {"message": "Market price update started", "status": "processing"}
    except Exception as e:
        logger.error(f"Error starting market price update: {e}")
        raise HTTPException(status_code=500, detail="Failed to start market price update")

@router.get("/market-price/{card_id}")
async def get_market_price(
    card_id: int,
    db: Session = Depends(get_db)
):
    """Get current market price for a card"""
    try:
        from app.models.database import Card, PriceHistory
        
        # Get the card
        card = db.query(Card).filter(Card.id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # Get latest price history
        latest_price = (
            db.query(PriceHistory)
            .filter(PriceHistory.card_id == card_id)
            .filter(PriceHistory.price_type == 'market')
            .order_by(PriceHistory.date.desc())
            .first()
        )
        
        if not latest_price:
            return {"card_id": card_id, "card_name": card.name, "market_price": None}
        
        return {
            "card_id": card_id,
            "card_name": card.name,
            "market_price": latest_price.price,
            "last_updated": latest_price.date
        }
    except Exception as e:
        logger.error(f"Error getting market price for card {card_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market price")

@router.get("/price-history/{card_id}")
async def get_price_history(
    card_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get price history for a card"""
    try:
        from app.models.database import PriceHistory
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        price_history = (
            db.query(PriceHistory)
            .filter(PriceHistory.card_id == card_id)
            .filter(PriceHistory.date >= cutoff_date)
            .order_by(PriceHistory.date.desc())
            .all()
        )
        
        return {
            "card_id": card_id,
            "days": days,
            "price_history": [
                {
                    "date": record.date,
                    "platform": record.platform,
                    "price_type": record.price_type,
                    "price": record.price
                }
                for record in price_history
            ]
        }
    except Exception as e:
        logger.error(f"Error getting price history for card {card_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get price history")

async def update_market_prices_task(db: Session, card_ids: Optional[List[int]] = None):
    """Background task to update market prices"""
    try:
        pricing_service = PricingService(db)
        updated_count = pricing_service.update_market_prices(card_ids)
        logger.info(f"Updated market prices for {updated_count} cards")
    except Exception as e:
        logger.error(f"Error in market price update task: {e}")
