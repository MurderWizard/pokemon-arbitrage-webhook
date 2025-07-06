#!/usr/bin/env python3
"""
Command-based Deal Approval Bot
Simple, reliable automation using /approve and /pass commands
"""
import os
import asyncio
import logging
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from pending_deals_storage import save_pending_deal, load_pending_deals, get_pending_deal, remove_pending_deal, get_latest_deal_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandApprovalBot:
    """Simple command-based deal approval system"""
    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv('TG_TOKEN')
        self.admin_id = int(os.getenv('TG_ADMIN_ID'))
        self.bot = Bot(token=self.token)
        self.pending_deals = {}  # Store deals waiting for decision
        self.last_deal_id = None  # Track most recent deal for quick commands
        
    def create_deal_message(self, deal: Dict, deal_id: str) -> str:
        """Create clean deal message with command instructions"""
        roi = (deal['potential_profit'] / deal['raw_price']) * 100
        
        # Clean title
        title = deal.get('condition_notes', 'Unknown condition')
        if len(title) > 50:
            title = title[:47] + "..."
        
        message = f"""🎯 **DEAL #{deal_id}** (Command Approval)

**{deal['card_name']} • {deal['set_name']}**
`{title}`

💰 **${deal['raw_price']:.0f}** ➜ **${deal['estimated_psa10_price']:.0f}**
🎯 **${deal['potential_profit']:.0f} profit** ({roi:.0f}% ROI)

📊 **Investment:**
• Purchase: ${deal['raw_price']:.0f}
• Grading: $25
• **Total Cost: ${deal['raw_price'] + 25:.0f}**

⚡ **COMMANDS:**
• `/approve {deal_id}` - Approve this deal
• `/pass {deal_id}` - Reject this deal
• `/approve` - Approve latest deal (#{deal_id})
• `/pass` - Reject latest deal (#{deal_id})

🔗 [View Listing]({deal.get('listing_url', 'https://ebay.com')})

⏰ {datetime.now().strftime('%H:%M')}"""
        
        return message
    
    async def send_deal_alert(self, deal: Dict, deal_id: str) -> bool:
        """Send deal alert with command instructions"""
        try:
            # Store deal in persistent storage
            save_pending_deal(deal_id, deal)
            
            message = self.create_deal_message(deal, deal_id)
            
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            logger.info(f"Deal alert sent: #{deal_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False
    
    async def handle_approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /approve command"""
        args = context.args
        
        # Determine which deal to approve
        if args:
            deal_id = args[0].upper()
        else:
            deal_id = get_latest_deal_id()
            if not deal_id:
                await update.message.reply_text(
                    "❌ No recent deals found.\n"
                    "Usage: `/approve DEAL_ID` or send a deal first",
                    parse_mode='Markdown'
                )
                return
        
        # Check if deal exists
        deal = get_pending_deal(deal_id)
        if not deal:
            await update.message.reply_text(
                f"❌ Deal #{deal_id} not found or already processed.\n"
                f"Use `/pending` to see available deals.",
                parse_mode='Markdown'
            )
            return
        
        # Process approval
        # Log approval
        try:
            from deal_logger import DealLogger
            deal_logger = DealLogger()
            deal_logger.update_deal_status(deal_id, "APPROVED", "Command approval")
        except Exception as e:
            logger.warning(f"Failed to log approval: {e}")
        
        # Send confirmation
        approved_message = f"""✅ **DEAL #{deal_id} APPROVED** 

🚨🚨🚨 **CRITICAL: THIS IS SIMULATION ONLY** 🚨🚨🚨
🚨🚨🚨 **NO MONEY WILL BE SPENT BY THIS BOT** 🚨🚨🚨
🚨🚨🚨 **NO AUTOMATIC PURCHASES EVER** 🚨🚨🚨

🎯 **WHAT JUST HAPPENED:**
• Deal #{deal_id} marked as "approved" in tracking system
• ${deal['raw_price']:.0f} tagged for potential manual purchase
• **ZERO dollars spent automatically**
• **ZERO payment methods connected**
• **ZERO risk of accidental purchases**

⚠️ **IF YOU WANT TO ACTUALLY BUY THIS CARD:**
1. 🛒 YOU must manually visit: {deal.get('listing_url', 'https://ebay.com')}
2. 🏦 YOU must manually pay with YOUR payment method
3. 📦 YOU must manually ship to PSA
4. 💎 YOU must manually list PSA 10 result

🚨 **SAFETY GUARANTEES:**
• ✅ Bot has NO payment information
• ✅ Bot has NO eBay purchasing ability  
• ✅ Bot has NO automatic spending capability
• ✅ Bot ONLY tracks your decisions
• ✅ 100% manual action required for any purchases

📝 **What was logged:** Deal #{deal_id} approval decision
⏰ Approved: {datetime.now().strftime('%H:%M:%S')}

_This approval is TRACKING ONLY - no financial impact whatsoever._"""
        
        await update.message.reply_text(
            approved_message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
        # Remove from pending
        remove_pending_deal(deal_id)
        logger.info(f"Deal {deal_id} APPROVED via command")
    
    async def handle_pass_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pass command"""
        args = context.args
        
        # Determine which deal to pass
        if args:
            deal_id = args[0].upper()
        else:
            deal_id = get_latest_deal_id()
            if not deal_id:
                await update.message.reply_text(
                    "❌ No recent deals found.\n"
                    "Usage: `/pass DEAL_ID` or send a deal first",
                    parse_mode='Markdown'
                )
                return
        
        # Check if deal exists
        deal = get_pending_deal(deal_id)
        if not deal:
            await update.message.reply_text(
                f"❌ Deal #{deal_id} not found or already processed.\n"
                f"Use `/pending` to see available deals.",
                parse_mode='Markdown'
            )
            return
        
        # Process rejection
        # Log rejection
        try:
            from deal_logger import DealLogger
            deal_logger = DealLogger()
            deal_logger.update_deal_status(deal_id, "REJECTED", "Command rejection")
        except Exception as e:
            logger.warning(f"Failed to log rejection: {e}")
        
        # Send confirmation
        rejected_message = f"""❌ **DEAL #{deal_id} PASSED**

~~{deal['card_name']} • {deal['set_name']}~~
~~${deal['raw_price']:.0f} → ${deal['estimated_psa10_price']:.0f}~~

**Reason:** Manual rejection
⏰ Rejected: {datetime.now().strftime('%H:%M:%S')}

🔍 Continuing search for better opportunities..."""
        
        await update.message.reply_text(
            rejected_message,
            parse_mode='Markdown'
        )
        
        # Remove from pending
        remove_pending_deal(deal_id)
        logger.info(f"Deal {deal_id} REJECTED via command")
        
        # Clean up
        del self.pending_deals[deal_id]
        logger.info(f"Deal {deal_id} REJECTED via command")
    
    async def handle_pending_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pending command - show all pending deals"""
        pending_deals = load_pending_deals()
        
        if not pending_deals:
            await update.message.reply_text(
                "📭 **No pending deals**\n\n"
                "All deals have been processed or no new deals found.\n"
                "Bot is monitoring for new opportunities...",
                parse_mode='Markdown'
            )
            return
        
        pending_list = "⏳ **PENDING DEALS**\n\n"
        
        for deal_id, deal in pending_deals.items():
            roi = (deal['potential_profit'] / deal['raw_price']) * 100
            pending_list += (
                f"🎯 **#{deal_id}** - {deal['card_name']}\n"
                f"   💰 ${deal['raw_price']:.0f} → ${deal['estimated_psa10_price']:.0f}\n"
                f"   🎯 ${deal['potential_profit']:.0f} ({roi:.0f}% ROI)\n\n"
            )
        
        latest_deal_id = get_latest_deal_id()
        pending_list += (
            f"**Commands:**\n"
            f"• `/approve DEAL_ID` - Approve specific deal\n"
            f"• `/pass DEAL_ID` - Reject specific deal\n"
            f"• `/approve` - Approve latest (#{latest_deal_id})\n"
            f"• `/pass` - Reject latest (#{latest_deal_id})"
        )
        
        await update.message.reply_text(
            pending_list,
            parse_mode='Markdown'
        )
    
    async def handle_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        pending_count = len(self.pending_deals)
        
        status_message = f"""📊 **ARBITRAGE BOT STATUS**

🔄 **Active:** Command approval mode
⏳ **Pending Deals:** {pending_count}
🎯 **Latest Deal:** #{self.last_deal_id or 'None'}
💰 **Min Deal Value:** $250
📈 **Min ROI:** 50%

**Available Commands:**
• `/pending` - Show pending deals
• `/approve [ID]` - Approve deal
• `/pass [ID]` - Reject deal
• `/help` - Show all commands

⏰ **Status Time:** {datetime.now().strftime('%H:%M:%S')}"""
        
        await update.message.reply_text(
            status_message,
            parse_mode='Markdown'
        )
    
    async def handle_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """🎴 **POKEMON ARBITRAGE BOT (SAFE MVP TEST MODE)**

🚨🚨🚨 **ABSOLUTE SAFETY GUARANTEE** 🚨🚨🚨
🚨 **THIS BOT CANNOT AND WILL NOT SPEND MONEY** 🚨
🚨 **NO PAYMENT METHODS ARE CONNECTED** 🚨
🚨 **NO AUTOMATIC PURCHASES POSSIBLE** 🚨

**What this bot does:**
✅ Finds potentially profitable Pokemon card deals
✅ Tracks your approval/rejection decisions  
✅ Logs deal outcomes for analysis
✅ **NOTHING ELSE - NO MONEY INVOLVED**

**Commands (ALL SAFE - NO FINANCIAL IMPACT):**
• `/approve` - Mark latest deal approved (TRACKING ONLY)
• `/approve DEAL_ID` - Mark specific deal approved
• `/pass` - Mark latest deal rejected
• `/pass DEAL_ID` - Mark specific deal rejected
• `/pending` - Show deals awaiting decision
• `/status` - Bot status & stats
• `/help` - This help message

**How the SAFE workflow works:**
1. 🤖 Bot finds deal and sends alert
2. 📱 You decide: `/approve` or `/pass` 
3. 📝 Bot logs your decision (NO MONEY SPENT)
4. 🛒 **IF you want to buy: YOU manually go to eBay**
5. 💳 **YOU manually pay with YOUR payment method**

**What happens when you type `/approve`:**
• ✅ Deal marked "approved" in tracking system
• ✅ Approval logged with timestamp  
• ✅ **ZERO money spent**
• ✅ **ZERO automatic actions**
• ✅ **100% safe decision tracking**

🚨 **FINANCIAL SAFETY FEATURES:**
• 🔒 No payment info stored
• 🔒 No eBay purchase capability
• 🔒 No automatic spending
• 🔒 No credit card access
• 🔒 No bank account access
• 🔒 Pure decision tracking only

🚀 **This is a 100% safe testing environment!**
_No financial risk whatsoever - only tracks your decisions._"""
        
        await update.message.reply_text(
            help_message,
            parse_mode='Markdown'
        )
    
    async def start_command_handler(self):
        """Start the command handler bot"""
        try:
            application = Application.builder().token(self.token).build()
            
            # Add command handlers
            application.add_handler(CommandHandler("approve", self.handle_approve_command))
            application.add_handler(CommandHandler("pass", self.handle_pass_command))
            application.add_handler(CommandHandler("pending", self.handle_pending_command))
            application.add_handler(CommandHandler("status", self.handle_status_command))
            application.add_handler(CommandHandler("help", self.handle_help_command))
            application.add_handler(CommandHandler("start", self.handle_help_command))
            
            logger.info("🤖 Command approval bot started")
            logger.info("📋 Available commands: /approve, /pass, /pending, /status, /help")
            
            # Start polling
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            
            # Keep running
            await asyncio.Event().wait()
            
        except Exception as e:
            logger.error(f"Failed to start command handler: {e}")

# Global bot instance
_command_bot = None

async def send_command_deal_alert(deal: Dict, deal_id: str) -> bool:
    """Send deal alert with command-based approval"""
    global _command_bot
    
    if _command_bot is None:
        _command_bot = CommandApprovalBot()
    
    return await _command_bot.send_deal_alert(deal, deal_id)

async def start_command_bot_service():
    """Start the command bot as a service"""
    global _command_bot
    
    if _command_bot is None:
        _command_bot = CommandApprovalBot()
    
    await _command_bot.start_command_handler()

# Test function
async def test_command_approval():
    """Test the command approval system"""
    test_deal = {
        'card_name': "Charizard",
        'set_name': "Base Set",
        'raw_price': 325.00,
        'estimated_psa10_price': 4500.00,
        'potential_profit': 4150.00,
        'condition_notes': "Near Mint condition - excellent centering, sharp corners",
        'listing_url': "https://www.ebay.com/itm/example"
    }
    
    await send_command_deal_alert(test_deal, "CMD001")
    print("✅ Test deal sent! Try:")
    print("   /approve CMD001")
    print("   /pass CMD001") 
    print("   /pending")

if __name__ == "__main__":
    print("🎴 Command-based Deal Approval Bot")
    print("Starting bot service...")
    asyncio.run(start_command_bot_service())
