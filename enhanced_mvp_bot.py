#!/usr/bin/env python3
"""
Enhanced MVP Telegram Bot - Focused on single deal lifecycle with smart metrics
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

class EnhancedMVPBot:
    """Smart bot for low-capital, high-accuracy arbitrage"""
    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv('TG_TOKEN')
        self.admin_id = int(os.getenv('TG_ADMIN_ID'))
        self.bot = Bot(token=self.token)
        
    def calculate_timeline_metrics(self, deal: Dict) -> Dict:
        """Calculate realistic timelines and velocity"""
        
        # PSA Grading Timeline (current estimates)
        grading_days = 45  # PSA Regular service
        
        # Market velocity estimates based on card type
        card_name = deal.get('card_name', '').lower()
        if 'charizard' in card_name:
            sell_velocity = 7  # High demand
            market_depth = "Deep"
        elif 'pikachu' in card_name:
            sell_velocity = 14  # Medium demand  
            market_depth = "Medium"
        else:
            sell_velocity = 30  # Standard
            market_depth = "Standard"
            
        # Risk assessment
        roi = (deal['potential_profit'] / deal['raw_price']) * 100
        if roi > 1000:  # Over 10x return
            risk_level = "High (too good to be true?)"
        elif roi > 500:  # 5-10x return
            risk_level = "Medium-High (verify condition)"
        elif roi > 200:  # 2-5x return  
            risk_level = "Medium (good opportunity)"
        else:
            risk_level = "Low (conservative)"
            
        total_days = grading_days + sell_velocity
        completion_date = datetime.now() + timedelta(days=total_days)
        
        return {
            'grading_days': grading_days,
            'sell_velocity': sell_velocity,
            'total_days': total_days,
            'completion_date': completion_date,
            'market_depth': market_depth,
            'risk_level': risk_level
        }
    
    def create_enhanced_deal_message(self, deal: Dict, deal_id: str) -> str:
        """Create comprehensive deal alert with lifecycle info"""
        
        # Calculate metrics
        metrics = self.calculate_timeline_metrics(deal)
        roi = (deal['potential_profit'] / deal['raw_price']) * 100
        
        # Extract clean title
        title = deal.get('condition_notes', 'Unknown condition')
        if len(title) > 45:
            title = title[:42] + "..."
        
        # Calculate daily profit rate
        daily_profit = deal['potential_profit'] / metrics['total_days']
        
        message = f"""🎯 *DEAL #{deal_id}* - Single Deal Focus

*{deal['card_name']} • {deal['set_name']}*
`{title}`

💰 *${deal['raw_price']:.0f}* ➜ *${deal['estimated_psa10_price']:.0f}*
🎯 *${deal['potential_profit']:.0f} profit* ({roi:.0f}% ROI)

📊 *Investment Analysis:*
• Purchase: ${deal['raw_price']:.0f}
• Grading: $25 (PSA Regular)
• *Total Risk: ${deal['raw_price'] + 25:.0f}*

⏱️ *Timeline Estimate:*
• Grading: {metrics['grading_days']} days
• Sell Time: {metrics['sell_velocity']} days  
• *Total: ~{metrics['total_days']} days*
• Done by: {metrics['completion_date'].strftime('%b %d')}

📈 *Market Intelligence:*
• Velocity: {metrics['market_depth']} market
• Risk Level: {metrics['risk_level']}
• Daily Rate: ${daily_profit:.0f}/day

⚠️ *Single Deal Strategy*
Focus capital on one opportunity at a time

⏰ {datetime.now().strftime('%H:%M')}"""

        return message
    
    def create_simple_buttons(self, deal_id: str, listing_url: str) -> InlineKeyboardMarkup:
        """Simple 2-button approach"""
        keyboard = [
            [
                InlineKeyboardButton("✅ APPROVE & BUY", callback_data=f"approve_{deal_id}"),
                InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{deal_id}")
            ],
            [
                InlineKeyboardButton("📱 View eBay Listing", url=listing_url)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def send_enhanced_deal_alert(self, deal: Dict, deal_id: str) -> bool:
        """Send enhanced deal alert with lifecycle info"""
        try:
            message = self.create_enhanced_deal_message(deal, deal_id)
            reply_markup = self.create_simple_buttons(deal_id, deal.get('listing_url', 'https://ebay.com'))
            
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            print(f"✅ Enhanced deal alert sent: #{deal_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send enhanced alert: {e}")
            return False
    
    async def send_capital_management_alert(self, current_deals: int, total_exposure: float) -> bool:
        """Alert about capital management"""
        if current_deals >= 1:  # Single deal strategy
            message = f"""⚠️ *CAPITAL MANAGEMENT ALERT*

Currently managing: {current_deals} active deal(s)
Total exposure: ${total_exposure:.0f}

*Single Deal Strategy:*
Wait for current deal to complete before approving new ones.

This ensures:
• Proper risk management
• Full lifecycle learning
• Capital preservation
• Quality over quantity

_New deals will be logged but not approved until current deal completes._"""

            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='Markdown'
            )
            return True
        return False

# Global bot instance
_enhanced_bot = None

async def send_enhanced_deal_alert(deal: Dict, deal_id: str) -> bool:
    """Send enhanced deal alert"""
    global _enhanced_bot
    
    if _enhanced_bot is None:
        _enhanced_bot = EnhancedMVPBot()
    
    return await _enhanced_bot.send_enhanced_deal_alert(deal, deal_id)

async def check_capital_management(current_deals: int = 0, total_exposure: float = 0) -> bool:
    """Check if we should pause new approvals"""
    global _enhanced_bot
    
    if _enhanced_bot is None:
        _enhanced_bot = EnhancedMVPBot()
    
    return await _enhanced_bot.send_capital_management_alert(current_deals, total_exposure)

# Test the enhanced system
async def test_enhanced_deal():
    """Test enhanced deal alert"""
    
    print("🧪 Testing Enhanced MVP Bot")
    print("=" * 35)
    
    test_deal = {
        'card_name': "Charizard",
        'set_name': "Base Set", 
        'raw_price': 299.00,
        'estimated_psa10_price': 4800.00,
        'potential_profit': 4476.00,
        'condition_notes': "Shadowless Near Mint - Excellent centering, clean edges",
        'listing_url': "https://www.ebay.com/itm/enhanced_test"
    }
    
    # Send enhanced alert
    success = await send_enhanced_deal_alert(test_deal, "ENH_001")
    
    if success:
        print("✅ Enhanced deal alert sent!")
        print("\n🎯 New Features:")
        print("   ⏱️ Grading timeline (45 days)")
        print("   📈 Sell velocity estimate")
        print("   🎲 Risk assessment")
        print("   💰 Daily profit rate")
        print("   📅 Completion date")
        print("   🔍 Market depth analysis")
        print("\n💡 Single Deal Focus!")
    
    # Test capital management
    await check_capital_management(current_deals=1, total_exposure=299.0)
    print("✅ Capital management alert sent!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_deal())
