#!/usr/bin/env python3
"""
Smart MVP Telegram Bot - Clean, actionable alerts with lifecycle management
Focuses on single⚠️ *Single Deal Strategy* - Focus all capital on one opportunity

{datetime.now().strftime('%I:%M %p • %b %d')}

**REQUIRES MANUAL APPROVAL**"""al strategy with enhanced metrics and minimal buttons
"""
import os
import asyncio
import logging
from typing import Dict
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# Simple logging
logging.basicConfig(level=logging.INFO)

class SmartMVPBot:
    """Streamlined bot for smart arbitrage with single deal focus"""
    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv('TG_TOKEN')
        self.admin_id = int(os.getenv('TG_ADMIN_ID'))
        self.bot = Bot(token=self.token)
        
    def calculate_smart_metrics(self, deal: Dict) -> Dict:
        """Calculate essential metrics for deal evaluation"""
        
        # Current PSA turnaround (realistic estimates)
        grading_days = 45  # PSA Regular service
        
        # Sell velocity based on card popularity and market depth
        card_name = deal.get('card_name', '').lower()
        if any(x in card_name for x in ['charizard', 'blastoise', 'venusaur']):
            sell_days = 7  # High demand starters
            market_depth = "Deep"
            confidence = "High"
        elif any(x in card_name for x in ['pikachu', 'alakazam', 'machamp']):
            sell_days = 14  # Popular cards
            market_depth = "Good"
            confidence = "Medium-High"
        elif any(x in card_name for x in ['mewtwo', 'mew', 'dragonite']):
            sell_days = 21  # Solid demand
            market_depth = "Steady"
            confidence = "Medium"
        else:
            sell_days = 30  # Standard cards
            market_depth = "Variable" 
            confidence = "Medium-Low"
            
        # Risk assessment based on ROI and market factors
        roi = (deal['potential_profit'] / deal['raw_price']) * 100
        
        if roi > 1000:  # 10x+ return
            risk_level = "⚠️ HIGH"
            risk_note = "Verify authenticity & condition"
        elif roi > 500:  # 5-10x return
            risk_level = "🔶 MEDIUM-HIGH" 
            risk_note = "Double-check comps & condition"
        elif roi > 300:  # 3-5x return
            risk_level = "🟡 MEDIUM"
            risk_note = "Good opportunity, verify listing"
        elif roi > 150:  # 1.5-3x return
            risk_level = "🟢 LOW-MEDIUM"
            risk_note = "Conservative, solid play"
        else:
            risk_level = "✅ LOW"
            risk_note = "Safe, lower upside"
            
        total_days = grading_days + sell_days
        completion_date = datetime.now() + timedelta(days=total_days)
        daily_profit = deal['potential_profit'] / total_days
        
        return {
            'grading_days': grading_days,
            'sell_days': sell_days,
            'total_days': total_days,
            'completion_date': completion_date,
            'market_depth': market_depth,
            'confidence': confidence,
            'risk_level': risk_level,
            'risk_note': risk_note,
            'daily_profit': daily_profit
        }
    
    def format_deal_alert(self, deal: Dict, deal_id: str) -> str:
        """Clean, scannable deal alert with actionable data"""
        
        metrics = self.calculate_smart_metrics(deal)
        roi = (deal['potential_profit'] / deal['raw_price']) * 100
        
        # Clean title (remove clutter)
        condition = deal.get('condition_notes', 'Unknown condition')
        if len(condition) > 50:
            condition = condition[:47] + "..."
        
        # Calculate all-in cost
        grading_cost = 25  # PSA Regular
        total_investment = deal['raw_price'] + grading_cost
        
        message = f"""🎯 *DEAL #{deal_id}* (Single Deal Focus)

*{deal['card_name']} • {deal['set_name']}*
{condition}

💰 Investment: *${deal['raw_price']:.0f}* + $25 grading = *${total_investment:.0f}*
🎯 Target Sale: *${deal['estimated_psa10_price']:.0f}*
💵 *Net Profit: ${deal['potential_profit']:.0f}* ({roi:.0f}% ROI)

⏱️ *Timeline: ~{metrics['total_days']} days total*
• Grade: {metrics['grading_days']}d • Sell: {metrics['sell_days']}d
• Done by: {metrics['completion_date'].strftime('%b %d, %Y')}
• Daily rate: ${metrics['daily_profit']:.0f}/day

📊 *Market Intel:*
• Demand: {metrics['market_depth']} market
• Confidence: {metrics['confidence']}
• Risk: {metrics['risk_level']}
• Note: {metrics['risk_note']}

⚠️ *Single Deal Strategy* - Focus all capital on one opportunity

{datetime.now().strftime('📅 %I:%M %p • %b %d')}"**  REQUIRES MANUAL APPROVAL **"""

        return message
    
    def create_action_buttons(self, deal_id: str, listing_url: str) -> InlineKeyboardMarkup:
        """Clean action buttons - just BUY/PASS (buttons visual only until webhook)"""
        keyboard = [
            [
                InlineKeyboardButton("✅ APPROVE & BUY", callback_data=f"buy_{deal_id}"),
                InlineKeyboardButton("❌ PASS", callback_data=f"pass_{deal_id}")
            ],
            [
                InlineKeyboardButton("📱 View on eBay", url=listing_url)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def send_deal_alert(self, deal: Dict, deal_id: str) -> bool:
        """Send optimized deal alert"""
        try:
            message = self.format_deal_alert(deal, deal_id)
            buttons = self.create_action_buttons(deal_id, deal.get('listing_url', 'https://ebay.com'))
            
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                reply_markup=buttons,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            print(f"✅ Smart deal alert sent: #{deal_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send deal alert: {e}")
            return False
    
    async def send_session_summary(self, session_stats: Dict) -> bool:
        """Send end-of-session summary"""
        try:
            found = session_stats.get('deals_found', 0)
            alerted = session_stats.get('deals_alerted', 0)
            skipped = session_stats.get('deals_skipped', 0)
            active = session_stats.get('active_deals', 0)
            
            message = f"""📊 *SESSION SUMMARY*

🔍 Deals Found: {found}
🚨 Alerts Sent: {alerted}
⏸️ Skipped (Active Deal): {skipped}

💼 Current Status:
• Active deals: {active}
• Strategy: Single deal focus
• Next scan: {session_stats.get('next_scan', 'TBD')}

{datetime.now().strftime('%I:%M %p • %b %d')"""

            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='Markdown'
            )
            return True
            
        except Exception as e:
            print(f"❌ Failed to send session summary: {e}")
            return False

# Global bot instance
_smart_bot = None

async def send_smart_deal_alert(deal: Dict, deal_id: str) -> bool:
    """Send smart deal alert with enhanced metrics"""
    global _smart_bot
    
    if _smart_bot is None:
        _smart_bot = SmartMVPBot()
    
    return await _smart_bot.send_deal_alert(deal, deal_id)

async def send_session_summary(session_stats: Dict) -> bool:
    """Send session summary"""
    global _smart_bot
    
    if _smart_bot is None:
        _smart_bot = SmartMVPBot()
    
    return await _smart_bot.send_session_summary(session_stats)

# Demo and test functions
async def test_smart_alert():
    """Test the smart alert system"""
    
    print("🧪 Testing Smart MVP Bot")
    print("=" * 30)
    
    # High-value Charizard deal
    test_deal = {
        'card_name': "Charizard",
        'set_name': "Base Set Shadowless", 
        'raw_price': 285.00,
        'estimated_psa10_price': 4200.00,
        'potential_profit': 3890.00,  # After grading costs
        'condition_notes': "Near Mint condition - excellent centering, minor edge wear",
        'listing_url': "https://www.ebay.com/itm/smart_test_001"
    }
    
    # Send smart alert
    success = await send_smart_deal_alert(test_deal, "SMART_001")
    
    if success:
        print("✅ Smart deal alert sent!")
        print("\n🎯 Key Features:")
        print("   📊 Enhanced risk assessment")
        print("   ⏱️ Realistic timeline estimates")
        print("   💰 Daily profit calculations")
        print("   🎯 Market confidence scoring")
        print("   🔍 Single deal focus")
        print("   ✅ Clean 2-button interface")
        
    # Test session summary
    session_stats = {
        'deals_found': 3,
        'deals_alerted': 1,
        'deals_skipped': 2,
        'active_deals': 1,
        'next_scan': '30 minutes'
    }
    
    await asyncio.sleep(1)  # Space out messages
    await send_session_summary(session_stats)
    print("✅ Session summary sent!")

async def test_multiple_deals():
    """Test alerts with different risk profiles"""
    
    deals = [
        {
            'card_name': "Pikachu Illustrator",
            'set_name': "Promo",
            'raw_price': 1250.00,
            'estimated_psa10_price': 15000.00,
            'potential_profit': 13725.00,
            'condition_notes': "Raw card - appears mint but needs verification",
            'listing_url': "https://ebay.com/high_risk"
        },
        {
            'card_name': "Blastoise",
            'set_name': "Base Set", 
            'raw_price': 175.00,
            'estimated_psa10_price': 800.00,
            'potential_profit': 600.00,
            'condition_notes': "PSA 9 with 10 potential - sharp corners, good centering",
            'listing_url': "https://ebay.com/safe_play"
        }
    ]
    
    for i, deal in enumerate(deals):
        await send_smart_deal_alert(deal, f"TEST_{i+1:03d}")
        await asyncio.sleep(2)  # Space out alerts

if __name__ == "__main__":
    print("Smart MVP Bot - Enhanced Alerts")
    print("Choose test:")
    print("1. Single deal test")
    print("2. Multiple risk profiles")
    
    choice = input("Enter choice (1-2): ").strip()
    
    if choice == "2":
        asyncio.run(test_multiple_deals())
    else:
        asyncio.run(test_smart_alert())
