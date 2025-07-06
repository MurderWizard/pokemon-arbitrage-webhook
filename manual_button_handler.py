#!/usr/bin/env python3
"""
Manual Button Response Handler - Simulates button actions until webhook is deployed
Handles approval/rejection of deals manually through CLI
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List
from single_deal_manager import approve_deal, reject_deal, SingleDealManager
from smart_mvp_bot import send_session_summary

class ButtonResponseHandler:
    """Handles manual deal approval/rejection"""
    
    def __init__(self):
        self.manager = SingleDealManager()
    
    def show_pending_deals(self) -> List[Dict]:
        """Show all pending deals waiting for approval"""
        active_deals = self.manager.load_active_deals()
        pending = [deal for deal in active_deals if deal['status'] == 'pending_approval']
        
        if not pending:
            print("📭 No deals pending approval")
            return []
        
        print(f"⏳ {len(pending)} deal(s) pending approval:")
        print("=" * 50)
        
        for i, deal in enumerate(pending, 1):
            deal_data = deal['deal']
            roi = deal_data['roi_percentage']
            profit = deal_data['potential_profit']
            price = deal_data['raw_price']
            card = f"{deal_data['card_name']} • {deal_data['set_name']}"
            
            print(f"{i}. Deal ID: {deal['deal_id']}")
            print(f"   Card: {card}")
            print(f"   Investment: ${price:.0f} + $25 grading = ${price + 25:.0f}")
            print(f"   Profit: ${profit:.0f} ({roi:.0f}% ROI)")
            print(f"   Alerted: {deal['alerted_timestamp'][:16].replace('T', ' ')}")
            print(f"   URL: {deal_data.get('listing_url', 'N/A')}")
            print()
        
        return pending
    
    def show_all_active_deals(self) -> List[Dict]:
        """Show all active deals (pending + approved)"""
        active_deals = self.manager.load_active_deals()
        
        if not active_deals:
            print("📭 No active deals")
            return []
        
        print(f"📊 {len(active_deals)} active deal(s):")
        print("=" * 40)
        
        total_exposure = 0
        for i, deal in enumerate(active_deals, 1):
            deal_data = deal['deal']
            status = deal['status']
            investment = deal['investment_amount']
            total_exposure += investment
            
            print(f"{i}. {deal['deal_id']} • {status.upper()}")
            print(f"   {deal_data['card_name']} • ${investment:.0f} at risk")
            print()
        
        print(f"💰 Total Capital at Risk: ${total_exposure:.0f}")
        return active_deals
    
    async def handle_approval(self, deal_id: str) -> bool:
        """Handle deal approval"""
        print(f"✅ Processing approval for {deal_id}...")
        
        success = approve_deal(deal_id)
        
        if success:
            print(f"✅ Deal {deal_id} approved!")
            print("   Status: Active investment")
            print("   Next: Monitor for grading/selling")
            
            # Send update to Telegram
            stats = {
                'action': 'approved',
                'deal_id': deal_id,
                'active_deals': self.manager.get_active_deal_count(),
                'total_exposure': self.manager.get_total_exposure()
            }
            
            # Note: In production, this would trigger a webhook response
            print(f"📱 Telegram: Deal {deal_id} approved - monitoring for completion")
            return True
        else:
            print(f"❌ Failed to approve {deal_id}")
            return False
    
    async def handle_rejection(self, deal_id: str) -> bool:
        """Handle deal rejection"""
        print(f"❌ Processing rejection for {deal_id}...")
        
        success = reject_deal(deal_id)
        
        if success:
            print(f"❌ Deal {deal_id} rejected!")
            print("   Status: Removed from active deals")
            print("   Result: Capital freed for new opportunities")
            
            # Check if we can now alert on new deals
            active_count = self.manager.get_active_deal_count()
            if active_count == 0:
                print("🎯 No active deals - system ready for new alerts")
            
            # Note: In production, this would trigger a webhook response
            print(f"📱 Telegram: Deal {deal_id} rejected - scanning for new opportunities")
            return True
        else:
            print(f"❌ Failed to reject {deal_id}")
            return False
    
    async def interactive_approval(self):
        """Interactive approval interface"""
        pending = self.show_pending_deals()
        
        if not pending:
            return
        
        print("Options:")
        print("A [deal_id] - Approve deal")
        print("R [deal_id] - Reject deal")
        print("Q - Quit")
        
        while True:
            action = input("\nEnter action: ").strip().upper()
            
            if action == 'Q':
                break
            
            if action.startswith('A '):
                deal_id = action[2:].strip()
                await self.handle_approval(deal_id)
                break
            elif action.startswith('R '):
                deal_id = action[2:].strip()
                await self.handle_rejection(deal_id)
                break
            else:
                print("Invalid action. Use 'A [deal_id]', 'R [deal_id]', or 'Q'")
    
    async def quick_approve_next(self) -> bool:
        """Quickly approve the next pending deal"""
        pending = self.manager.load_active_deals()
        pending = [d for d in pending if d['status'] == 'pending_approval']
        
        if not pending:
            print("📭 No deals to approve")
            return False
        
        # Get the most recent pending deal
        next_deal = max(pending, key=lambda d: d['alerted_timestamp'])
        deal_id = next_deal['deal_id']
        
        print(f"🚀 Quick approving: {deal_id}")
        return await self.handle_approval(deal_id)
    
    async def quick_reject_all(self) -> bool:
        """Quickly reject all pending deals"""
        pending = self.manager.load_active_deals()
        pending = [d for d in pending if d['status'] == 'pending_approval']
        
        if not pending:
            print("📭 No deals to reject")
            return False
        
        print(f"🧹 Rejecting {len(pending)} pending deals...")
        
        for deal in pending:
            await self.handle_rejection(deal['deal_id'])
        
        print("✅ All pending deals rejected")
        return True

# CLI interface
async def main():
    """Main CLI for manual button responses"""
    handler = ButtonResponseHandler()
    
    print("🎯 Manual Button Response Handler")
    print("=" * 35)
    print("Simulates Telegram button actions until webhook is deployed")
    print()
    
    # Show current status
    handler.show_all_active_deals()
    print()
    
    print("Actions:")
    print("1. Show pending deals")
    print("2. Interactive approval")
    print("3. Quick approve next")
    print("4. Quick reject all")
    print("5. Show all active deals")
    print("6. Simulate button test")
    
    choice = input("Choose action (1-6): ").strip()
    
    if choice == "1":
        handler.show_pending_deals()
    elif choice == "2":
        await handler.interactive_approval()
    elif choice == "3":
        await handler.quick_approve_next()
    elif choice == "4":
        await handler.quick_reject_all()
    elif choice == "5":
        handler.show_all_active_deals()
    elif choice == "6":
        await simulate_button_test()

async def simulate_button_test():
    """Simulate receiving button presses for testing"""
    print("🧪 Simulating button test scenario")
    print("=" * 35)
    
    # This simulates what would happen when buttons are pressed
    test_scenarios = [
        ("TEST_001", "approve", "User clicked APPROVE button"),
        ("TEST_002", "reject", "User clicked PASS button"),
        ("TEST_003", "approve", "User clicked APPROVE button")
    ]
    
    handler = ButtonResponseHandler()
    
    for deal_id, action, description in test_scenarios:
        print(f"\n📱 Telegram: {description}")
        print(f"   Deal ID: {deal_id}")
        print(f"   Action: {action.upper()}")
        
        if action == "approve":
            # In production: webhook would call this
            print("   → Calling approval handler...")
            print(f"   → Result: Deal {deal_id} would be marked as approved")
        elif action == "reject":
            # In production: webhook would call this  
            print("   → Calling rejection handler...")
            print(f"   → Result: Deal {deal_id} would be removed from active deals")
        
        await asyncio.sleep(1)
    
    print("\n✅ Button simulation complete")
    print("📝 Note: In production, webhook server would handle these automatically")

if __name__ == "__main__":
    asyncio.run(main())
