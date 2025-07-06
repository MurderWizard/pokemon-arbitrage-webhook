#!/usr/bin/env python3
"""
Quick Opportunity Check
Fast scan for immediate opportunities - perfect for regular checks
"""
import asyncio
from strategic_opportunity_finder import StrategicOpportunityFinder

async def quick_opportunity_check():
    """Quick scan for immediate opportunities"""
    
    print("⚡ QUICK OPPORTUNITY CHECK")
    print("=" * 40)
    print("🔍 Scanning for immediate profit opportunities...")
    print()
    
    finder = StrategicOpportunityFinder()
    
    try:
        opportunity = await finder.find_best_opportunity()
        
        if opportunity:
            print("🎯 IMMEDIATE OPPORTUNITY FOUND!")
            print(f"💰 {opportunity['card_name']} ({opportunity['set_name']})")
            print(f"💸 ${opportunity['raw_price']:.0f} → ${opportunity['estimated_psa10_price']:.0f}")
            print(f"🎯 ${opportunity['potential_profit']:.0f} profit ({opportunity['profit_margin']:.0f}% ROI)")
            print()
            print("📱 CHECK TELEGRAM FOR ALERT!")
            print("⚡ Decide quickly - /approve or /pass")
            print("💰 This could be your next profit!")
            
        else:
            print("❌ No immediate opportunities found")
            print("💡 Good deals appear throughout the day")
            print("🔄 Try running this again in 10-15 minutes")
            print("📈 Or start continuous monitoring with:")
            print("   python3 active_opportunity_monitor.py")
        
    except Exception as e:
        print(f"❌ Error during scan: {e}")
        print("🔄 Try again in a few minutes")

if __name__ == "__main__":
    asyncio.run(quick_opportunity_check())
