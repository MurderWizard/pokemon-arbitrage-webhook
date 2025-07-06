import schedule
import time
import logging
from rq import Queue
from app.workers.main import redis_conn
from app.workers.jobs import (
    find_deals_job,
    update_pricing_job,
    update_inventory_aging_job,
    sync_comc_inventory_job,
    send_daily_summary_job
)

logger = logging.getLogger(__name__)

# Initialize queues
deal_queue = Queue('deals', connection=redis_conn)
pricing_queue = Queue('pricing', connection=redis_conn)
general_queue = Queue('general', connection=redis_conn)

def schedule_jobs():
    """Schedule recurring jobs"""
    
    # Deal finding - every 5 minutes
    schedule.every(5).minutes.do(
        lambda: deal_queue.enqueue(find_deals_job)
    )
    
    # Price updates - every hour
    schedule.every().hour.do(
        lambda: pricing_queue.enqueue(update_pricing_job)
    )
    
    # Inventory aging update - daily at 1 AM
    schedule.every().day.at("01:00").do(
        lambda: general_queue.enqueue(update_inventory_aging_job)
    )
    
    # COMC inventory sync - daily at 2 AM
    schedule.every().day.at("02:00").do(
        lambda: general_queue.enqueue(sync_comc_inventory_job)
    )
    
    # Daily summary - daily at 11 PM
    schedule.every().day.at("23:00").do(
        lambda: general_queue.enqueue(send_daily_summary_job)
    )
    
    # Repricing - daily at 11:30 PM
    schedule.every().day.at("23:30").do(
        lambda: pricing_queue.enqueue(update_pricing_job)
    )

def main():
    """Main scheduler process"""
    logger.info("Starting job scheduler...")
    
    schedule_jobs()
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    main()
