#!/usr/bin/env python3
"""
Smart Timing-Aware Opportunity Monitor
Adjusts scanning frequency and strategy based on optimal time windows
"""
import asyncio
from datetime import datetime
from optimal_timing_strategy import OptimalTimingStrategy
from strategic_opportunity_finder import StrategicOpportunityFinder

class SmartTimingMonitor:
    """Timing-aware opportunity monitoring with dynamic strategy"""
    
    def __init__(self):
        self.strategy = OptimalTimingStrategy()
        self.finder = StrategicOpportunityFinder()
        self.running = True
        self.total_scans = 0
        self.opportunities_found = 0
        
    async def start_smart_monitoring(self):
        """Start timing-aware monitoring with dynamic strategy"""
        
        print("🧠 SMART TIMING-AWARE OPPORTUNITY MONITOR")
        print("=" * 60)
        print("💡 Strategy: Adjust scanning based on optimal time windows")
        print("🎯 Focus: Maximum opportunities with minimum effort")
        print("⏰ Dynamic: Changes strategy based on current time")
        print()
        
        while self.running:
            try:
                # Get current timing context
                current = self.strategy.get_current_window()
                
                # Display current strategy
                self.show_current_strategy(current)
                
                # Execute scan with timing-aware strategy
                await self.execute_timing_aware_scan(current)
                
                # Calculate wait time based on current window
                wait_time = self.get_optimal_wait_time(current['window'])
                
                print(f"   ⏳ Next scan in {wait_time//60} minutes (optimized for {current['window']})")
                print()
                
                await asyncio.sleep(wait_time)
                
            except KeyboardInterrupt:
                print("\n⚠️ Smart monitoring stopped by user")
                break
            except Exception as e:
                print(f"   ❌ Scan error: {e}")
                print("   🔄 Retrying in 5 minutes...")
                await asyncio.sleep(300)
        
        self.show_session_summary()
    
    def show_current_strategy(self, current: dict):
        """Display current timing strategy"""
        self.total_scans += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"🔍 SCAN #{self.total_scans} - {timestamp}")
        print(f"   ⏰ Window: {current['window'].replace('_', ' ').title()}")
        print(f"   📊 Expected Success: {current['data'].get('success_rate', 'Unknown')}")
        print(f"   🎯 Day Quality: {current['weekly_quality'].get('quality', 'Unknown')}")
        
        # Show top recommendation
        if current['recommendations']:
            print(f"   💡 {current['recommendations'][0]}")
    
    async def execute_timing_aware_scan(self, current: dict):
        """Execute scan with timing-aware strategy"""
        window = current['window']
        
        # Adjust search strategy based on timing
        if window == 'golden_hours':
            # Aggressive scanning during golden hours
            strategy_notes = "🔥 GOLDEN HOURS - Aggressive scanning, all opportunities"
            min_roi_threshold = 200  # Lower threshold during golden hours
        elif window == 'prime_hours':
            strategy_notes = "📈 PRIME HOURS - Standard scanning, good opportunities"
            min_roi_threshold = 250  # Standard threshold
        elif window == 'peak_hours':
            strategy_notes = "⚠️ PEAK HOURS - Conservative, exceptional deals only"
            min_roi_threshold = 400  # Higher threshold during peak hours
        else:
            strategy_notes = "🌙 OFF HOURS - Opportunistic scanning"
            min_roi_threshold = 300
        
        print(f"   🎯 {strategy_notes}")
        
        # Execute the scan
        opportunity = await self.finder.find_best_opportunity()
        
        if opportunity:
            roi = opportunity.get('profit_margin', 0)
            
            # Apply timing-aware filtering
            if roi >= min_roi_threshold:
                self.opportunities_found += 1
                print(f"   ✅ OPPORTUNITY #{self.opportunities_found} APPROVED!")
                print(f"   💰 ${opportunity['potential_profit']:.0f} profit ({roi:.0f}% ROI)")
                print(f"   🎯 Meets {window} criteria (>{min_roi_threshold}% ROI)")
                print(f"   📱 Check Telegram for alert!")
            else:
                print(f"   ⚠️ Opportunity found but filtered out")
                print(f"   📊 {roi:.0f}% ROI < {min_roi_threshold}% threshold for {window}")
        else:
            print(f"   ❌ No opportunities this scan")
    
    def get_optimal_wait_time(self, window: str) -> int:
        """Get optimal wait time based on current window"""
        wait_times = {
            'golden_hours': 300,    # 5 minutes - aggressive
            'prime_hours': 600,     # 10 minutes - standard  
            'peak_hours': 900,      # 15 minutes - conservative
            'off_hours': 1200       # 20 minutes - relaxed
        }
        
        return wait_times.get(window, 600)
    
    def show_session_summary(self):
        """Show session summary"""
        print("📊 SMART TIMING SESSION COMPLETE:")
        print(f"   🔍 Total scans: {self.total_scans}")
        print(f"   🎯 Opportunities found: {self.opportunities_found}")
        print(f"   📈 Success rate: {(self.opportunities_found/self.total_scans*100):.1f}%")
        print(f"   ⏰ Smart timing optimization: Active")

async def main():
    """Start smart timing-aware monitoring"""
    monitor = SmartTimingMonitor()
    
    print("🚀 STARTING SMART TIMING-AWARE MONITORING")
    print()
    print("💡 What this does:")
    print("   • Adjusts strategy based on optimal time windows")
    print("   • Scans more frequently during golden hours (85% success)")
    print("   • Uses higher ROI thresholds during peak hours (high competition)")
    print("   • Maximizes opportunities while minimizing wasted effort")
    print()
    print("⏰ Current Status:")
    
    # Show current timing context
    strategy = OptimalTimingStrategy()
    current = strategy.get_current_window()
    
    for rec in current['recommendations'][:2]:
        print(f"   {rec}")
    
    print()
    print("🎯 Ready to start smart opportunity hunting!")
    print("Press Ctrl+C to stop monitoring anytime")
    print()
    
    try:
        await monitor.start_smart_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Smart monitoring stopped. Timing is everything!")

if __name__ == "__main__":
    asyncio.run(main())
