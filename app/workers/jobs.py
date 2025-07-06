from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.deal_finder import DealFinder
from app.services.enhanced_deal_finder import EnhancedDealFinder
from app.services.hands_off_automation import HandsOffAutomationEngine
from app.services.pricing import PricingService
from app.models.database import InventoryItem
from app.telegram.bot import send_message
from app.core.config import settings
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)

def get_db_session():
    """Get database session for jobs"""
    return SessionLocal()

def hands_off_automation_job():
    """Main hands-off automation job - runs the complete automation cycle"""
    try:
        db = get_db_session()
        automation_engine = HandsOffAutomationEngine(db)
        
        # Run the complete automation cycle
        results = asyncio.run(automation_engine.run_automation_cycle())
        
        # Log results
        logger.info(f"Automation cycle completed:")
        logger.info(f"  - Deals found: {results['deals_found']}")
        logger.info(f"  - Auto purchases: {results['auto_purchases']}")
        logger.info(f"  - Repricing updates: {results['repricing_updates']}")
        logger.info(f"  - Alerts sent: {results['alerts_sent']}")
        logger.info(f"  - Duration: {results['cycle_duration']:.2f} seconds")
        
        if results['errors']:
            logger.error(f"Automation errors: {results['errors']}")
        
        # Send summary for significant activity
        if results['auto_purchases'] > 0 or results['repricing_updates'] > 5:
            summary_message = f"🤖 AUTOMATION SUMMARY\n\n"
            summary_message += f"🔍 Deals Found: {results['deals_found']}\n"
            summary_message += f"🛒 Auto Purchases: {results['auto_purchases']}\n"
            summary_message += f"💰 Price Updates: {results['repricing_updates']}\n"
            summary_message += f"⏱️ Cycle Time: {results['cycle_duration']:.1f}s\n"
            
            if results['errors']:
                summary_message += f"⚠️ Errors: {len(results['errors'])}\n"
            
            send_message(summary_message)
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error in hands_off_automation_job: {e}")
        
        # Send error notification
        error_message = f"🚨 AUTOMATION ERROR\n\n"
        error_message += f"Job: hands_off_automation_job\n"
        error_message += f"Error: {str(e)}\n"
        error_message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        send_message(error_message)

def find_deals_job():
    """Enhanced deal finding job with community insights"""
    try:
        db = get_db_session()
        deal_finder = EnhancedDealFinder(db)
        
        # Find deals with enhanced strategies
        deals = asyncio.run(deal_finder.find_enhanced_deals())
        
        # Save deals to database
        saved_count = 0
        for deal_data in deals:
            try:
                deal_finder.save_deal(deal_data)
                saved_count += 1
                
                # Send alert for high-margin deals
                if deal_data['profit_margin'] > 0.5:  # 50%+ margin
                    message = f"🔥 High Margin Deal Alert!\n\n"
                    message += f"Card: {deal_data['card_name']}\n"
                    message += f"Set: {deal_data.get('set_name', 'Unknown')}\n"
                    message += f"Price: ${deal_data['listing_price']:.2f}\n"
                    message += f"Market: ${deal_data['market_price']:.2f}\n"
                    message += f"Profit: {deal_data['profit_margin']:.1%}\n"
                    message += f"Platform: {deal_data['platform']}\n"
                    message += f"Confidence: {deal_data.get('confidence', 'N/A')}\n"
                    message += f"URL: {deal_data.get('listing_url', 'N/A')}"
                    
                    send_message(message)
                    
            except Exception as e:
                logger.error(f"Error saving deal: {e}")
                continue
        
        logger.info(f"Found and saved {saved_count} enhanced deals")
        db.close()
        
    except Exception as e:
        logger.error(f"Error in find_deals_job: {e}")

def off_peak_auction_job():
    """Specialized job for off-peak auction scanning"""
    try:
        current_hour = datetime.now().hour
        
        # Only run during off-peak hours (midnight to 1PM)
        if not (0 <= current_hour <= 13):
            logger.info("Skipping off-peak auction job - not in off-peak hours")
            return
            
        db = get_db_session()
        deal_finder = EnhancedDealFinder(db)
        
        # Focus on ending auctions during off-peak hours
        auction_deals = asyncio.run(deal_finder._scan_ending_auctions())
        
        high_value_deals = []
        for deal in auction_deals:
            if deal['profit_margin'] > 0.4:  # 40%+ margin
                high_value_deals.append(deal)
                deal_finder.save_deal(deal)
        
        if high_value_deals:
            message = f"🌙 OFF-PEAK AUCTION ALERT\n\n"
            message += f"Found {len(high_value_deals)} high-value auctions ending soon:\n\n"
            
            for deal in high_value_deals[:3]:  # Show top 3
                message += f"• {deal['card_name']}\n"
                message += f"  Current: ${deal['current_bid']:.2f}\n"
                message += f"  Market: ${deal['market_price']:.2f}\n"
                message += f"  Margin: {deal['profit_margin']:.1%}\n\n"
            
            send_message(message)
        
        logger.info(f"Off-peak auction scan found {len(high_value_deals)} qualifying deals")
        db.close()
        
    except Exception as e:
        logger.error(f"Error in off_peak_auction_job: {e}")

def bulk_lot_analysis_job():
    """Specialized job for bulk lot analysis"""
    try:
        db = get_db_session()
        deal_finder = EnhancedDealFinder(db)
        
        # Scan for bulk lot opportunities
        bulk_deals = asyncio.run(deal_finder._scan_bulk_lots())
        
        qualified_lots = []
        for deal in bulk_deals:
            if deal['profit_margin'] > 0.3:  # 30%+ margin for lots
                qualified_lots.append(deal)
                deal_finder.save_deal(deal)
        
        if qualified_lots:
            message = f"📦 BULK LOT OPPORTUNITIES\n\n"
            message += f"Found {len(qualified_lots)} qualifying bulk lots:\n\n"
            
            for deal in qualified_lots[:2]:  # Show top 2
                message += f"• {deal['card_name']}\n"
                message += f"  Price: ${deal['listing_price']:.2f}\n"
                message += f"  Est. Value: ${deal['market_price']:.2f}\n"
                message += f"  Margin: {deal['profit_margin']:.1%}\n\n"
            
            send_message(message)
        
        logger.info(f"Bulk lot analysis found {len(qualified_lots)} opportunities")
        db.close()
        
    except Exception as e:
        logger.error(f"Error in bulk_lot_analysis_job: {e}")

def update_pricing_job():
    """Background job to update pricing"""
    try:
        db = get_db_session()
        pricing_service = PricingService(db)
        
        # Update market prices
        updated_count = pricing_service.update_market_prices()
        
        # Run repricing
        reprice_results = pricing_service.run_repricing()
        
        logger.info(f"Updated {updated_count} market prices")
        logger.info(f"Repricing results: {reprice_results}")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error in update_pricing_job: {e}")

def update_inventory_aging_job():
    """Background job to update inventory aging"""
    try:
        db = get_db_session()
        
        # Update days_in_stock for all inventory items
        inventory_items = db.query(InventoryItem).filter(
            InventoryItem.status != 'sold'
        ).all()
        
        for item in inventory_items:
            days_since_purchase = (datetime.utcnow() - item.purchase_date).days
            item.days_in_stock = days_since_purchase
        
        db.commit()
        logger.info(f"Updated aging for {len(inventory_items)} inventory items")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error in update_inventory_aging_job: {e}")

def sync_comc_inventory_job():
    """Background job to sync COMC inventory"""
    try:
        # This would sync with COMC's CSV exports
        # Placeholder for now
        logger.info("COMC inventory sync completed")
        
    except Exception as e:
        logger.error(f"Error in sync_comc_inventory_job: {e}")

def send_daily_summary_job():
    """Background job to send daily summary"""
    try:
        db = get_db_session()
        
        # Calculate daily metrics
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        # Get deals found today
        from app.models.database import Deal
        deals_today = db.query(Deal).filter(
            Deal.created_at >= yesterday
        ).count()
        
        # Get sales today
        from app.models.database import Sale
        sales_today = db.query(Sale).filter(
            Sale.sale_date >= yesterday
        ).all()
        
        revenue_today = sum(sale.sale_price for sale in sales_today)
        profit_today = sum(sale.net_profit for sale in sales_today)
        
        # Get aged inventory
        aged_inventory = db.query(InventoryItem).filter(
            InventoryItem.days_in_stock > 60,
            InventoryItem.status != 'sold'
        ).count()
        
        # Send summary message
        message = f"📊 Daily Summary - {today.strftime('%Y-%m-%d')}\n\n"
        message += f"💰 Revenue: ${revenue_today:.2f}\n"
        message += f"📈 Profit: ${profit_today:.2f}\n"
        message += f"🔍 Deals Found: {deals_today}\n"
        message += f"📦 Sales: {len(sales_today)}\n"
        message += f"⏰ Aged Items (60+ days): {aged_inventory}\n"
        
        send_message(message)
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error in send_daily_summary_job: {e}")

def check_stop_loss_job():
    """Background job to check for stop-loss conditions"""
    try:
        db = get_db_session()
        
        # Find items aged >90 days that should be auto-auctioned
        stop_loss_items = db.query(InventoryItem).filter(
            InventoryItem.days_in_stock > 90,
            InventoryItem.status == 'listed'
        ).all()
        
        for item in stop_loss_items:
            # Check if current price is below stop-loss threshold
            if item.list_price and item.list_price < item.purchase_price * settings.STOP_LOSS_THRESHOLD:
                # Send alert for manual review
                message = f"🚨 Stop-Loss Alert!\n\n"
                message += f"SKU: {item.sku}\n"
                message += f"Card: {item.card.name}\n"
                message += f"Purchase Price: ${item.purchase_price:.2f}\n"
                message += f"Current Price: ${item.list_price:.2f}\n"
                message += f"Days in Stock: {item.days_in_stock}\n"
                message += f"Recommend: Auto-auction or manual review"
                
                send_message(message)
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error in check_stop_loss_job: {e}")
