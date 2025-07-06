#!/usr/bin/env python3
"""
MVP Interactive Telegram Bot - Clean, user-friendly deal alerts with working buttons
"""
import os
import asyncio
import logging
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Simple logging
logging.basicConfig(level=logging.INFO)

class MVPTelegramBot:
    """Clean, focused bot for deal approval"""
    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv('TG_TOKEN')
        self.admin_id = int(os.getenv('TG_ADMIN_ID'))
        self.bot = Bot(token=self.token)
    
    def create_deal_message(self, deal: Dict, deal_id: str) -> str:
        """Create clean, scannable deal message"""
        
        # Calculate key metrics
        roi = (deal['potential_profit'] / deal['raw_price']) * 100
        
        # Extract clean title
        title = deal.get('condition_notes', 'Unknown condition')
        if len(title) > 50:
            title = title[:47] + "..."
        
        # Create message with clear visual hierarchy
        message = f"""🎯 *DEAL #{deal_id}*

*{deal['card_name']} • {deal['set_name']}*
`{title}`

💰 *${deal['raw_price']:.0f}* ➜ *${deal['estimated_psa10_price']:.0f}*
🎯 *${deal['potential_profit']:.0f} profit* ({roi:.0f}% ROI)

📊 *Investment Breakdown:*
• Purchase: ${deal['raw_price']:.0f}
• Grading: $25
• *Total Cost: ${deal['raw_price'] + 25:.0f}*

⚡ Quick Decision Required
⏰ {datetime.now().strftime('%H:%M')}"""

        return message
    
    def create_deal_buttons(self, deal_id: str) -> InlineKeyboardMarkup:
        """Create clean action buttons"""
        keyboard = [
            [
                InlineKeyboardButton("✅ BUY", callback_data=f"buy_{deal_id}"),
                InlineKeyboardButton("❌ PASS", callback_data=f"pass_{deal_id}")
            ],
            [
                InlineKeyboardButton("📱 View Listing", url="#"),  # URL will be set dynamically
                InlineKeyboardButton("📊 Details", callback_data=f"info_{deal_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def send_deal_alert(self, deal: Dict, deal_id: str) -> bool:
        """Send formatted deal alert"""
        try:
            message = self.create_deal_message(deal, deal_id)
            
            # Update the View Listing button with actual URL
            keyboard = [
                [
                    InlineKeyboardButton("✅ BUY", callback_data=f"buy_{deal_id}"),
                    InlineKeyboardButton("❌ PASS", callback_data=f"pass_{deal_id}")
                ],
                [
                    InlineKeyboardButton("📱 View Listing", url=deal.get('listing_url', 'https://ebay.com')),
                    InlineKeyboardButton("📊 Details", callback_data=f"info_{deal_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            print(f"✅ Deal alert sent: #{deal_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send alert: {e}")
            return False
    
    async def send_summary_alert(self, deals_found: int, session_profit: float) -> bool:
        """Send session summary when multiple deals found"""
        if deals_found == 0:
            return False
            
        try:
            summary = f"""📈 *SCANNING COMPLETE*

🎯 Found *{deals_found} deals* this session
💰 Total potential: *${session_profit:.0f}*
⏰ {datetime.now().strftime('%H:%M:%S')}

_Review deals above and make decisions._
_Bot will continue monitoring..._"""

            await self.bot.send_message(
                chat_id=self.admin_id,
                text=summary,
                parse_mode='Markdown'
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send summary: {e}")
            return False

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        
        if not query or not query.data:
            return
            
        await query.answer()  # This acknowledges the button tap immediately
        
        callback_data = query.data
        
        try:
            # Parse callback data and handle different actions
            if callback_data.startswith("buy_"):
                deal_id = callback_data.replace("buy_", "")
                await self.handle_buy_action(query, deal_id)
                
            elif callback_data.startswith("pass_"):
                deal_id = callback_data.replace("pass_", "")
                await self.handle_pass_action(query, deal_id)
                
            elif callback_data.startswith("info_"):
                deal_id = callback_data.replace("info_", "")
                await self.handle_info_action(query, deal_id)
                
        except Exception as e:
            print(f"❌ Callback error: {e}")
            await query.answer("❌ Error processing request", show_alert=True)
    
    async def handle_buy_action(self, query, deal_id: str):
        """Handle BUY button press"""
        # Update the message to show approval
        approved_message = f"""✅ *APPROVED - Deal #{deal_id}*

🎯 *PURCHASE AUTHORIZED*
⏰ Approved: {datetime.now().strftime('%H:%M:%S')}

*Next Steps:*
1. 🛒 Buy immediately on eBay
2. 📦 Ship to PSA for grading  
3. 💎 List PSA 10 result

📝 Status: MANUAL PURCHASE REQUIRED
_Proceed with manual purchase on eBay._"""
        
        await query.edit_message_text(
            text=approved_message,
            parse_mode='Markdown'
        )
        
        # Log the approval
        try:
            from deal_logger import DealLogger
            logger = DealLogger()
            logger.update_deal_status(deal_id, "APPROVED", "Manual approval via Telegram")
        except:
            pass  # Don't fail if logging fails
        
        # Show confirmation popup
        await query.answer("✅ Deal approved! Proceed with purchase.", show_alert=True)
        print(f"✅ Deal {deal_id} APPROVED via button tap")
    
    async def handle_pass_action(self, query, deal_id: str):
        """Handle PASS button press"""
        # Update the message to show rejection
        rejected_message = f"""❌ *REJECTED - Deal #{deal_id}*

*Reason:* Manual rejection
⏰ Rejected: {datetime.now().strftime('%H:%M:%S')}

_Continuing search for better deals..._"""
        
        await query.edit_message_text(
            text=rejected_message,
            parse_mode='Markdown'
        )
        
        # Log the rejection
        try:
            from deal_logger import DealLogger
            logger = DealLogger()
            logger.update_deal_status(deal_id, "REJECTED", "Manual rejection via Telegram")
        except:
            pass  # Don't fail if logging fails
        
        # Show confirmation popup
        await query.answer("❌ Deal rejected. Continuing search...", show_alert=True)
        print(f"❌ Deal {deal_id} REJECTED via button tap")
    
    async def handle_info_action(self, query, deal_id: str):
        """Handle INFO button press"""
        # Send detailed info as a new message
        details = f"""📊 *Deal #{deal_id} Details*

*MVP Notice:* Manual purchase required
*Status:* Awaiting decision
*Time:* {datetime.now().strftime('%H:%M:%S')}

For full details, check the original deal message above."""
        
        await query.message.reply_text(
            text=details,
            parse_mode='Markdown'
        )
        
        await query.answer("📊 Details sent below")
        print(f"📊 Info requested for deal {deal_id}")

# Global instance for use by deal finders
_mvp_bot = None

async def send_mvp_deal_alert(deal: Dict, deal_id: str) -> bool:
    """Easy function for deal finders to use"""
    global _mvp_bot
    
    if _mvp_bot is None:
        _mvp_bot = MVPTelegramBot()
    
    return await _mvp_bot.send_deal_alert(deal, deal_id)

async def send_mvp_summary(deals_found: int, session_profit: float) -> bool:
    """Send session summary"""
    global _mvp_bot
    
    if _mvp_bot is None:
        _mvp_bot = MVPTelegramBot()
    
    return await _mvp_bot.send_summary_alert(deals_found, session_profit)

# Test function
async def test_mvp_alert():
    """Test the MVP alert system"""
    test_deal = {
        'card_name': "Charizard",
        'set_name': "Base Set",
        'raw_price': 325.00,
        'estimated_psa10_price': 5000.00,
        'potential_profit': 4650.00,
        'condition_notes': "Shadowless Near Mint - Excellent Centering",
        'listing_url': "https://www.ebay.com/itm/123456789"
    }
    
    bot = MVPTelegramBot()
    await bot.send_deal_alert(test_deal, "MVP_001")
    print("✅ MVP test alert sent!")

if __name__ == "__main__":
    asyncio.run(test_mvp_alert())
