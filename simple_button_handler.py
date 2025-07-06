#!/usr/bin/env python3
"""
Simple Button Handler - Webhook approach for BUY/PASS buttons
"""
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Application, CallbackQueryHandler
from deal_logger import DealLogger

class SimpleButtonHandler:
    """Lightweight button handler"""
    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv('TG_TOKEN')
        self.admin_id = int(os.getenv('TG_ADMIN_ID'))
        self.deal_logger = DealLogger()
        
    async def handle_callback(self, update: Update, context):
        """Handle button presses"""
        query = update.callback_query
        await query.answer()  # Acknowledge immediately
        
        if not query.data:
            return
            
        try:
            if query.data.startswith("approve_"):
                deal_id = query.data.replace("approve_", "")
                await self.handle_approval(query, deal_id)
                
            elif query.data.startswith("reject_"):
                deal_id = query.data.replace("reject_", "")
                await self.handle_rejection(query, deal_id)
                
        except Exception as e:
            print(f"❌ Button error: {e}")
            await query.answer("❌ Error processing", show_alert=True)
    
    async def handle_approval(self, query, deal_id: str):
        """Handle APPROVE button"""
        
        # Update deal status
        self.deal_logger.update_deal_status(deal_id, "APPROVED", "Button approval")
        
        # Create approval message
        approved_message = f"""✅ *DEAL #{deal_id} APPROVED*

🎯 *NEXT ACTIONS:*
1. 🛒 Purchase immediately on eBay
2. 📦 Ship to PSA (use Regular service)
3. ⏱️ Wait ~45 days for grading
4. 💎 List PSA 10 result

⚠️ *CAPITAL LOCKED:*
No new deals until this completes.

📝 *Tracking:*
Deal #{deal_id} is now your active investment.
Monitor progress and update status manually.

⏰ Approved: {datetime.now().strftime('%H:%M:%S')}"""
        
        await query.edit_message_text(
            text=approved_message,
            parse_mode='Markdown'
        )
        
        await query.answer("✅ APPROVED! Proceed with purchase.", show_alert=True)
        print(f"✅ Deal {deal_id} APPROVED - Capital committed")
    
    async def handle_rejection(self, query, deal_id: str):
        """Handle REJECT button"""
        
        # Update deal status  
        self.deal_logger.update_deal_status(deal_id, "REJECTED", "Button rejection")
        
        # Create rejection message
        rejected_message = f"""❌ *DEAL #{deal_id} REJECTED*

*Reason:* Manual rejection via button
⏰ Rejected: {datetime.now().strftime('%H:%M:%S')}

_Capital preserved. Continuing search for better opportunities..._

🔍 *Next Steps:*
System will continue scanning for deals.
Focus on quality over quantity."""
        
        await query.edit_message_text(
            text=rejected_message,
            parse_mode='Markdown'
        )
        
        await query.answer("❌ REJECTED. Continuing search...", show_alert=True)
        print(f"❌ Deal {deal_id} REJECTED - Capital preserved")

async def start_simple_button_handler():
    """Start simple button handler"""
    load_dotenv()
    token = os.getenv('TG_TOKEN')
    
    handler = SimpleButtonHandler()
    
    print("🎯 Starting Simple Button Handler")
    print("=" * 40)
    print("✅ BUY/PASS buttons will now work")
    print("🔄 Listening for button presses...")
    print("💡 Single deal focus enabled")
    print("\nReady to process approvals! 🚀\n")
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add callback handler
    application.add_handler(CallbackQueryHandler(handler.handle_callback))
    
    try:
        # Start polling - this is the key part that was missing
        print("🤖 Bot is now polling for button presses...")
        await application.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\n🛑 Button handler stopped")
    except Exception as e:
        print(f"❌ Handler error: {e}")

if __name__ == "__main__":
    asyncio.run(start_simple_button_handler())
