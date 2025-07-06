from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.database import get_db
from app.models.schemas import InventoryItem, InventoryItemCreate, AgedInventoryItem
from app.services.pricing import PricingService
from app.models.database import InventoryItem as InventoryItemDB, Card
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[InventoryItem])
async def get_inventory(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get inventory items"""
    try:
        query = db.query(InventoryItemDB)
        
        if status:
            query = query.filter(InventoryItemDB.status == status)
        
        inventory_items = query.offset(skip).limit(limit).all()
        return inventory_items
    except Exception as e:
        logger.error(f"Error getting inventory: {e}")
        raise HTTPException(status_code=500, detail="Failed to get inventory")

@router.post("/", response_model=InventoryItem)
async def create_inventory_item(
    item: InventoryItemCreate,
    db: Session = Depends(get_db)
):
    """Create new inventory item"""
    try:
        # Check if card exists
        card = db.query(Card).filter(Card.id == item.card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # Create inventory item
        db_item = InventoryItemDB(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        return db_item
    except Exception as e:
        logger.error(f"Error creating inventory item: {e}")
        raise HTTPException(status_code=500, detail="Failed to create inventory item")

@router.get("/aged", response_model=List[AgedInventoryItem])
async def get_aged_inventory(
    days: int = 60,
    db: Session = Depends(get_db)
):
    """Get aged inventory items"""
    try:
        query = (
            db.query(InventoryItemDB)
            .join(Card)
            .filter(InventoryItemDB.days_in_stock >= days)
            .filter(InventoryItemDB.status.in_(['listed', 'processing']))
            .order_by(InventoryItemDB.days_in_stock.desc())
        )
        
        aged_items = []
        for item in query.all():
            aged_items.append(AgedInventoryItem(
                id=item.id,
                sku=item.sku,
                card_name=item.card.name,
                purchase_price=item.purchase_price,
                current_price=item.list_price,
                days_in_stock=item.days_in_stock,
                status=item.status
            ))
        
        return aged_items
    except Exception as e:
        logger.error(f"Error getting aged inventory: {e}")
        raise HTTPException(status_code=500, detail="Failed to get aged inventory")

@router.get("/stats")
async def get_inventory_stats(db: Session = Depends(get_db)):
    """Get inventory statistics"""
    try:
        total_items = db.query(InventoryItemDB).count()
        
        # Get items by status
        stats_by_status = {}
        for status in ['purchased', 'in_transit', 'processing', 'listed', 'sold']:
            count = db.query(InventoryItemDB).filter(
                InventoryItemDB.status == status
            ).count()
            stats_by_status[status] = count
        
        # Get total inventory value
        total_value = db.query(
            db.func.sum(InventoryItemDB.purchase_price)
        ).scalar() or 0
        
        # Get average days in stock
        avg_days = db.query(
            db.func.avg(InventoryItemDB.days_in_stock)
        ).scalar() or 0
        
        return {
            "total_items": total_items,
            "stats_by_status": stats_by_status,
            "total_inventory_value": float(total_value),
            "average_days_in_stock": float(avg_days)
        }
    except Exception as e:
        logger.error(f"Error getting inventory stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get inventory statistics")

@router.put("/{item_id}/price")
async def update_item_price(
    item_id: int,
    price: float,
    db: Session = Depends(get_db)
):
    """Update price for inventory item"""
    try:
        item = db.query(InventoryItemDB).filter(InventoryItemDB.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        
        item.list_price = price
        db.commit()
        
        return {"message": "Price updated successfully", "item_id": item_id, "new_price": price}
    except Exception as e:
        logger.error(f"Error updating item price: {e}")
        raise HTTPException(status_code=500, detail="Failed to update item price")

@router.post("/{item_id}/mark-sold")
async def mark_item_sold(
    item_id: int,
    sale_price: float,
    platform: str,
    db: Session = Depends(get_db)
):
    """Mark inventory item as sold"""
    try:
        item = db.query(InventoryItemDB).filter(InventoryItemDB.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        
        # Update item status
        item.status = 'sold'
        db.commit()
        
        # TODO: Create sale record
        
        return {"message": "Item marked as sold", "item_id": item_id}
    except Exception as e:
        logger.error(f"Error marking item as sold: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark item as sold")

@router.post("/reprice")
async def run_repricing(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run repricing for all inventory"""
    try:
        background_tasks.add_task(run_repricing_task, db)
        return {"message": "Repricing started", "status": "processing"}
    except Exception as e:
        logger.error(f"Error starting repricing: {e}")
        raise HTTPException(status_code=500, detail="Failed to start repricing")

async def run_repricing_task(db: Session):
    """Background task to run repricing"""
    try:
        pricing_service = PricingService(db)
        results = pricing_service.run_repricing()
        logger.info(f"Repricing completed: {results}")
    except Exception as e:
        logger.error(f"Error in repricing task: {e}")
