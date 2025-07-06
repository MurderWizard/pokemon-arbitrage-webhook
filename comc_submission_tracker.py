#!/usr/bin/env python3
"""
COMC Submission Tracker
Track and manage COMC card submissions
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class COMCSubmission:
    submission_id: str
    date_sent: str
    tracking_number: str
    num_cards: int
    processing_type: str
    total_cost: float
    insurance_value: float
    expected_completion: str
    status: str = "Shipped"
    notes: str = ""
    
class COMCSubmissionTracker:
    def __init__(self, db_path: str = "comc_submissions.db"):
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Create submissions tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                submission_id TEXT PRIMARY KEY,
                date_sent TEXT,
                tracking_number TEXT,
                num_cards INTEGER,
                processing_type TEXT,
                total_cost REAL,
                insurance_value REAL,
                expected_completion TEXT,
                status TEXT,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submission_cards (
                card_id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id TEXT,
                card_name TEXT,
                set_name TEXT,
                condition TEXT,
                estimated_value REAL,
                notes TEXT,
                FOREIGN KEY(submission_id) REFERENCES submissions(submission_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_submission(self, submission: COMCSubmission) -> bool:
        """Add a new submission to tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO submissions (
                    submission_id, date_sent, tracking_number, num_cards,
                    processing_type, total_cost, insurance_value,
                    expected_completion, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                submission.submission_id,
                submission.date_sent,
                submission.tracking_number,
                submission.num_cards,
                submission.processing_type,
                submission.total_cost,
                submission.insurance_value,
                submission.expected_completion,
                submission.status,
                submission.notes
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding submission: {e}")
            return False
            
    def add_card_to_submission(self, 
                             submission_id: str,
                             card_name: str,
                             set_name: str,
                             condition: str,
                             estimated_value: float,
                             notes: str = "") -> bool:
        """Add a card to a submission"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO submission_cards (
                    submission_id, card_name, set_name,
                    condition, estimated_value, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                submission_id,
                card_name,
                set_name,
                condition,
                estimated_value,
                notes
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding card to submission: {e}")
            return False
            
    def update_submission_status(self, 
                               submission_id: str,
                               status: str,
                               notes: str = "") -> bool:
        """Update submission status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE submissions 
                SET status = ?, notes = ?
                WHERE submission_id = ?
            ''', (status, notes, submission_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating submission status: {e}")
            return False
            
    def get_submission_details(self, submission_id: str) -> Dict:
        """Get full details of a submission including cards"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get submission info
        cursor.execute('SELECT * FROM submissions WHERE submission_id = ?', 
                      (submission_id,))
        submission = cursor.fetchone()
        
        if not submission:
            conn.close()
            return None
            
        # Get cards in submission
        cursor.execute('''
            SELECT card_name, set_name, condition, estimated_value, notes
            FROM submission_cards
            WHERE submission_id = ?
        ''', (submission_id,))
        cards = cursor.fetchall()
        
        conn.close()
        
        return {
            'submission_id': submission[0],
            'date_sent': submission[1],
            'tracking_number': submission[2],
            'num_cards': submission[3],
            'processing_type': submission[4],
            'total_cost': submission[5],
            'insurance_value': submission[6],
            'expected_completion': submission[7],
            'status': submission[8],
            'notes': submission[9],
            'cards': [{
                'name': card[0],
                'set': card[1],
                'condition': card[2],
                'value': card[3],
                'notes': card[4]
            } for card in cards]
        }
        
    def get_active_submissions(self) -> List[Dict]:
        """Get all active (non-completed) submissions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT submission_id, date_sent, status, num_cards,
                   processing_type, expected_completion
            FROM submissions
            WHERE status != 'Completed'
            ORDER BY date_sent DESC
        ''')
        
        submissions = [{
            'submission_id': row[0],
            'date_sent': row[1],
            'status': row[2],
            'num_cards': row[3],
            'processing_type': row[4],
            'expected_completion': row[5]
        } for row in cursor.fetchall()]
        
        conn.close()
        return submissions

def test_submission_tracker():
    """Test the submission tracking system"""
    print("📦 Testing COMC Submission Tracker")
    print("=" * 60)
    
    tracker = COMCSubmissionTracker()
    
    # Test submission
    test_sub = COMCSubmission(
        submission_id="TEST-001",
        date_sent="2025-07-04",
        tracking_number="USPS12345",
        num_cards=50,
        processing_type="Basic",
        total_cost=25.00,
        insurance_value=500.00,
        expected_completion="2025-08-15",
        status="Shipped",
        notes="Test submission"
    )
    
    # Add submission
    if tracker.add_submission(test_sub):
        print("✅ Added test submission")
        
    # Add some cards
    test_cards = [
        ("Charizard VMAX", "Champions Path", "NM", 85.00),
        ("Pikachu V", "Vivid Voltage", "NM", 25.00),
        ("Lugia V", "Silver Tempest", "NM", 80.00)
    ]
    
    for card_name, set_name, condition, value in test_cards:
        if tracker.add_card_to_submission(
            test_sub.submission_id,
            card_name,
            set_name,
            condition,
            value
        ):
            print(f"✅ Added {card_name} to submission")
            
    # Get submission details
    details = tracker.get_submission_details(test_sub.submission_id)
    if details:
        print("\n📦 Submission Details:")
        print(f"ID: {details['submission_id']}")
        print(f"Status: {details['status']}")
        print(f"Cards: {len(details['cards'])}")
        print("\nCard List:")
        for card in details['cards']:
            print(f"  • {card['name']} ({card['set']}) - ${card['value']:.2f}")

if __name__ == "__main__":
    test_submission_tracker()
