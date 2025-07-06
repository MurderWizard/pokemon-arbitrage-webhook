"""
Hands-Off Automation Scheduler

This module schedules all automation jobs to run at optimal times based on 
community insights and market patterns.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
from app.core.config import settings
from app.workers.jobs import (
    hands_off_automation_job,
    find_deals_job,
    off_peak_auction_job,
    bulk_lot_analysis_job,
    update_pricing_job,
    update_inventory_aging_job,
    sync_comc_inventory_job
)

logger = logging.getLogger(__name__)

class AutomationScheduler:
    """Scheduler for hands-off automation jobs"""
    
    def __init__(self):
        self.redis_conn = Redis.from_url(settings.REDIS_URL)
        self.queue = Queue(connection=self.redis_conn)
        self.scheduler = Scheduler(queue=self.queue, connection=self.redis_conn)
        
        # Schedule configurations based on community insights
        self.schedule_config = self._get_optimal_schedule()
    
    def _get_optimal_schedule(self) -> Dict[str, Dict]:
        """Get optimal schedule configuration based on market patterns"""
        return {
            # Main automation engine - runs every 30 minutes
            'hands_off_automation': {
                'job': hands_off_automation_job,
                'interval': 30,  # minutes
                'description': 'Complete hands-off automation cycle'
            },
            
            # Enhanced deal finding - runs every 15 minutes during active hours
            'enhanced_deal_finding': {
                'job': find_deals_job,
                'interval': 15,  # minutes
                'active_hours': list(range(8, 23)),  # 8AM-11PM
                'description': 'Enhanced deal discovery with community insights'
            },
            
            # Off-peak auction scanning - runs every 10 minutes during off-peak
            'off_peak_auctions': {
                'job': off_peak_auction_job,
                'interval': 10,  # minutes
                'active_hours': list(range(0, 13)),  # Midnight-1PM
                'description': 'Off-peak auction opportunity scanning'
            },
            
            # Bulk lot analysis - runs every 2 hours
            'bulk_lot_analysis': {
                'job': bulk_lot_analysis_job,
                'interval': 120,  # minutes
                'description': 'Bulk lot opportunity analysis'
            },
            
            # Dynamic pricing updates - runs every 4 hours
            'pricing_updates': {
                'job': update_pricing_job,
                'interval': 240,  # minutes
                'description': 'Dynamic pricing and repricing updates'
            },
            
            # Inventory aging - runs daily at 6AM
            'inventory_aging': {
                'job': update_inventory_aging_job,
                'cron': '0 6 * * *',  # Daily at 6AM
                'description': 'Update inventory aging metrics'
            },
            
            # COMC sync - runs every 6 hours
            'comc_sync': {
                'job': sync_comc_inventory_job,
                'interval': 360,  # minutes
                'description': 'Sync COMC inventory and orders'
            }
        }
    
    def start_scheduler(self):
        """Start the automation scheduler"""
        logger.info("Starting hands-off automation scheduler...")
        
        # Clear existing scheduled jobs
        self.scheduler.cancel_all()
        
        # Schedule all jobs
        for job_name, config in self.schedule_config.items():
            self._schedule_job(job_name, config)
        
        logger.info(f"Scheduled {len(self.schedule_config)} automation jobs")
    
    def _schedule_job(self, job_name: str, config: Dict):
        """Schedule a specific job"""
        try:
            job_func = config['job']
            description = config['description']
            
            if 'cron' in config:
                # Schedule with cron expression
                self.scheduler.cron(
                    cron_string=config['cron'],
                    func=job_func,
                    description=description
                )
                logger.info(f"Scheduled {job_name} with cron: {config['cron']}")
                
            elif 'interval' in config:
                # Schedule with interval
                interval_seconds = config['interval'] * 60
                
                # Check if job has active hours restriction
                if 'active_hours' in config:
                    # Schedule conditional job that checks active hours
                    self.scheduler.schedule(
                        scheduled_time=datetime.now(),
                        func=self._conditional_job_wrapper,
                        args=(job_func, config['active_hours']),
                        interval=interval_seconds,
                        repeat=None,
                        description=description
                    )
                else:
                    # Schedule regular interval job
                    self.scheduler.schedule(
                        scheduled_time=datetime.now(),
                        func=job_func,
                        interval=interval_seconds,
                        repeat=None,
                        description=description
                    )
                
                logger.info(f"Scheduled {job_name} every {config['interval']} minutes")
            
        except Exception as e:
            logger.error(f"Error scheduling job {job_name}: {e}")
    
    def _conditional_job_wrapper(self, job_func, active_hours: List[int]):
        """Wrapper that only runs job during active hours"""
        current_hour = datetime.now().hour
        
        if current_hour in active_hours:
            logger.info(f"Running {job_func.__name__} during active hours")
            job_func()
        else:
            logger.debug(f"Skipping {job_func.__name__} - outside active hours")
    
    def stop_scheduler(self):
        """Stop the automation scheduler"""
        logger.info("Stopping automation scheduler...")
        self.scheduler.cancel_all()
    
    def get_scheduled_jobs(self) -> List[Dict]:
        """Get list of scheduled jobs"""
        jobs = []
        
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'func_name': job.func_name,
                'description': job.description,
                'next_run': job.get_next_run_time(),
                'interval': getattr(job, 'interval', None)
            })
        
        return jobs
    
    def add_immediate_job(self, job_name: str, priority: str = 'normal'):
        """Add an immediate job to the queue"""
        try:
            if job_name in self.schedule_config:
                job_func = self.schedule_config[job_name]['job']
                
                # Set priority
                if priority == 'high':
                    self.queue.enqueue(job_func, job_timeout='10m')
                else:
                    self.queue.enqueue(job_func, job_timeout='5m')
                
                logger.info(f"Added immediate job: {job_name}")
                return True
            else:
                logger.error(f"Unknown job name: {job_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding immediate job {job_name}: {e}")
            return False
    
    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        return {
            'queue_length': len(self.queue),
            'failed_jobs': len(self.queue.failed_job_registry),
            'scheduled_jobs': len(self.scheduler.get_jobs()),
            'workers': len(self.queue.workers)
        }

# Global scheduler instance
automation_scheduler = AutomationScheduler()

def start_hands_off_automation():
    """Start the hands-off automation system"""
    logger.info("🤖 Starting Hands-Off Automation System")
    
    # Start the scheduler
    automation_scheduler.start_scheduler()
    
    # Run initial automation cycle
    automation_scheduler.add_immediate_job('hands_off_automation', priority='high')
    
    logger.info("✅ Hands-Off Automation System started successfully")

def stop_hands_off_automation():
    """Stop the hands-off automation system"""
    logger.info("🛑 Stopping Hands-Off Automation System")
    automation_scheduler.stop_scheduler()
    logger.info("✅ Hands-Off Automation System stopped")

if __name__ == "__main__":
    # For testing - start the scheduler
    start_hands_off_automation()
    
    # Keep running
    try:
        while True:
            import time
            time.sleep(60)
    except KeyboardInterrupt:
        stop_hands_off_automation()
