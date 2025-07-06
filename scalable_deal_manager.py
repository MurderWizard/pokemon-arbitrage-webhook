#!/usr/bin/env python3
"""
Scalable Deal Manager - Supports multiple deals as capital grows
Manual approval gates prevent overextension
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from smart_mvp_bot_fixed import send_smart_deal_alert, send_session_summary

class ScalableDealManager:
    """Deal manager that scales with available capital"""
    
    def __init__(self):
        self.deals_log_file = "scalable_deal_log.json"
        self.active_deals_file = "active_deals.json"
        self.config_file = "deal_config.json"
        self.load_config()
        
    def load_config(self):
        """Load deal management configuration"""
        default_config = {
            'max_concurrent_deals': 1,  # Start with 1, increase as capital grows
            'max_total_exposure': 1000.0,  # Maximum capital at risk
            'min_deal_roi': 200.0,  # Minimum 200% ROI
            'preferred_cards': ['Charizard', 'Blastoise', 'Venusaur', 'Pikachu'],
            'capital_allocation': {
                'per_deal_limit': 500.0,  # Max per single deal
                'reserve_cash': 200.0,     # Always keep in reserve
                'total_available': 1200.0  # Total capital available
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                self.save_config()
        except Exception:
            self.config = default_config
    
    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save config: {e}")
    
    def can_approve_new_deal(self, deal_amount: float) -> tuple[bool, str]:
        """Check if we can approve a new deal based on capital limits"""
        active_deals = self.load_active_deals()
        
        # Count active and pending deals
        active_count = len([d for d in active_deals if d['status'] in ['approved', 'pending_approval']])
        total_exposure = sum(d.get('investment_amount', 0) for d in active_deals if d['status'] == 'approved')
        
        # Check concurrent deal limit
        if active_count >= self.config['max_concurrent_deals']:
            return False, f"Already have {active_count}/{self.config['max_concurrent_deals']} active deals"
        
        # Check total exposure limit
        new_total_exposure = total_exposure + deal_amount
        if new_total_exposure > self.config['max_total_exposure']:
            return False, f"Would exceed exposure limit: ${new_total_exposure:.0f} > ${self.config['max_total_exposure']:.0f}"
        
        # Check per-deal limit
        if deal_amount > self.config['capital_allocation']['per_deal_limit']:
            return False, f"Deal too large: ${deal_amount:.0f} > ${self.config['capital_allocation']['per_deal_limit']:.0f}"
        
        # Check available capital
        available = self.config['capital_allocation']['total_available'] - total_exposure - self.config['capital_allocation']['reserve_cash']
        if deal_amount > available:
            return False, f"Insufficient capital: ${deal_amount:.0f} needed, ${available:.0f} available"
        
        return True, f"Can approve: ${deal_amount:.0f} within limits"
    
    def get_capital_status(self) -> Dict:
        """Get current capital allocation status"""
        active_deals = self.load_active_deals()
        approved_deals = [d for d in active_deals if d['status'] == 'approved']
        pending_deals = [d for d in active_deals if d['status'] == 'pending_approval']
        
        total_exposure = sum(d.get('investment_amount', 0) for d in approved_deals)
        pending_exposure = sum(d.get('investment_amount', 0) for d in pending_deals)
        
        available = (self.config['capital_allocation']['total_available'] - 
                    total_exposure - 
                    self.config['capital_allocation']['reserve_cash'])
        
        return {
            'total_available': self.config['capital_allocation']['total_available'],
            'active_exposure': total_exposure,
            'pending_exposure': pending_exposure,
            'reserve_cash': self.config['capital_allocation']['reserve_cash'],
            'available_for_new_deals': available,
            'active_deal_count': len(approved_deals),
            'pending_deal_count': len(pending_deals),
            'max_concurrent': self.config['max_concurrent_deals'],
            'utilization_pct': (total_exposure / self.config['max_total_exposure']) * 100
        }
    
    def update_capital_limits(self, new_total: float = None, new_max_deals: int = None):
        """Update capital limits as your bankroll grows"""
        if new_total:
            self.config['capital_allocation']['total_available'] = new_total
            self.config['max_total_exposure'] = new_total * 0.8  # 80% max exposure
            print(f"✅ Updated total capital to ${new_total:.0f}")
        
        if new_max_deals:
            self.config['max_concurrent_deals'] = new_max_deals
            print(f"✅ Updated max concurrent deals to {new_max_deals}")
        
        self.save_config()
    
    def load_active_deals(self) -> List[Dict]:
        """Load current active deals"""
        try:
            if os.path.exists(self.active_deals_file):
                with open(self.active_deals_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading active deals: {e}")
        return []
    
    def save_active_deals(self, deals: List[Dict]) -> bool:
        """Save active deals list"""
        try:
            with open(self.active_deals_file, 'w') as f:
                json.dump(deals, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving active deals: {e}")
            return False
    
    async def send_capital_status_alert(self):
        """Send capital management status to Telegram"""
        status = self.get_capital_status()
        
        message = f"""💼 *CAPITAL MANAGEMENT STATUS*

💰 *Current Allocation:*
• Total Available: ${status['total_available']:.0f}
• Active Exposure: ${status['active_exposure']:.0f}
• Pending Deals: ${status['pending_exposure']:.0f}
• Reserve Cash: ${status['reserve_cash']:.0f}
• Available: ${status['available_for_new_deals']:.0f}

📊 *Deal Capacity:*
• Active Deals: {status['active_deal_count']}/{status['max_concurrent']}
• Utilization: {status['utilization_pct']:.1f}%

🎯 *Strategy: Scale Responsibly*
Manual approval prevents overextension"""

        try:
            from smart_mvp_bot_fixed import _smart_bot
            if _smart_bot:
                await _smart_bot.bot.send_message(
                    chat_id=_smart_bot.admin_id,
                    text=message,
                    parse_mode='Markdown'
                )
                return True
        except Exception as e:
            print(f"⚠️ Could not send capital status: {e}")
        return False

# CLI interface for capital management
async def manage_capital():
    """Capital management CLI"""
    manager = ScalableDealManager()
    
    print("💼 Scalable Capital Management")
    print("=" * 35)
    
    # Show current status
    status = manager.get_capital_status()
    print(f"💰 Current Status:")
    print(f"   Total Available: ${status['total_available']:.0f}")
    print(f"   Active Exposure: ${status['active_exposure']:.0f}")
    print(f"   Available for New: ${status['available_for_new_deals']:.0f}")
    print(f"   Active Deals: {status['active_deal_count']}/{status['max_concurrent']}")
    print(f"   Utilization: {status['utilization_pct']:.1f}%")
    print()
    
    print("Actions:")
    print("1. Update total capital")
    print("2. Update max concurrent deals")
    print("3. Test deal approval")
    print("4. Send status to Telegram")
    print("5. Show configuration")
    
    choice = input("Choose action (1-5): ").strip()
    
    if choice == "1":
        try:
            new_total = float(input("Enter new total capital: $").strip())
            manager.update_capital_limits(new_total=new_total)
        except ValueError:
            print("❌ Invalid amount")
    
    elif choice == "2":
        try:
            new_max = int(input("Enter new max concurrent deals: ").strip())
            manager.update_capital_limits(new_max_deals=new_max)
        except ValueError:
            print("❌ Invalid number")
    
    elif choice == "3":
        try:
            test_amount = float(input("Enter deal amount to test: $").strip())
            can_approve, message = manager.can_approve_new_deal(test_amount)
            print(f"{'✅' if can_approve else '❌'} {message}")
        except ValueError:
            print("❌ Invalid amount")
    
    elif choice == "4":
        await manager.send_capital_status_alert()
        print("✅ Status sent to Telegram")
    
    elif choice == "5":
        print("\n📋 Current Configuration:")
        print(json.dumps(manager.config, indent=2))

if __name__ == "__main__":
    asyncio.run(manage_capital())
