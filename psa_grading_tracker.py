#!/usr/bin/env python3
"""
PSA Grading Tracker & Vault Manager
Tracks cards through grading → vault → automatic sell orders
"""
import os
import json
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class DealStatus(Enum):
    PENDING = "pending_approval"
    APPROVED = "approved" 
    PURCHASED = "purchased"
    SHIPPED_TO_PSA = "shipped_to_psa"
    AT_PSA = "at_psa"
    GRADED = "graded"
    IN_VAULT = "in_vault"
    LISTED_FOR_SALE = "listed_for_sale"
    SOLD = "sold"
    COMPLETED = "completed"

@dataclass
class GradingUpdate:
    deal_id: str
    status: DealStatus
    grade: Optional[int] = None
    cert_number: Optional[str] = None
    estimated_value: Optional[float] = None
    notes: str = ""
    timestamp: str = ""

class PSAGradingTracker:
    """Tracks cards through PSA grading process"""
    
    def __init__(self):
        self.tracking_file = "psa_tracking.json"
        self.vault_file = "vault_inventory.json"
        self.config_file = "grading_config.json"
        self.load_config()
    
    def load_config(self):
        """Load grading tracking configuration"""
        default_config = {
            'psa_submission_tracking': {
                'check_frequency_days': 7,  # Check PSA status weekly
                'expected_turnaround_days': 45,
                'auto_notifications': True
            },
            'vault_management': {
                'auto_list_after_grading': False,  # Manual approval for listing
                'target_sale_markup': 1.1,  # 10% above estimated value
                'min_hold_days': 7  # Hold for at least 7 days after grading
            },
            'selling_preferences': {
                'preferred_platform': 'ebay',
                'listing_duration_days': 10,
                'accept_best_offer': True,
                'auto_accept_threshold': 0.95  # Auto-accept offers ≥95% of asking
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
            print(f"⚠️ Could not save grading config: {e}")
    
    def load_tracking_data(self) -> List[Dict]:
        """Load PSA tracking data"""
        try:
            if os.path.exists(self.tracking_file):
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading tracking data: {e}")
        return []
    
    def save_tracking_data(self, data: List[Dict]):
        """Save PSA tracking data"""
        try:
            with open(self.tracking_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving tracking data: {e}")
    
    def update_deal_status(self, deal_id: str, new_status: DealStatus, **kwargs) -> bool:
        """Update deal status with additional info"""
        tracking_data = self.load_tracking_data()
        
        # Find existing entry or create new one
        entry = None
        for item in tracking_data:
            if item['deal_id'] == deal_id:
                entry = item
                break
        
        if not entry:
            entry = {
                'deal_id': deal_id,
                'status_history': [],
                'current_status': '',
                'created_timestamp': datetime.now().isoformat()
            }
            tracking_data.append(entry)
        
        # Add status update
        update = {
            'status': new_status.value,
            'timestamp': datetime.now().isoformat(),
            'grade': kwargs.get('grade'),
            'cert_number': kwargs.get('cert_number'),
            'estimated_value': kwargs.get('estimated_value'),
            'notes': kwargs.get('notes', '')
        }
        
        entry['status_history'].append(update)
        entry['current_status'] = new_status.value
        entry['last_updated'] = update['timestamp']
        
        # Add specific fields for current status
        if new_status == DealStatus.GRADED:
            entry['grade'] = kwargs.get('grade')
            entry['cert_number'] = kwargs.get('cert_number')
            entry['graded_date'] = update['timestamp']
        
        self.save_tracking_data(tracking_data)
        print(f"✅ Updated {deal_id} to {new_status.value}")
        return True
    
    def check_psa_status(self, submission_number: str) -> Optional[Dict]:
        """Check PSA submission status (mock implementation)"""
        # In reality, this would call PSA's API or scrape their website
        # For now, return mock data
        
        mock_responses = {
            'in_grading': {
                'status': 'Research & ID',
                'estimated_completion': '2025-08-15',
                'notes': 'Cards are currently being researched and identified'
            },
            'graded': {
                'status': 'Graded',
                'completion_date': '2025-08-10',
                'cards': [
                    {
                        'cert_number': '82034567',
                        'grade': 9,
                        'description': 'Charizard Base Set Shadowless',
                        'estimated_value': 4200.00
                    }
                ]
            }
        }
        
        # This would be actual PSA API integration
        print(f"🔍 Checking PSA submission {submission_number}...")
        print("📝 Note: PSA API integration needed for live tracking")
        
        return mock_responses.get('in_grading')  # Mock response
    
    def process_graded_card(self, deal_id: str, grade: int, cert_number: str, estimated_value: float):
        """Process a newly graded card"""
        # Update status
        self.update_deal_status(
            deal_id, 
            DealStatus.GRADED,
            grade=grade,
            cert_number=cert_number,
            estimated_value=estimated_value,
            notes=f"PSA {grade} - Cert #{cert_number}"
        )
        
        # Add to vault inventory
        self.add_to_vault(deal_id, grade, cert_number, estimated_value)
        
        # Send notification
        asyncio.create_task(self.send_grading_notification(deal_id, grade, estimated_value))
    
    def add_to_vault(self, deal_id: str, grade: int, cert_number: str, estimated_value: float):
        """Add graded card to vault inventory"""
        try:
            vault_data = []
            if os.path.exists(self.vault_file):
                with open(self.vault_file, 'r') as f:
                    vault_data = json.load(f)
            
            vault_entry = {
                'deal_id': deal_id,
                'cert_number': cert_number,
                'grade': grade,
                'estimated_value': estimated_value,
                'date_received': datetime.now().isoformat(),
                'status': 'in_vault',
                'hold_until': (datetime.now() + timedelta(days=self.config['vault_management']['min_hold_days'])).isoformat()
            }
            
            vault_data.append(vault_entry)
            
            with open(self.vault_file, 'w') as f:
                json.dump(vault_data, f, indent=2)
            
            print(f"✅ Added {deal_id} to vault (PSA {grade})")
            
        except Exception as e:
            print(f"❌ Error adding to vault: {e}")
    
    async def send_grading_notification(self, deal_id: str, grade: int, estimated_value: float):
        """Send notification when card is graded"""
        try:
            from smart_mvp_bot_fixed import _smart_bot
            
            if grade >= 9:
                grade_emoji = "🏆"
                result = "EXCELLENT"
            elif grade >= 7:
                grade_emoji = "✅"
                result = "GOOD"
            else:
                grade_emoji = "⚠️"
                result = "BELOW TARGET"
            
            message = f"""🎯 *GRADING COMPLETE* {grade_emoji}

*Deal #{deal_id}*

📊 *Result: PSA {grade}* ({result})
💰 Estimated Value: ${estimated_value:.0f}
📅 Received: {datetime.now().strftime('%b %d, %Y')}

🏦 *Next Steps:*
• Card secured in vault
• Market analysis in progress
• Listing recommendation pending

⏰ *Hold Period:* {self.config['vault_management']['min_hold_days']} days minimum"""

            if _smart_bot:
                await _smart_bot.bot.send_message(
                    chat_id=_smart_bot.admin_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            print(f"⚠️ Could not send grading notification: {e}")
    
    def get_vault_inventory(self) -> List[Dict]:
        """Get current vault inventory"""
        try:
            if os.path.exists(self.vault_file):
                with open(self.vault_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading vault inventory: {e}")
        return []
    
    def check_ready_to_sell(self) -> List[Dict]:
        """Check which cards are ready to sell"""
        vault_inventory = self.get_vault_inventory()
        ready_cards = []
        
        for card in vault_inventory:
            if card['status'] == 'in_vault':
                hold_until = datetime.fromisoformat(card['hold_until'])
                if datetime.now() >= hold_until:
                    ready_cards.append(card)
        
        return ready_cards
    
    async def suggest_selling_opportunities(self):
        """Suggest cards ready for selling"""
        ready_cards = self.check_ready_to_sell()
        
        if not ready_cards:
            print("📭 No cards ready for selling yet")
            return
        
        print(f"💰 {len(ready_cards)} card(s) ready for selling:")
        
        for card in ready_cards:
            suggested_price = card['estimated_value'] * self.config['vault_management']['target_sale_markup']
            print(f"   {card['deal_id']}: PSA {card['grade']} → ${suggested_price:.0f}")
        
        # Send Telegram notification
        try:
            from smart_mvp_bot_fixed import _smart_bot
            
            message = f"""💰 *SELLING OPPORTUNITIES*

{len(ready_cards)} card(s) ready for listing:

"""
            
            for card in ready_cards:
                suggested_price = card['estimated_value'] * self.config['vault_management']['target_sale_markup']
                message += f"• Deal #{card['deal_id']}: PSA {card['grade']}\n"
                message += f"  Target: ${suggested_price:.0f}\n\n"
            
            message += "⏰ Ready to create listings?"
            
            if _smart_bot:
                await _smart_bot.bot.send_message(
                    chat_id=_smart_bot.admin_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            print(f"⚠️ Could not send selling notification: {e}")

# CLI interface
async def main():
    """PSA tracking CLI"""
    tracker = PSAGradingTracker()
    
    print("🏆 PSA Grading Tracker & Vault Manager")
    print("=" * 40)
    
    print("Actions:")
    print("1. Update deal status")
    print("2. Check vault inventory")
    print("3. Check selling opportunities")
    print("4. Simulate grading completion")
    print("5. Configure settings")
    
    choice = input("Choose action (1-5): ").strip()
    
    if choice == "1":
        deal_id = input("Enter Deal ID: ").strip()
        print("\nAvailable statuses:")
        for status in DealStatus:
            print(f"  {status.value}")
        
        status_str = input("Enter new status: ").strip()
        try:
            new_status = DealStatus(status_str)
            
            if new_status == DealStatus.GRADED:
                grade = int(input("Enter PSA grade: "))
                cert_number = input("Enter cert number: ")
                estimated_value = float(input("Enter estimated value: $"))
                
                tracker.process_graded_card(deal_id, grade, cert_number, estimated_value)
            else:
                tracker.update_deal_status(deal_id, new_status)
                
        except ValueError:
            print("❌ Invalid status")
    
    elif choice == "2":
        inventory = tracker.get_vault_inventory()
        if inventory:
            print(f"\n🏦 Vault Inventory ({len(inventory)} cards):")
            for card in inventory:
                print(f"   {card['deal_id']}: PSA {card['grade']} - ${card['estimated_value']:.0f}")
        else:
            print("📭 Vault is empty")
    
    elif choice == "3":
        await tracker.suggest_selling_opportunities()
    
    elif choice == "4":
        # Simulate a card being graded
        deal_id = input("Enter Deal ID to simulate grading: ").strip()
        grade = int(input("Enter simulated grade (1-10): "))
        cert_number = f"SIM{datetime.now().strftime('%m%d%H%M')}"
        
        # Estimate value based on grade
        base_values = {10: 4200, 9: 2800, 8: 1200, 7: 600, 6: 300}
        estimated_value = base_values.get(grade, 200)
        
        tracker.process_graded_card(deal_id, grade, cert_number, estimated_value)
    
    elif choice == "5":
        print("\n📋 Current Configuration:")
        print(json.dumps(tracker.config, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
