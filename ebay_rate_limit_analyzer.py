#!/usr/bin/env python3
"""
eBay API Rate Limit Analysis & Optimization Strategy
Deep dive into eBay SDK limits and optimal exploration patterns
"""
import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

class EbayRateLimitAnalyzer:
    """Analyze and optimize eBay API usage for maximum efficiency"""
    
    def __init__(self):
        load_dotenv()
        self.app_id = os.getenv('EBAY_APP_ID')
        self.daily_limit = 5000  # Free tier limit
        self.calls_made_today = 0
        self.call_log = []
        
    def analyze_current_limits(self):
        """Analyze eBay API rate limits and current usage"""
        
        print("🔍 EBAY API RATE LIMIT ANALYSIS")
        print("=" * 50)
        
        # eBay Finding API Limits (Free Tier)
        limits = {
            "daily_calls": 5000,
            "calls_per_second": 10,  # Estimated safe rate
            "calls_per_minute": 300,  # Conservative estimate
            "calls_per_hour": 1200,   # 20% of daily limit per hour max
            "concurrent_requests": 5,  # Safe concurrent limit
            "search_results_per_call": 100,  # Max results per API call
            "max_pages_per_search": 10  # Practical limit
        }
        
        print("📊 EBAY FINDING API LIMITS (FREE TIER):")
        print(f"   📅 Daily Calls: {limits['daily_calls']:,}")
        print(f"   ⏱️ Calls/Second: {limits['calls_per_second']}")
        print(f"   🕐 Calls/Minute: {limits['calls_per_minute']}")
        print(f"   📈 Calls/Hour: {limits['calls_per_hour']:,}")
        print(f"   🔄 Concurrent: {limits['concurrent_requests']}")
        print(f"   📋 Results/Call: {limits['search_results_per_call']}")
        print()
        
        return limits
    
    def calculate_optimal_search_strategy(self):
        """Calculate the most efficient search strategy"""
        
        print("🎯 OPTIMAL SEARCH STRATEGY ANALYSIS")
        print("=" * 50)
        
        # Our target cards (6 proven winners)
        target_cards = [
            "Charizard Base Set",
            "Dark Charizard Team Rocket", 
            "Blastoise Base Set",
            "Venusaur Base Set",
            "Lugia Neo Genesis",
            "Ho-oh Neo Revelation"
        ]
        
        # Calculate API calls needed for different strategies
        strategies = {
            "conservative": {
                "description": "1 search per card, every 30 minutes",
                "cards_searched": len(target_cards),
                "searches_per_hour": 2,
                "calls_per_hour": len(target_cards) * 2,
                "daily_calls": len(target_cards) * 2 * 24,
                "results_per_call": 50
            },
            "moderate": {
                "description": "1 search per card, every 15 minutes", 
                "cards_searched": len(target_cards),
                "searches_per_hour": 4,
                "calls_per_hour": len(target_cards) * 4,
                "daily_calls": len(target_cards) * 4 * 24,
                "results_per_call": 50
            },
            "aggressive": {
                "description": "1 search per card, every 10 minutes",
                "cards_searched": len(target_cards), 
                "searches_per_hour": 6,
                "calls_per_hour": len(target_cards) * 6,
                "daily_calls": len(target_cards) * 6 * 24,
                "results_per_call": 50
            },
            "intensive": {
                "description": "2 searches per card (different price ranges), every 15 minutes",
                "cards_searched": len(target_cards) * 2,
                "searches_per_hour": 4,
                "calls_per_hour": len(target_cards) * 2 * 4,
                "daily_calls": len(target_cards) * 2 * 4 * 24,
                "results_per_call": 50
            }
        }
        
        print("🔍 SEARCH STRATEGY COMPARISON:")
        print()
        
        for name, strategy in strategies.items():
            daily_usage = (strategy['daily_calls'] / 5000) * 100
            status = "✅ SAFE" if daily_usage < 80 else "⚠️ RISKY" if daily_usage < 100 else "❌ EXCEEDS LIMIT"
            
            print(f"📋 {name.upper()} STRATEGY:")
            print(f"   📝 {strategy['description']}")
            print(f"   🔢 API Calls/Hour: {strategy['calls_per_hour']}")
            print(f"   📅 API Calls/Day: {strategy['daily_calls']:,}")
            print(f"   📊 Daily Usage: {daily_usage:.1f}% of limit")
            print(f"   🎯 Status: {status}")
            print()
        
        return strategies
    
    def recommend_optimal_timing(self):
        """Recommend optimal timing for API calls"""
        
        print("⏰ OPTIMAL TIMING RECOMMENDATIONS")
        print("=" * 50)
        
        timing_strategy = {
            "peak_hours": {
                "times": "12PM-8PM EST",
                "description": "Most eBay activity - new listings appear",
                "recommended_frequency": "Every 10-15 minutes",
                "priority": "🔥 HIGH"
            },
            "off_peak_hours": {
                "times": "8PM-8AM EST", 
                "description": "Lower activity - fewer new listings",
                "recommended_frequency": "Every 30 minutes",
                "priority": "📈 MEDIUM"
            },
            "dead_hours": {
                "times": "2AM-6AM EST",
                "description": "Minimal activity - mostly international",
                "recommended_frequency": "Every 60 minutes", 
                "priority": "💤 LOW"
            }
        }
        
        for period, info in timing_strategy.items():
            print(f"🕒 {period.replace('_', ' ').upper()}:")
            print(f"   ⏰ {info['times']}")
            print(f"   📝 {info['description']}")
            print(f"   🔄 Frequency: {info['recommended_frequency']}")
            print(f"   ⭐ Priority: {info['priority']}")
            print()
        
        return timing_strategy
    
    def design_smart_monitoring_system(self):
        """Design smart monitoring system within API limits"""
        
        print("🧠 SMART MONITORING SYSTEM DESIGN")
        print("=" * 50)
        
        # Recommended strategy: MODERATE with dynamic adjustment
        recommended = {
            "base_strategy": "moderate",
            "dynamic_adjustments": True,
            "total_daily_calls": 288,  # Well under 5000 limit
            "api_usage_percentage": 5.76,  # Only 5.76% of daily limit
            "safety_margin": "94.24%",  # Huge safety margin
            
            "schedule": {
                "peak_hours_12pm_8pm": {
                    "frequency": "Every 15 minutes",
                    "calls_per_hour": 24,  # 6 cards * 4 searches/hour
                    "hours": 8,
                    "total_calls": 192
                },
                "off_peak_8pm_12am": {
                    "frequency": "Every 30 minutes", 
                    "calls_per_hour": 12,  # 6 cards * 2 searches/hour
                    "hours": 4,
                    "total_calls": 48
                },
                "overnight_12am_8am": {
                    "frequency": "Every 60 minutes",
                    "calls_per_hour": 6,   # 6 cards * 1 search/hour
                    "hours": 8,
                    "total_calls": 48
                }
            }
        }
        
        print("🎯 RECOMMENDED MONITORING SYSTEM:")
        print(f"   📊 Base Strategy: {recommended['base_strategy'].upper()}")
        print(f"   📅 Total Daily API Calls: {recommended['total_daily_calls']}")
        print(f"   📈 API Usage: {recommended['api_usage_percentage']:.1f}% of daily limit")
        print(f"   🛡️ Safety Margin: {recommended['safety_margin']}")
        print()
        
        print("📅 DAILY SCHEDULE:")
        for period, schedule in recommended['schedule'].items():
            print(f"   🕐 {period.replace('_', ' ').title()}:")
            print(f"      ⏱️ {schedule['frequency']}")
            print(f"      🔢 {schedule['calls_per_hour']} calls/hour")
            print(f"      ⏰ {schedule['hours']} hours")
            print(f"      📊 {schedule['total_calls']} total calls")
            print()
        
        return recommended
    
    def create_api_efficiency_tips(self):
        """Create tips for maximum API efficiency"""
        
        print("💡 API EFFICIENCY OPTIMIZATION TIPS")
        print("=" * 50)
        
        tips = {
            "search_optimization": [
                "Use specific keywords (e.g., 'Charizard Base Set' not 'Charizard')",
                "Set price filters ($250+ for high-value focus)",
                "Request max results per call (100 items)",
                "Use category filters (2536 = Trading Card Games)",
                "Filter by condition (New/Like New only)"
            ],
            "caching_strategy": [
                "Cache search results for 10-15 minutes",
                "Store item details to avoid re-fetching",
                "Keep price history to identify trends",
                "Cache seller information for quick filtering"
            ],
            "smart_filtering": [
                "Pre-filter results client-side to reduce API calls",
                "Focus on Buy-It-Now listings only",
                "Skip graded cards in search filters",
                "Prioritize high-feedback sellers (98%+)"
            ],
            "error_handling": [
                "Implement exponential backoff for rate limits",
                "Retry failed calls with delay",
                "Monitor API response times",
                "Log all API calls for usage tracking"
            ]
        }
        
        for category, tip_list in tips.items():
            print(f"🔧 {category.replace('_', ' ').upper()}:")
            for tip in tip_list:
                print(f"   ✅ {tip}")
            print()
        
        return tips
    
    def calculate_coverage_analysis(self):
        """Calculate how much market coverage we get with API limits"""
        
        print("📊 MARKET COVERAGE ANALYSIS")
        print("=" * 50)
        
        # With our recommended strategy
        coverage = {
            "target_cards": 6,
            "searches_per_card_per_day": 48,  # Average across peak/off-peak/overnight
            "results_per_search": 50,
            "total_listings_analyzed_daily": 6 * 48 * 50,
            "new_listings_per_day_estimate": 200,  # For our 6 target cards
            "coverage_percentage": (6 * 48 * 50) / (200 * 6) * 100
        }
        
        print(f"🎯 TARGET CARDS: {coverage['target_cards']}")
        print(f"🔍 SEARCHES PER CARD/DAY: {coverage['searches_per_card_per_day']}")
        print(f"📋 RESULTS PER SEARCH: {coverage['results_per_search']}")
        print(f"📊 TOTAL LISTINGS ANALYZED: {coverage['total_listings_analyzed_daily']:,}/day")
        print(f"📈 ESTIMATED NEW LISTINGS: {coverage['new_listings_per_day_estimate'] * coverage['target_cards']:,}/day")
        print(f"🎯 MARKET COVERAGE: {coverage['coverage_percentage']:.0f}%")
        print()
        
        print("💡 COVERAGE INSIGHTS:")
        print("   ✅ We'll see virtually every profitable deal")
        print("   ✅ Multiple chances to catch the same listing") 
        print("   ✅ Real-time detection of new opportunities")
        print("   ✅ Historical tracking of price changes")
        
        return coverage

def main():
    """Run complete eBay API analysis"""
    analyzer = EbayRateLimitAnalyzer()
    
    print("🎴 EBAY API OPTIMIZATION ANALYSIS")
    print("=" * 60)
    print("📊 Comprehensive analysis of eBay API limits and optimal usage")
    print()
    
    # Run all analyses
    limits = analyzer.analyze_current_limits()
    strategies = analyzer.calculate_optimal_search_strategy()
    timing = analyzer.recommend_optimal_timing()
    monitoring = analyzer.design_smart_monitoring_system()
    tips = analyzer.create_api_efficiency_tips()
    coverage = analyzer.calculate_coverage_analysis()
    
    # Final recommendations
    print("🚀 FINAL RECOMMENDATIONS")
    print("=" * 50)
    print("✅ Use MODERATE strategy (every 15 minutes during peak)")
    print("✅ Focus on 6 proven high-ROI cards only")
    print("✅ Implement dynamic timing (peak/off-peak/overnight)")
    print("✅ Use only 5.8% of daily API limit (huge safety margin)")
    print("✅ Cache results to maximize efficiency")
    print("✅ 100% market coverage for target opportunities")
    print()
    print("🎯 RESULT: Maximum opportunity detection with minimal API usage!")
    
    return {
        "limits": limits,
        "strategies": strategies,
        "timing": timing,
        "monitoring": monitoring,
        "tips": tips,
        "coverage": coverage
    }

if __name__ == "__main__":
    main()
