#!/usr/bin/env python3
"""
Telegram Bot Callback Handler - Handle button presses
"""
import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from deal_logger import DealLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DealCallbackHandler:
    """Handle button callbacks from deal alerts"""
    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv('TG_TOKEN')
        self.admin_id = int(os.getenv('TG_ADMIN_ID'))
        self.deal_logger = DealLogger()
        
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process button callbacks"""
        query = update.callback_query
        
        if not query or not query.data:
            return
            
        await query.answer()  # Acknowledge the callback
        
        callback_data = query.data
        user_id = query.from_user.id
        
        # Security check - only admin can approve deals
        if user_id != self.admin_id:
            await query.answer("❌ Unauthorized", show_alert=True)
            return
            
        try:
            # Parse callback data
            if callback_data.startswith("buy_"):
                deal_id = callback_data.replace("buy_", "")
                await self.handle_buy_decision(query, deal_id)
                
            elif callback_data.startswith("pass_"):
                deal_id = callback_data.replace("pass_", "")
                await self.handle_pass_decision(query, deal_id)
                
            elif callback_data.startswith("info_"):
                deal_id = callback_data.replace("info_", "")
                await self.handle_info_request(query, deal_id)
                
            else:
                await query.answer("❌ Unknown action", show_alert=True)
                
        except Exception as e:
            logger.error(f"Callback error: {e}")
            await query.answer("❌ Error processing request", show_alert=True)
    
    async def handle_buy_decision(self, query, deal_id: str):
        """Handle BUY button press"""
        try:
            # Update deal status in database
            self.deal_logger.update_deal_status(deal_id, "APPROVED", "Manual approval via Telegram")
            
            # Get deal details for confirmation
            deal_info = self.get_deal_info(deal_id)
            
            # Update the message to show approval
            approved_message = f"""✅ *APPROVED - Deal #{deal_id}*

🎯 *PURCHASE AUTHORIZED*
💰 ${deal_info.get('raw_price', 0):.0f} → ${deal_info.get('estimated_psa10_price', 0):.0f}
🎯 ${deal_info.get('potential_profit', 0):.0f} profit target

*Next Steps:*
1. 🛒 Buy immediately on eBay
2. 📦 Ship to PSA for grading
3. 💎 List PSA 10 result

⏰ Approved: {datetime.now().strftime('%H:%M:%S')}
📝 Status: MANUAL PURCHASE REQUIRED

_Proceed with manual purchase on eBay._"""
            
            await query.edit_message_text(
                text=approved_message,
                parse_mode='Markdown'
            )
            
            # Send confirmation
            await query.answer("✅ Deal approved! Proceed with purchase.", show_alert=True)
            
            logger.info(f"Deal {deal_id} APPROVED by user {query.from_user.id}")
            
        except Exception as e:
            logger.error(f"Error handling buy decision: {e}")
            await query.answer("❌ Error approving deal", show_alert=True)
    
    async def handle_pass_decision(self, query, deal_id: str):
        """Handle PASS button press"""
        try:
            # Update deal status in database
            self.deal_logger.update_deal_status(deal_id, "REJECTED", "Manual rejection via Telegram")
            
            # Get deal details
            deal_info = self.get_deal_info(deal_id)
            
            # Update the message to show rejection
            rejected_message = f"""❌ *REJECTED - Deal #{deal_id}*

~~💰 ${deal_info.get('raw_price', 0):.0f} → ${deal_info.get('estimated_psa10_price', 0):.0f}~~
~~🎯 ${deal_info.get('potential_profit', 0):.0f} profit~~

*Reason:* Manual rejection
⏰ Rejected: {datetime.now().strftime('%H:%M:%S')}

_Continuing search for better deals..._"""
            
            await query.edit_message_text(
                text=rejected_message,
                parse_mode='Markdown'
            )
            
            # Send confirmation
            await query.answer("❌ Deal rejected. Continuing search...", show_alert=True)
            
            logger.info(f"Deal {deal_id} REJECTED by user {query.from_user.id}")
            
        except Exception as e:
            logger.error(f"Error handling pass decision: {e}")
            await query.answer("❌ Error rejecting deal", show_alert=True)
    
    async def handle_info_request(self, query, deal_id: str):
        """Handle INFO button press"""
        try:
            deal_info = self.get_deal_info(deal_id)
            
            if not deal_info:
                await query.answer("❌ Deal not found", show_alert=True)
                return
            
            # Create detailed info message
            details = f"""📊 *Deal #{deal_id} Details*

*Card Information:*
• Name: {deal_info.get('card_name', 'Unknown')}
• Set: {deal_info.get('set_name', 'Unknown')}
• Condition: {deal_info.get('condition_notes', 'Not specified')}

*Financial Breakdown:*
• Purchase: ${deal_info.get('raw_price', 0):.2f}
• Grading: $25.00
• Total Cost: ${deal_info.get('raw_price', 0) + 25:.2f}
• Est. PSA 10 Sale: ${deal_info.get('estimated_psa10_price', 0):.2f}
• Net Profit: ${deal_info.get('potential_profit', 0):.2f}
• ROI: {(deal_info.get('potential_profit', 0) / deal_info.get('raw_price', 1)) * 100:.1f}%

*Risk Assessment:*
• Grading Risk: Medium (condition dependent)
• Market Risk: Low (established pricing)
• Time to Sale: 30-60 days estimated

*Listing URL:*
{deal_info.get('listing_url', 'Not available')}

⚠️ *MVP Notice:* Manual purchase required"""
            
            # Send as new message to avoid replacing the original deal
            await query.message.reply_text(
                text=details,
                parse_mode='Markdown'
            )
            
            await query.answer("📊 Details sent below", show_alert=False)
            
        except Exception as e:
            logger.error(f"Error handling info request: {e}")
            await query.answer("❌ Error getting details", show_alert=True)
    
    def get_deal_info(self, deal_id: str) -> dict:
        """Get deal information from database"""
        try:
            import sqlite3
            conn = sqlite3.connect("deals.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT card_name, set_name, raw_price, estimated_psa10_price, 
                       potential_profit, condition_notes, listing_url
                FROM deals WHERE id = ?
            ''', (deal_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'card_name': result[0],
                    'set_name': result[1],
                    'raw_price': result[2],
                    'estimated_psa10_price': result[3],
                    'potential_profit': result[4],
                    'condition_notes': result[5],
                    'listing_url': result[6]
                }
            return {}
            
        except Exception as e:
            logger.error(f"Error getting deal info: {e}")
            return {}
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🎴 *Pokemon Card Deal Bot*\n\n"
            "✅ Callback handler active\n"
            "🔄 Ready to process button taps\n"
            "💰 Deal approvals working\n\n"
            "_Tap buttons on deal alerts to approve/reject!_",
            parse_mode='Markdown'
        )
    
    async def handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        # Get recent deals count
        try:
            import sqlite3
            conn = sqlite3.connect("deals.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM deals WHERE date(timestamp) = date('now')")
            today_deals = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM deals WHERE status = 'APPROVED'")
            approved_deals = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM deals WHERE status = 'REJECTED'")
            rejected_deals = cursor.fetchone()[0]
            
            conn.close()
            
            await update.message.reply_text(
                f"📊 *Bot Status*\n\n"
                f"🔄 Callback Handler: Active\n"
                f"📈 Today's Deals: {today_deals}\n"
                f"✅ Approved: {approved_deals}\n"
                f"❌ Rejected: {rejected_deals}\n"
                f"⏰ Last Update: {datetime.now().strftime('%H:%M:%S')}",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting status: {e}")

async def start_callback_bot():
    """Start the callback handler bot"""
    handler = DealCallbackHandler()
    
    # Create application
    application = Application.builder().token(handler.token).build()
    
    # Add handlers
    application.add_handler(CallbackQueryHandler(handler.handle_callback))
    application.add_handler(CommandHandler("start", handler.handle_start))
    application.add_handler(CommandHandler("status", handler.handle_status))
    
    print("🤖 Starting Telegram callback handler...")
    print("✅ Ready to process button taps!")
    
    # Run the bot
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(start_callback_bot())
