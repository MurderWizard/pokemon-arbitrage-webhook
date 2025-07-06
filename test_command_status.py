#!/usr/bin/env python3
"""
Simple command tester - Test the Telegram commands
"""
from pending_deals_storage import load_pending_deals, get_latest_deal_id, clear_all_pending
import json

def show_status():
    """Show current status of pending deals"""
    print("🎯 COMMAND APPROVAL SYSTEM STATUS")
    print("=" * 50)
    
    deals = load_pending_deals()
    latest = get_latest_deal_id()
    
    print(f"📋 Pending Deals: {len(deals)}")
    print(f"🔥 Latest Deal: {latest or 'None'}")
    
    if deals:
        print("\n⏳ PENDING DEALS:")
        for deal_id, deal in deals.items():
            roi = (deal['potential_profit'] / deal['raw_price']) * 100
            print(f"   🎯 #{deal_id}: {deal['card_name']}")
            print(f"      💰 ${deal['raw_price']:.0f} → ${deal['estimated_psa10_price']:.0f}")
            print(f"      📈 ${deal['potential_profit']:.0f} ({roi:.0f}% ROI)")
            print(f"      ⏰ Added: {deal['added_timestamp'][:19]}")
    
    print("\n🤖 TELEGRAM COMMANDS TO TRY:")
    print("   • /pending - Show all pending deals")
    print("   • /status - Bot status")
    if latest:
        print(f"   • /approve - Approve latest (#{latest})")
        print(f"   • /pass - Reject latest (#{latest})")
        print(f"   • /approve {latest} - Approve specific deal")
        print(f"   • /pass {latest} - Reject specific deal")
    print("   • /help - Show help message")
    
    print(f"\n✅ Command bot is running! Go to Telegram and test the commands.")

if __name__ == "__main__":
    show_status()
