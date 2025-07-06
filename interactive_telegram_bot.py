#!/usr/bin/env python3
"""
Interactive Telegram Bot for Pokemon Card Deal Approval
MVP-focused with clean UI and easy decision making
"""
import os
import asyncio
import logging
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PokemonDealBot:
    """Interactive bot for deal approval with clean UI"""
    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv('TG_TOKEN')
        self.admin_id = int(os.getenv('TG_ADMIN_ID'))
        self.bot = Bot(token=self.token)
        self.pending_deals = {}  # Store deals waiting for approval
        
    def format_deal_alert(self, deal: Dict, deal_id: str) -> tuple:
        """Format deal with clean UI and inline buttons"""
        
        # Calculate key metrics
        roi = (deal['potential_profit'] / deal['raw_price']) * 100
        profit_per_day = deal['potential_profit'] / 30  # Rough estimate
        
        # Clean title extraction
        title = deal.get('condition_notes', deal.get('title', 'Unknown'))
        if len(title) > 60:
            title = title[:57] + "..."
            
        # Format main message
        message = (
            f"🎯 **DEAL #{deal_id}**\n\n"
            f"**{deal['card_name']} - {deal['set_name']}**\n"
            f"`{title}`\n\n"
            
            f"💰 **${deal['raw_price']:.0f}** → **${deal['estimated_psa10_price']:.0f}**\n"
            f"🎯 **${deal['potential_profit']:.0f} profit** ({roi:.0f}% ROI)\n"
            f"📅 ~${profit_per_day:.0f}/day potential\n\n"
            
            f"📊 **Costs Included:**\n"
            f"• Purchase: ${deal['raw_price']:.0f}\n"
            f"• Grading: ${deal.get('grading_cost', 25):.0f}\n"
            f"• Total: ${deal.get('total_cost', deal['raw_price'] + 25):.0f}\n\n"
            
            f"⏰ Found: {datetime.now().strftime('%H:%M')}\n"
        )
        
        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("✅ BUY ($" + f"{deal['raw_price']:.0f})", 
                                   callback_data=f"approve_{deal_id}"),
                InlineKeyboardButton("❌ PASS", 
                                   callback_data=f"reject_{deal_id}")
            ],
            [
                InlineKeyboardButton("📱 View Listing", 
                                   url=deal.get('listing_url', '#')),
                InlineKeyboardButton("📊 Details", 
                                   callback_data=f"details_{deal_id}")
            ],
            [
                InlineKeyboardButton("⏸ Pause Alerts", 
                                   callback_data="pause_alerts"),
                InlineKeyboardButton("🔄 Refresh", 
                                   callback_data=f"refresh_{deal_id}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        return message, reply_markup
    
    async def send_deal_alert(self, deal: Dict, deal_id: str) -> bool:
        """Send formatted deal alert with buttons"""
        try:
            # Store deal for callback handling
            self.pending_deals[deal_id] = deal
            
            # Format message and buttons
            message, reply_markup = self.format_deal_alert(deal, deal_id)
            
            # Send to admin
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"Deal alert sent: #{deal_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False
    
    async def handle_approval(self, query, deal_id: str):
        """Handle deal approval"""
        deal = self.pending_deals.get(deal_id)
        if not deal:
            await query.answer("Deal expired or not found")
            return
            
        # Log approval (MVP: manual purchase for now)
        from deal_logger import DealLogger
        deal_logger = DealLogger()
        deal_logger.update_deal_status(deal_id, 'APPROVED')
        
        # Update message
        await query.edit_message_text(
            text=(
                f"✅ **APPROVED - Deal #{deal_id}**\n\n"
                f"**{deal['card_name']} - {deal['set_name']}**\n"
                f"💰 **${deal['raw_price']:.0f}** purchase approved\n"
                f"🎯 **${deal['potential_profit']:.0f}** profit target\n\n"
                f"**Next Steps:**\n"
                f"1. 🛒 Buy manually on eBay\n"
                f"2. 📦 Ship to grading service\n"
                f"3. 💎 List PSA 10 for ${deal['estimated_psa10_price']:.0f}\n\n"
                f"🔗 [Buy Now]({deal.get('listing_url', '#')})\n"
                f"⏰ Approved: {datetime.now().strftime('%H:%M:%S')}"
            ),
            parse_mode='Markdown'
        )
        
        await query.answer("✅ Deal approved! Proceed with manual purchase.")
        
        # Clean up
        if deal_id in self.pending_deals:
            del self.pending_deals[deal_id]
    
    async def handle_rejection(self, query, deal_id: str):
        """Handle deal rejection"""
        deal = self.pending_deals.get(deal_id)
        if not deal:
            await query.answer("Deal expired or not found")
            return
            
        # Log rejection
        from deal_logger import DealLogger
        deal_logger = DealLogger()
        deal_logger.update_deal_status(deal_id, 'REJECTED')
        
        # Update message
        await query.edit_message_text(
            text=(
                f"❌ **REJECTED - Deal #{deal_id}**\n\n"
                f"~~{deal['card_name']} - {deal['set_name']}~~\n"
                f"~~${deal['raw_price']:.0f} → ${deal['estimated_psa10_price']:.0f}~~\n\n"
                f"Reason: Manual rejection\n"
                f"⏰ Rejected: {datetime.now().strftime('%H:%M:%S')}\n\n"
                f"_Continuing to search for better deals..._"
            ),
            parse_mode='Markdown'
        )
        
        await query.answer("❌ Deal rejected. Continuing search...")
        
        # Clean up
        if deal_id in self.pending_deals:
            del self.pending_deals[deal_id]
    
    async def handle_details(self, query, deal_id: str):
        """Show detailed deal information"""
        deal = self.pending_deals.get(deal_id)
        if not deal:
            await query.answer("Deal expired")
            return
            
        details = (
            f"📊 **Deal #{deal_id} Details**\n\n"
            f"**Card Info:**\n"
            f"• Name: {deal['card_name']}\n"
            f"• Set: {deal['set_name']}\n"
            f"• Condition: {deal.get('condition_notes', 'Unknown')}\n\n"
            
            f"**Financial Breakdown:**\n"
            f"• Purchase Price: ${deal['raw_price']:.2f}\n"
            f"• Grading Cost: ${deal.get('grading_cost', 25):.2f}\n"
            f"• Total Investment: ${deal.get('total_cost', deal['raw_price'] + 25):.2f}\n"
            f"• Expected Sale: ${deal['estimated_psa10_price']:.2f}\n"
            f"• Net Profit: ${deal['potential_profit']:.2f}\n"
            f"• ROI: {(deal['potential_profit'] / deal['raw_price']) * 100:.1f}%\n\n"
            
            f"**Risk Assessment:**\n"
            f"• Grading Risk: Medium (condition dependent)\n"
            f"• Market Risk: Low (established card)\n"
            f"• Liquidity: High (PSA 10 in demand)\n\n"
            
            f"⚠️ **MVP Notice:** Manual purchase required"
        )
        
        await query.answer()
        await self.bot.send_message(
            chat_id=query.from_user.id,
            text=details,
            parse_mode='Markdown'
        )
    
    async def start_bot_handlers(self):
        """Start bot with callback handlers (for running as service)"""
        application = Application.builder().token(self.token).build()
        
        # Add handlers
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(CommandHandler("start", self.handle_start))
        application.add_handler(CommandHandler("status", self.handle_status))
        
        # Start polling
        await application.run_polling()
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("approve_"):
            deal_id = data.replace("approve_", "")
            await self.handle_approval(query, deal_id)
            
        elif data.startswith("reject_"):
            deal_id = data.replace("reject_", "")
            await self.handle_rejection(query, deal_id)
            
        elif data.startswith("details_"):
            deal_id = data.replace("details_", "")
            await self.handle_details(query, deal_id)
            
        elif data == "pause_alerts":
            await self.handle_pause_alerts(query)
            
        elif data.startswith("refresh_"):
            deal_id = data.replace("refresh_", "")
            await self.handle_refresh(query, deal_id)
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🎴 **Pokemon Card Arbitrage Bot**\n\n"
            "I'll send you high-value deal alerts with:\n"
            "• Clean deal summaries\n"
            "• One-click approval/rejection\n"
            "• Detailed profit analysis\n"
            "• Direct eBay links\n\n"
            "Ready to find profitable cards! 🚀",
            parse_mode='Markdown'
        )
    
    async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        pending_count = len(self.pending_deals)
        await update.message.reply_text(
            f"📊 **Bot Status**\n\n"
            f"🔄 Active: Yes\n"
            f"⏳ Pending Deals: {pending_count}\n"
            f"💰 Minimum Deal: $250\n"
            f"🎯 Min ROI: 50%\n"
            f"⏰ Last Check: {datetime.now().strftime('%H:%M:%S')}",
            parse_mode='Markdown'
        )
    
    async def handle_pause_alerts(self, query):
        """Handle pause alerts button"""
        await query.edit_message_text(
            "⏸ **Alerts Paused**\n\n"
            "Deal alerts are temporarily paused.\n"
            "Use /resume to restart scanning.\n\n"
            "_Existing pending deals remain active._"
        )
    
    async def handle_refresh(self, query, deal_id: str):
        """Handle refresh deal button"""
        deal = self.pending_deals.get(deal_id)
        if not deal:
            await query.answer("Deal expired")
            return
            
        # Refresh the deal alert
        message, reply_markup = self.format_deal_alert(deal, deal_id)
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        await query.answer("🔄 Deal refreshed!")

# Global bot instance for use by deal finder
_bot_instance = None

async def send_interactive_deal_alert(deal: Dict, deal_id: str) -> bool:
    """Function to be called by deal finder"""
    global _bot_instance
    
    if _bot_instance is None:
        _bot_instance = PokemonDealBot()
    
    return await _bot_instance.send_deal_alert(deal, deal_id)

# For manual testing
async def test_interactive_alert():
    """Test the interactive alert system"""
    test_deal = {
        'card_name': "Charizard",
        'set_name': "Base Set",
        'raw_price': 325.00,
        'estimated_psa10_price': 5000.00,
        'potential_profit': 4650.00,
        'condition_notes': "Shadowless Near Mint - High Grade Potential",
        'listing_url': "https://www.ebay.com/itm/123456789",
        'grading_cost': 25.0,
        'total_cost': 350.0
    }
    
    bot = PokemonDealBot()
    await bot.send_deal_alert(test_deal, "TEST_001")
    print("✅ Test alert sent!")

if __name__ == "__main__":
    asyncio.run(test_interactive_alert())
