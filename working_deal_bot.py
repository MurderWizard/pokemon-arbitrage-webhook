#!/usr/bin/env python3
"""
MVP Deal Bot with Button Support - Single script solution
"""
import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MVPDealBotWithCallbacks:
    """All-in-one deal bot with working buttons"""
    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv('TG_TOKEN')
        self.admin_id = int(os.getenv('TG_ADMIN_ID'))
        self.pending_deals = {}  # Store deal info for callbacks
        
    def create_deal_message(self, deal: dict, deal_id: str) -> str:
        """Create clean deal message"""
        roi = (deal['potential_profit'] / deal['raw_price']) * 100
        title = deal.get('condition_notes', 'Unknown condition')
        if len(title) > 50:
            title = title[:47] + "..."
        
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
    
    def create_deal_buttons(self, deal_id: str, listing_url: str) -> InlineKeyboardMarkup:
        """Create action buttons"""
        keyboard = [
            [
                InlineKeyboardButton("✅ BUY", callback_data=f"buy_{deal_id}"),
                InlineKeyboardButton("❌ PASS", callback_data=f"pass_{deal_id}")
            ],
            [
                InlineKeyboardButton("📱 View Listing", url=listing_url),
                InlineKeyboardButton("📊 Details", callback_data=f"info_{deal_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def send_deal_alert(self, deal: dict, deal_id: str) -> bool:
        """Send deal alert with working buttons"""
        try:
            # Store deal for callback handling
            self.pending_deals[deal_id] = deal
            
            bot = Bot(token=self.token)
            message = self.create_deal_message(deal, deal_id)
            reply_markup = self.create_deal_buttons(deal_id, deal.get('listing_url', 'https://ebay.com'))
            
            await bot.send_message(
                chat_id=self.admin_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            logger.info(f"Deal alert sent: #{deal_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()  # Acknowledge immediately
        
        callback_data = query.data
        
        try:
            if callback_data.startswith("buy_"):
                deal_id = callback_data.replace("buy_", "")
                await self.handle_buy(query, deal_id)
                
            elif callback_data.startswith("pass_"):
                deal_id = callback_data.replace("pass_", "")
                await self.handle_pass(query, deal_id)
                
            elif callback_data.startswith("info_"):
                deal_id = callback_data.replace("info_", "")
                await self.handle_info(query, deal_id)
                
        except Exception as e:
            logger.error(f"Callback error: {e}")
            await query.answer("❌ Error", show_alert=True)
    
    async def handle_buy(self, query, deal_id: str):
        """Handle BUY button"""
        deal = self.pending_deals.get(deal_id, {})
        
        approved_message = f"""✅ *APPROVED - Deal #{deal_id}*

🎯 *PURCHASE AUTHORIZED*
💰 ${deal.get('raw_price', 0):.0f} approved for purchase

*Next Steps:*
1. 🛒 Buy immediately on eBay
2. 📦 Ship to PSA for grading
3. 💎 List PSA 10 result

⏰ Approved: {datetime.now().strftime('%H:%M:%S')}
📝 Status: MANUAL PURCHASE REQUIRED"""
        
        await query.edit_message_text(text=approved_message, parse_mode='Markdown')
        await query.answer("✅ Deal approved! Proceed with purchase.", show_alert=True)
        
        # Log approval
        try:
            from deal_logger import DealLogger
            logger = DealLogger()
            logger.update_deal_status(deal_id, "APPROVED", "Telegram button approval")
        except:
            pass
        
        logger.info(f"Deal {deal_id} APPROVED")
    
    async def handle_pass(self, query, deal_id: str):
        """Handle PASS button"""
        rejected_message = f"""❌ *REJECTED - Deal #{deal_id}*

*Reason:* Manual rejection
⏰ Rejected: {datetime.now().strftime('%H:%M:%S')}

_Continuing search for better deals..._"""
        
        await query.edit_message_text(text=rejected_message, parse_mode='Markdown')
        await query.answer("❌ Deal rejected. Continuing search...", show_alert=True)
        
        # Log rejection
        try:
            from deal_logger import DealLogger
            logger = DealLogger()
            logger.update_deal_status(deal_id, "REJECTED", "Telegram button rejection")
        except:
            pass
        
        logger.info(f"Deal {deal_id} REJECTED")
    
    async def handle_info(self, query, deal_id: str):
        """Handle INFO button"""
        deal = self.pending_deals.get(deal_id, {})
        
        details = f"""📊 *Deal #{deal_id} Details*

*Card:* {deal.get('card_name', 'Unknown')}
*Set:* {deal.get('set_name', 'Unknown')}
*Purchase:* ${deal.get('raw_price', 0):.2f}
*Est. PSA 10:* ${deal.get('estimated_psa10_price', 0):.2f}
*Profit:* ${deal.get('potential_profit', 0):.2f}
*ROI:* {(deal.get('potential_profit', 0) / deal.get('raw_price', 1)) * 100:.1f}%

*Listing:* {deal.get('listing_url', 'Not available')}

⚠️ *MVP:* Manual purchase required"""
        
        await query.message.reply_text(text=details, parse_mode='Markdown')
        await query.answer("📊 Details sent")
        
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🎴 *Pokemon Deal Bot*\n\n"
            "✅ Buttons are working!\n"
            "🎯 Ready for deal alerts\n"
            "💰 Tap buttons to approve/reject deals",
            parse_mode='Markdown'
        )
    
    async def start_bot_service(self):
        """Start the bot service for handling callbacks"""
        application = Application.builder().token(self.token).build()
        
        # Add handlers
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(CommandHandler("start", self.handle_start))
        
        logger.info("🤖 Starting MVP Deal Bot with button support...")
        logger.info("✅ Ready to process button taps!")
        
        # Start polling
        await application.run_polling()

# Global bot instance
_mvp_bot_with_callbacks = None

async def send_interactive_deal_alert(deal: dict, deal_id: str) -> bool:
    """Send deal alert with working buttons"""
    global _mvp_bot_with_callbacks
    
    if _mvp_bot_with_callbacks is None:
        _mvp_bot_with_callbacks = MVPDealBotWithCallbacks()
    
    return await _mvp_bot_with_callbacks.send_deal_alert(deal, deal_id)

# Test function
async def test_interactive_deal():
    """Test deal with working buttons"""
    test_deal = {
        'card_name': "Charizard",
        'set_name': "Base Set",
        'raw_price': 350.00,
        'estimated_psa10_price': 5000.00,
        'potential_profit': 4625.00,
        'condition_notes': "WORKING BUTTONS TEST - All buttons should respond",
        'listing_url': "https://www.ebay.com/itm/working_test"
    }
    
    print("🧪 Testing Interactive Deal Bot")
    success = await send_interactive_deal_alert(test_deal, "WORK_TEST")
    
    if success:
        print("✅ Interactive deal sent!")
        print("\n🔥 NOW BUTTONS SHOULD WORK!")
        print("   ✅ BUY - Should show approval")
        print("   ❌ PASS - Should show rejection")
        print("   📊 INFO - Should show details")
        print("   📱 VIEW - Should open eBay")
    
    return success

if __name__ == "__main__":
    # Send test deal and start service
    asyncio.run(test_interactive_deal())
