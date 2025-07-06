#!/usr/bin/env python3
"""
Active Opportunity Monitor
Continuously watches for profitable deals and alerts immediately
"""
import asyncio
import time
from datetime import datetime
from strategic_opportunity_finder import StrategicOpportunityFinder

class ActiveOpportunityMonitor:
    """Continuously monitor for profitable opportunities"""
    
    def __init__(self):
        self.finder = StrategicOpportunityFinder()
        self.scan_interval = 300  # 5 minutes between scans
        self.opportunities_found = 0
        self.running = True
        
    async def start_monitoring(self):
        """Start continuous opportunity monitoring"""
        
        print("🚨 ACTIVE OPPORTUNITY MONITOR STARTED")
        print("=" * 50)
        print("🎯 Strategy: Scan every 5 minutes for profit opportunities")
        print("⚡ Speed: Quick decisions on good deals")
        print("💰 Focus: 3x+ ROI opportunities only")
        print("🔄 Mode: Continuous monitoring")
        print()
        
        scan_count = 0
        
        while self.running:
            scan_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"🔍 SCAN #{scan_count} - {timestamp}")
            print("-" * 30)
            
            try:
                # Look for opportunities
                opportunity = await self.finder.find_best_opportunity()
                
                if opportunity:
                    self.opportunities_found += 1
                    print(f"🎯 OPPORTUNITY #{self.opportunities_found} FOUND!")
                    print(f"   💰 ${opportunity['potential_profit']:.0f} profit potential")
                    print(f"   📱 Check Telegram for approval!")
                    print(f"   ⚡ Decide quickly - good deals disappear fast!")
                    
                    # Wait longer after finding a deal (let user decide)
                    wait_time = 900  # 15 minutes
                    print(f"   ⏳ Waiting 15 minutes for your decision...")
                    
                else:
                    print(f"   ❌ No qualifying opportunities this scan")
                    wait_time = self.scan_interval
                
                print(f"   💤 Next scan in {wait_time//60} minutes")
                print()
                
                # Wait before next scan
                await asyncio.sleep(wait_time)
                
            except KeyboardInterrupt:
                print("\n⚠️ Monitoring stopped by user")
                break
            except Exception as e:
                print(f"   ❌ Scan error: {e}")
                print(f"   🔄 Retrying in {self.scan_interval//60} minutes...")
                await asyncio.sleep(self.scan_interval)
        
        # Summary
        print("\n📊 MONITORING SESSION COMPLETE:")
        print(f"   🔍 Total scans: {scan_count}")
        print(f"   🎯 Opportunities found: {self.opportunities_found}")
        print(f"   ⏰ Duration: {scan_count * self.scan_interval // 60} minutes")
        
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.running = False

async def main():
    """Start active opportunity monitoring"""
    monitor = ActiveOpportunityMonitor()
    
    print("🚀 STARTING ACTIVE OPPORTUNITY MONITORING")
    print()
    print("💡 What this does:")
    print("   • Scans for profitable deals every 5 minutes")
    print("   • Alerts you immediately when opportunities appear")
    print("   • Focuses on 3x+ ROI deals only")
    print("   • Keeps running until you stop it")
    print()
    print("⚡ Quick Decision Strategy:")
    print("   • Good deals disappear fast on eBay")
    print("   • Be ready to /approve or /pass quickly")
    print("   • Focus on highest ROI opportunities")
    print()
    print("🎯 Ready to start hunting for money-making opportunities!")
    print("Press Ctrl+C to stop monitoring anytime")
    print()
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped. Happy hunting!")

if __name__ == "__main__":
    asyncio.run(main())
