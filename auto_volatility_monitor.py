#!/usr/bin/env python3
"""
Automated Volatility Monitoring System

This script continuously monitors card prices, tracks volatility,
and sends alerts for significant price movements.
"""

import os
import time
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional
from price_volatility_tracker import PriceVolatilityTracker
from daily_price_updater import DailyPriceUpdater
from pokemon_price_system import price_db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VolatilityMonitor:
    """Automated price volatility monitoring system"""
    
    def __init__(self):
        self.tracker = PriceVolatilityTracker()
        self.updater = DailyPriceUpdater()
        self.last_full_scan = datetime.now()
        self.last_high_value_check = datetime.now()
        
    def monitor_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                self.check_schedule()
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(60)  # Wait a bit on error
    
    def check_schedule(self):
        """Check if any scheduled tasks need to run"""
        now = datetime.now()
        
        # Full scan every 8 hours
        if now - self.last_full_scan > timedelta(hours=8):
            self.run_full_scan()
            self.last_full_scan = now
        
        # High value cards every 2 hours  
        if now - self.last_high_value_check > timedelta(hours=2):
            self.check_high_value_cards()
            self.last_high_value_check = now
        
        # Daily morning update at 8 AM
        if now.hour == 8 and now.minute < 5:
            self.updater.morning_update()
            
        # Daily evening update at 8 PM    
        if now.hour == 20 and now.minute < 5:
            self.updater.evening_update()
    
    def run_full_scan(self):
        """Run a full scan of all cards"""
        logger.info("Starting full price scan...")
        
        # Get all cards from database
        conn = sqlite3.connect(price_db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT card_name, set_name 
            FROM card_prices
        ''')
        
        cards = cursor.fetchall()
        conn.close()
        
        logger.info(f"Scanning {len(cards)} cards...")
        for card_name, set_name in cards:
            try:
                # Analyze price movement
                movement = self.tracker.analyze_price_movement(card_name, set_name)
                if movement:
                    # Update volatility score
                    self.tracker.update_volatility_score(card_name, set_name)
                    
                    # Alert on significant movements
                    if movement.alert_level in ['medium', 'high']:
                        self.tracker.record_price_alert(movement)
                        
            except Exception as e:
                logger.error(f"Error analyzing {card_name} ({set_name}): {e}")
        
        logger.info("Full scan complete")
    
    def check_high_value_cards(self):
        """Check high value cards more frequently"""
        logger.info("Checking high-value cards...")
        self.updater.check_high_value_cards()
        
    def generate_volatility_report(self) -> Dict:
        """Generate a volatility overview report"""
        volatile_cards = self.tracker.get_volatile_cards(50)
        recent_alerts = self.tracker.get_recent_alerts(24, "medium")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'volatile_cards': len(volatile_cards),
            'recent_alerts': len(recent_alerts),
            'top_movers': volatile_cards[:5],
            'latest_alerts': recent_alerts[:5]
        }

def main():
    """Run the volatility monitoring system"""
    logger.info("Starting volatility monitoring system...")
    monitor = VolatilityMonitor()
    monitor.monitor_loop()

if __name__ == "__main__":
    main()
