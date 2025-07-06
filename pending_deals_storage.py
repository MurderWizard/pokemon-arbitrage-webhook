#!/usr/bin/env python3
"""
Shared storage for pending deals
"""
import json
import os
from typing import Dict, List
from datetime import datetime

PENDING_DEALS_FILE = "/home/jthomas4641/pokemon/pending_deals.json"

def save_pending_deal(deal_id: str, deal: Dict):
    """Save a pending deal to file"""
    try:
        # Load existing deals
        pending = load_pending_deals()
        
        # Add new deal with timestamp
        pending[deal_id] = {
            **deal,
            'added_timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # Save back to file
        with open(PENDING_DEALS_FILE, 'w') as f:
            json.dump(pending, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Error saving pending deal: {e}")
        return False

def load_pending_deals() -> Dict:
    """Load all pending deals from file"""
    try:
        if os.path.exists(PENDING_DEALS_FILE):
            with open(PENDING_DEALS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading pending deals: {e}")
        return {}

def get_pending_deal(deal_id: str) -> Dict:
    """Get specific pending deal"""
    pending = load_pending_deals()
    return pending.get(deal_id, {})

def remove_pending_deal(deal_id: str) -> bool:
    """Remove a deal from pending (after approval/rejection)"""
    try:
        pending = load_pending_deals()
        if deal_id in pending:
            del pending[deal_id]
            with open(PENDING_DEALS_FILE, 'w') as f:
                json.dump(pending, f, indent=2)
            return True
        return False
    except Exception as e:
        print(f"Error removing pending deal: {e}")
        return False

def get_latest_deal_id() -> str:
    """Get the most recently added deal ID"""
    pending = load_pending_deals()
    if not pending:
        return ""
    
    # Find most recent by timestamp
    latest = max(pending.items(), key=lambda x: x[1].get('added_timestamp', ''))
    return latest[0]

def clear_all_pending():
    """Clear all pending deals"""
    try:
        with open(PENDING_DEALS_FILE, 'w') as f:
            json.dump({}, f)
        return True
    except Exception as e:
        print(f"Error clearing pending deals: {e}")
        return False
