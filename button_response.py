#!/usr/bin/env python3
"""
Button Response System - Manual trigger for button actions
Since polling has environment issues, we'll use a different approach
"""
import sqlite3
from datetime import datetime
from deal_logger import DealLogger

def manual_approve_deal(deal_id: str):
    """Manually approve a deal (simulates button press)"""
    print(f"🎯 Processing APPROVAL for Deal #{deal_id}")
    
    # Update deal status
    deal_logger = DealLogger()
    deal_logger.update_deal_status(deal_id, "APPROVED", "Manual approval")
    
    # Get deal info
    deal_info = get_deal_info(deal_id)
    
    print(f"\n✅ DEAL #{deal_id} APPROVED")
    print(f"💰 Investment: ${deal_info.get('raw_price', 0):.0f}")
    print(f"🎯 Target Profit: ${deal_info.get('potential_profit', 0):.0f}")
    print(f"📅 Approved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n🎯 NEXT ACTIONS:")
    print(f"1. 🛒 Purchase immediately on eBay")
    print(f"2. 📦 Ship to PSA (Regular service ~45 days)")
    print(f"3. 💎 List PSA 10 result for ${deal_info.get('estimated_psa10_price', 0):.0f}")
    
    print(f"\n⚠️ CAPITAL STATUS:")
    print(f"Deal #{deal_id} is now your active investment.")
    print(f"No new deals will be approved until this completes.")
    
    return True

def manual_reject_deal(deal_id: str):
    """Manually reject a deal"""
    print(f"🎯 Processing REJECTION for Deal #{deal_id}")
    
    # Update deal status
    deal_logger = DealLogger()
    deal_logger.update_deal_status(deal_id, "REJECTED", "Manual rejection")
    
    print(f"\n❌ DEAL #{deal_id} REJECTED")
    print(f"📅 Rejected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💰 Capital preserved")
    print(f"🔍 Continuing search for better opportunities...")
    
    return True

def get_deal_info(deal_id: str) -> dict:
    """Get deal information from database"""
    try:
        conn = sqlite3.connect("deals.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT card_name, set_name, raw_price, estimated_psa10_price, 
                   potential_profit, condition_notes, listing_url
            FROM deals WHERE id = ?
        ''', (deal_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'card_name': result[0],
                'set_name': result[1], 
                'raw_price': result[2],
                'estimated_psa10_price': result[3],
                'potential_profit': result[4],
                'condition_notes': result[5],
                'listing_url': result[6]
            }
        return {}
        
    except Exception as e:
        print(f"❌ Error getting deal info: {e}")
        return {}

def show_pending_deals():
    """Show deals awaiting decision"""
    try:
        conn = sqlite3.connect("deals.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, card_name, set_name, raw_price, potential_profit, timestamp
            FROM deals 
            WHERE status = 'new' OR status IS NULL
            ORDER BY timestamp DESC
            LIMIT 5
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        if results:
            print("📋 PENDING DEALS (Awaiting Decision):")
            print("-" * 50)
            for row in results:
                deal_id, card, set_name, price, profit, timestamp = row
                print(f"Deal #{deal_id}: {card} {set_name}")
                print(f"   💰 ${price:.0f} → ${profit:.0f} profit")
                print(f"   📅 {timestamp}")
                print()
        else:
            print("✅ No pending deals")
            
    except Exception as e:
        print(f"❌ Error getting pending deals: {e}")

if __name__ == "__main__":
    print("🎯 Manual Button Response System")
    print("=" * 40)
    
    # Show pending deals
    show_pending_deals()
    
    print("\n💡 To approve/reject deals:")
    print("python3 -c \"from button_response import manual_approve_deal; manual_approve_deal('11')\"")
    print("python3 -c \"from button_response import manual_reject_deal; manual_reject_deal('11')\"")
    
    print("\n🔄 Or use the functions directly in this script")
    
    # Example: Process the latest deal (Deal #11)
    print("\n🧪 Example - Processing Deal #11:")
    choice = input("Approve Deal #11? (y/n): ").lower().strip()
    
    if choice == 'y':
        manual_approve_deal('11')
    elif choice == 'n':
        manual_reject_deal('11')
    else:
        print("⏳ No action taken - deal remains pending")
