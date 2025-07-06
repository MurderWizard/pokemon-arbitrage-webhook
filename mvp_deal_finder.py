#!/usr/bin/env python3
"""
MVP Deal Finder - Simple, focused deal finding and manual approval
"""
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot
from quick_price import get_card_market_price
from deal_logger import DealLogger
from alert_formatter import format_deal_alert

class MVPDealFinder:
    """Minimal viable product deal finder"""
    
    def __init__(self):
        load_dotenv()
        self.bot = Bot(token=os.getenv('TG_TOKEN'))
        self.chat_id = os.getenv('TG_ADMIN_ID')
        self.deal_logger = DealLogger()
        self.min_price = 250.0
        self.min_roi = 0.35  # 35%
        
    async def send_deal_alert(self, deal):
        """Send deal alert and wait for approval"""
        alert = format_deal_alert(deal)
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=alert,
            parse_mode='Markdown'
        )
        
        # Log the deal
        deal_id = self.deal_logger.log_deal(deal)
        print(f"Deal {deal_id} sent for approval: {deal['card_name']} - ${deal['raw_price']:.2f}")
        
    def evaluate_card(self, card_name, set_name, listing_price, condition="raw"):
        """Quick deal evaluation"""
        # Get prices
        raw_price, raw_confidence = get_card_market_price(card_name, set_name, "raw")
        psa10_price, psa10_confidence = get_card_market_price(card_name, set_name, "PSA 10")
        
        if not psa10_price or listing_price < self.min_price:
            return None
            
        # Calculate profit potential
        grading_cost = 25.0  # PSA basic
        total_cost = listing_price + grading_cost
        potential_profit = psa10_price - total_cost
        roi = potential_profit / listing_price
        
        if roi < self.min_roi:
            return None
            
        return {
            'card_name': card_name,
            'set_name': set_name,
            'raw_price': listing_price,
            'estimated_psa10_price': psa10_price,
            'potential_profit': potential_profit,
            'profit_margin': roi,
            'condition_notes': condition,
            'listing_url': 'https://www.ebay.com/...',  # Will be real URL
            'recent_sales_count': 5,  # Placeholder
            'price_trend': 'Stable'   # Placeholder
        }
        
    async def test_deal_alert(self):
        """Test the deal alert system with a sample deal"""
        test_deal = self.evaluate_card("Charizard", "Base Set", 400.0, "Near Mint")
        if test_deal:
            await self.send_deal_alert(test_deal)
            print("Test deal alert sent!")
        else:
            print("Test deal didn't meet criteria")

async def main():
    finder = MVPDealFinder()
    
    print("🎯 MVP Deal Finder Test")
    print("=" * 30)
    
    # Test deal evaluation
    print("\n1. Testing deal evaluation...")
    test_deal = finder.evaluate_card("Charizard", "Base Set", 400.0)
    if test_deal:
        print(f"✅ Found viable deal: ${test_deal['potential_profit']:.2f} profit")
        
        # Test alert
        print("\n2. Testing deal alert...")
        await finder.test_deal_alert()
    else:
        print("❌ No viable deal found")

if __name__ == "__main__":
    asyncio.run(main())
