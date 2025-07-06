#!/usr/bin/env python3
"""
Deal Logger - Track all potential deals for analysis
"""
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DealLogger:
    """Log and analyze potential deals"""
    
    def __init__(self, db_path: str = "deals.db"):
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Deals table - track everything we find
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                card_name TEXT NOT NULL,
                set_name TEXT NOT NULL,
                raw_price FLOAT NOT NULL,
                estimated_psa10_price FLOAT NOT NULL,
                potential_profit FLOAT NOT NULL,
                profit_margin FLOAT NOT NULL,
                monthly_sales INTEGER,
                price_stability FLOAT,
                population_psa10 INTEGER,
                condition_notes TEXT,
                listing_url TEXT,
                alert_sent BOOLEAN DEFAULT FALSE,
                high_priority BOOLEAN DEFAULT FALSE,
                status TEXT DEFAULT 'new',
                details TEXT
            )
        ''')
        
        # Deal outcomes - track what happened
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outcomes (
                deal_id INTEGER PRIMARY KEY,
                purchased BOOLEAN,
                purchase_date DATETIME,
                grading_sent_date DATETIME,
                grade_received TEXT,
                final_sale_price FLOAT,
                actual_profit FLOAT,
                actual_roi FLOAT,
                time_to_sale INTEGER,
                notes TEXT,
                FOREIGN KEY(deal_id) REFERENCES deals(id)
            )
        ''')
        
        # High-value deal metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS high_value_metrics (
                deal_id INTEGER PRIMARY KEY,
                price_trend_30d FLOAT,
                sales_velocity_30d INTEGER,
                market_competition INTEGER,
                price_volatility FLOAT,
                last_updated DATETIME,
                FOREIGN KEY(deal_id) REFERENCES deals(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def log_deal(self, deal: Dict) -> int:
        """Log a new potential deal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO deals (
                timestamp, card_name, set_name, raw_price,
                estimated_psa10_price, potential_profit, profit_margin,
                condition_notes, listing_url, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            deal['card_name'],
            deal.get('set_name', 'Unknown'),
            deal['raw_price'],
            deal['estimated_psa10_price'],
            deal['potential_profit'],
            deal['profit_margin'],
            deal.get('condition_notes', ''),
            deal.get('listing_url', ''),
            json.dumps(deal)
        ))
        
        deal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Logged deal {deal_id}: {deal['card_name']} - ${deal['raw_price']:.2f}")
        return deal_id
    
    def mark_alert_sent(self, deal_id: int):
        """Mark that we've sent an alert for this deal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE deals 
            SET alert_sent = TRUE 
            WHERE id = ?
        ''', (deal_id,))
        
        conn.commit()
        conn.close()
    
    def update_status(self, deal_id: int, status: str):
        """Update deal status (new, investigating, purchased, passed, etc)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE deals 
            SET status = ? 
            WHERE id = ?
        ''', (status, deal_id))
        
        conn.commit()
        conn.close()
    
    def log_outcome(self, deal_id: int, outcome: Dict):
        """Log what happened with a deal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO outcomes (
                deal_id, purchased, purchase_date,
                grading_sent_date, grade_received,
                final_sale_price, actual_profit, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            deal_id,
            outcome.get('purchased', False),
            outcome.get('purchase_date'),
            outcome.get('grading_sent_date'),
            outcome.get('grade_received'),
            outcome.get('final_sale_price'),
            outcome.get('actual_profit'),
            outcome.get('notes', '')
        ))
        
        conn.commit()
        conn.close()
    
    def get_daily_summary(self) -> Dict:
        """Get summary of today's deals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_deals,
                AVG(profit_margin) as avg_margin,
                MIN(raw_price) as min_price,
                MAX(raw_price) as max_price,
                COUNT(CASE WHEN profit_margin >= 0.35 THEN 1 END) as good_deals
            FROM deals
            WHERE date(timestamp) = date('now')
        ''')
        
        row = cursor.fetchone()
        
        summary = {
            'date': datetime.now().date().isoformat(),
            'total_deals': row[0],
            'avg_margin': row[1] * 100 if row[1] else 0,  # Convert to percentage
            'price_range': f"${row[2]:.2f} - ${row[3]:.2f}" if row[2] and row[3] else "N/A",
            'good_deals': row[4]
        }
        
        conn.close()
        return summary
    
    def analyze_profits(self, days: int = 30) -> Dict:
        """Analyze profit performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                AVG(CASE WHEN o.actual_profit IS NOT NULL 
                    THEN (o.actual_profit / d.raw_price) 
                    ELSE NULL END) as avg_roi,
                COUNT(CASE WHEN o.purchased = TRUE THEN 1 END) as purchases,
                AVG(CASE WHEN o.final_sale_price IS NOT NULL 
                    THEN o.final_sale_price / d.estimated_psa10_price 
                    ELSE NULL END) as price_prediction_accuracy
            FROM deals d
            LEFT JOIN outcomes o ON d.id = o.deal_id
            WHERE d.timestamp >= date('now', ?)
        ''', (f'-{days} days',))
        
        row = cursor.fetchone()
        
        analysis = {
            'period_days': days,
            'avg_roi': row[0] * 100 if row[0] else 0,  # Convert to percentage
            'total_purchases': row[1] or 0,
            'price_prediction_accuracy': row[2] * 100 if row[2] else 0  # Convert to percentage
        }
        
        conn.close()
        return analysis
    
    def log_high_value_deal(self, deal: Dict) -> int:
        """Log a new high-value deal ($250+) with enhanced metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO deals (
                    timestamp, card_name, set_name, raw_price,
                    estimated_psa10_price, potential_profit, profit_margin,
                    monthly_sales, price_stability, population_psa10,
                    condition_notes, listing_url, high_priority, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                deal['card_name'],
                deal.get('set_name', 'Unknown'),
                deal['raw_price'],
                deal['estimated_psa10_price'],
                deal['potential_profit'],
                deal['profit_margin'],
                deal.get('monthly_sales', 0),
                deal.get('price_stability', 0.0),
                deal.get('population_psa10', 0),
                deal.get('condition_notes', ''),
                deal.get('listing_url', ''),
                deal['raw_price'] >= 250.0,  # High priority for $250+
                json.dumps(deal)
            ))
            
            deal_id = cursor.lastrowid
            
            # Add high-value metrics if available
            if 'price_trend_30d' in deal or 'sales_velocity_30d' in deal:
                cursor.execute('''
                    INSERT INTO high_value_metrics (
                        deal_id, price_trend_30d, sales_velocity_30d,
                        market_competition, price_volatility, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    deal_id,
                    deal.get('price_trend_30d', 0.0),
                    deal.get('sales_velocity_30d', 0),
                    deal.get('market_competition', 0),
                    deal.get('price_volatility', 0.0),
                    datetime.now()
                ))
            
            conn.commit()
            logger.info(f"Logged high-value deal {deal_id}: {deal['card_name']} - ${deal['raw_price']:.2f}")
            return deal_id
            
        except Exception as e:
            logger.error(f"Error logging high-value deal: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_high_value_deals(self, min_price: float = 250.0, limit: int = 50) -> List[Dict]:
        """Get recent high-value deals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, hvm.* 
            FROM deals d
            LEFT JOIN high_value_metrics hvm ON d.id = hvm.deal_id
            WHERE d.raw_price >= ?
            ORDER BY d.timestamp DESC
            LIMIT ?
        ''', (min_price, limit))
        
        columns = [desc[0] for desc in cursor.description]
        deals = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return deals
        
    def get_deal_stats(self, min_price: float = 250.0, days: int = 30) -> Dict:
        """Get statistics about high-value deals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff = cutoff - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_deals,
                AVG(potential_profit) as avg_potential_profit,
                AVG(profit_margin) as avg_profit_margin,
                SUM(CASE WHEN status = 'purchased' THEN 1 ELSE 0 END) as purchased_count
            FROM deals
            WHERE raw_price >= ?
            AND timestamp >= ?
        ''', (min_price, cutoff))
        
        stats = dict(cursor.fetchone())
        
        # Get outcome stats
        cursor.execute('''
            SELECT 
                AVG(actual_profit) as avg_actual_profit,
                AVG(actual_roi) as avg_actual_roi,
                AVG(time_to_sale) as avg_time_to_sale
            FROM outcomes o
            JOIN deals d ON o.deal_id = d.id
            WHERE d.raw_price >= ?
            AND d.timestamp >= ?
            AND o.final_sale_price IS NOT NULL
        ''', (min_price, cutoff))
        
        stats.update(dict(cursor.fetchone()))
        conn.close()
        
        return stats
    
    def update_deal_status(self, deal_id: str, status: str, notes: str = ""):
        """Update deal status (APPROVED, REJECTED, PURCHASED, etc.)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE deals 
                SET status = ?, 
                    details = COALESCE(details, '') || ? || char(10)
                WHERE id = ?
            ''', (status, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {status} - {notes}", deal_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated deal {deal_id} status to {status}")
            
        except Exception as e:
            logger.error(f"Failed to update deal status: {e}")

    def get_deal_status(self, deal_id: str) -> Optional[str]:
        """Get current status of a deal"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT status FROM deals WHERE id = ?', (deal_id,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Failed to get deal status: {e}")
            return None

if __name__ == "__main__":
    # Test the logger
    logger = DealLogger()
    
    # Log a test deal
    test_deal = {
        'card_name': "Charizard VMAX",
        'set_name': "Champions Path",
        'raw_price': 280.00,
        'estimated_psa10_price': 450.00,
        'potential_profit': 170.00,
        'profit_margin': 0.38,
        'condition_notes': "Pack fresh, centered",
        'listing_url': "https://www.ebay.com/itm/1234567890",
        'monthly_sales': 10,
        'price_stability': 0.95,
        'population_psa10': 1500,
        'sales_velocity_30d': 5,
        'market_competition': 3,
        'price_volatility': 0.1
    }
    
    deal_id = logger.log_high_value_deal(test_deal)
    print(f"Test deal logged with ID: {deal_id}")
    
    # Get daily summary
    summary = logger.get_daily_summary()
    print("Daily Summary:", summary)
    
    # Analyze profits
    profit_analysis = logger.analyze_profits(30)
    print("Profit Analysis (last 30 days):", profit_analysis)
    
    # Get high-value deals
    high_value_deals = logger.get_high_value_deals(250, 5)
    print("High-Value Deals:", high_value_deals)
    
    # Get deal stats
    deal_stats = logger.get_deal_stats(250, 30)
    print("Deal Stats (last 30 days):", deal_stats)
