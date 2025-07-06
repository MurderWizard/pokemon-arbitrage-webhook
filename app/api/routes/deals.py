from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.database import get_db
from app.models.schemas import Deal, DealCreate
from app.services.deal_finder import DealFinder
from app.services.external_apis import EbayAPI
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[Deal])
async def get_deals(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get recent deals from database"""
    try:
        deal_finder = DealFinder(db)
        deals = deal_finder.get_recent_deals(limit)
        return deals
    except Exception as e:
        logger.error(f"Error getting deals: {e}")
        raise HTTPException(status_code=500, detail="Failed to get deals")

@router.post("/find")
async def find_deals(
    search_terms: Optional[List[str]] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Find new deals based on search terms"""
    try:
        deal_finder = DealFinder(db)
        
        # Run deal finding in background
        background_tasks.add_task(find_and_save_deals, db, search_terms)
        
        return {"message": "Deal finding started", "status": "processing"}
    except Exception as e:
        logger.error(f"Error starting deal finding: {e}")
        raise HTTPException(status_code=500, detail="Failed to start deal finding")

@router.get("/stats")
async def get_deal_stats(db: Session = Depends(get_db)):
    """Get deal statistics"""
    try:
        from app.models.database import Deal
        
        total_deals = db.query(Deal).count()
        
        # Get deals by status
        found_deals = db.query(Deal).filter(Deal.status == 'found').count()
        purchased_deals = db.query(Deal).filter(Deal.status == 'purchased').count()
        
        # Get average profit margin
        avg_margin = db.query(Deal).with_entities(
            db.func.avg(Deal.profit_margin)
        ).scalar() or 0
        
        return {
            "total_deals": total_deals,
            "found_deals": found_deals,
            "purchased_deals": purchased_deals,
            "passed_deals": total_deals - found_deals - purchased_deals,
            "average_profit_margin": float(avg_margin)
        }
    except Exception as e:
        logger.error(f"Error getting deal stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get deal statistics")

@router.post("/{deal_id}/purchase")
async def purchase_deal(
    deal_id: int,
    db: Session = Depends(get_db)
):
    """Mark a deal as purchased (manual trigger)"""
    try:
        from app.models.database import Deal
        
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        
        # TODO: Implement actual purchase logic via eBay API
        deal.status = 'purchased'
        db.commit()
        
        return {"message": "Deal marked as purchased", "deal_id": deal_id}
    except Exception as e:
        logger.error(f"Error purchasing deal {deal_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to purchase deal")

@router.post("/{deal_id}/pass")
async def pass_deal(
    deal_id: int,
    db: Session = Depends(get_db)
):
    """Mark a deal as passed"""
    try:
        from app.models.database import Deal
        
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        
        deal.status = 'passed'
        db.commit()
        
        return {"message": "Deal marked as passed", "deal_id": deal_id}
    except Exception as e:
        logger.error(f"Error passing deal {deal_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to pass deal")

async def find_and_save_deals(db: Session, search_terms: Optional[List[str]] = None):
    """Background task to find and save deals"""
    try:
        deal_finder = DealFinder(db)
        deals = deal_finder.find_deals(search_terms)
        
        saved_count = 0
        for deal_data in deals:
            try:
                deal_finder.save_deal(deal_data)
                saved_count += 1
            except Exception as e:
                logger.error(f"Error saving deal: {e}")
                continue
        
        logger.info(f"Saved {saved_count} deals to database")
    except Exception as e:
        logger.error(f"Error in background deal finding: {e}")
