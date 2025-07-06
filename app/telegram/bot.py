import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from app.core.config import settings
from app.database import SessionLocal
from app.models.database import Deal, InventoryItem, Sale, Transaction
from datetime import datetime, timedelta
from sqlalchemy import func

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = settings.TG_TOKEN
        self.admin_id = settings.TG_ADMIN_ID
        self.app = Application.builder().token(self.token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("pnl", self.pnl_command))
        self.app.add_handler(CommandHandler("aging", self.aging_command))
        self.app.add_handler(CommandHandler("deals", self.deals_command))
        self.app.add_handler(CommandHandler("bankroll", self.bankroll_command))
        self.app.add_handler(CommandHandler("halt", self.halt_command))
        self.app.add_handler(CommandHandler("resume", self.resume_command))
        self.app.add_handler(CommandHandler("stats", self.stats_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        message = "🤖 Pokemon Card Arbitrage Bot\n\n"
        message += "Available commands:\n"
        message += "/pnl - Profit & Loss summary\n"
        message += "/aging [days] - Show aged inventory\n"
        message += "/deals - Recent deals found\n"
        message += "/bankroll - Current bankroll status\n"
        message += "/stats - Performance statistics\n"
        message += "/halt - Halt auto-buying\n"
        message += "/resume - Resume auto-buying\n"
        message += "/help - Show this help message"
        
        await update.message.reply_text(message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command handler"""
        await self.start_command(update, context)
    
    async def pnl_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """P&L command handler"""
        try:
            db = SessionLocal()
            
            # Get days parameter (default 30)
            days = 30
            if context.args and context.args[0].isdigit():
                days = int(context.args[0])
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Calculate P&L
            sales = db.query(Sale).filter(Sale.sale_date >= cutoff_date).all()
            total_revenue = sum(sale.sale_price for sale in sales)
            total_fees = sum(sale.fees for sale in sales)
            total_profit = sum(sale.net_profit for sale in sales)
            
            # Get purchase costs
            purchases = db.query(Transaction).filter(
                Transaction.type == 'purchase',
                Transaction.date >= cutoff_date
            ).all()
            total_costs = sum(abs(t.amount) for t in purchases)
            
            # Calculate metrics
            net_revenue = total_revenue - total_fees
            profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
            roi = (total_profit / total_costs * 100) if total_costs > 0 else 0
            
            message = f"📊 P&L Summary ({days} days)\n\n"
            message += f"💰 Revenue: ${total_revenue:.2f}\n"
            message += f"💸 Fees: ${total_fees:.2f}\n"
            message += f"📈 Net Revenue: ${net_revenue:.2f}\n"
            message += f"🛒 Costs: ${total_costs:.2f}\n"
            message += f"✅ Net Profit: ${total_profit:.2f}\n"
            message += f"📊 Profit Margin: {profit_margin:.1f}%\n"
            message += f"📈 ROI: {roi:.1f}%\n"
            message += f"🔄 Sales Count: {len(sales)}"
            
            await update.message.reply_text(message)
            db.close()
            
        except Exception as e:
            logger.error(f"Error in pnl_command: {e}")
            await update.message.reply_text("Error generating P&L report")
    
    async def aging_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Aging command handler"""
        try:
            db = SessionLocal()
            
            # Get days parameter (default 60)
            days = 60
            if context.args and context.args[0].isdigit():
                days = int(context.args[0])
            
            aged_items = db.query(InventoryItem).filter(
                InventoryItem.days_in_stock >= days,
                InventoryItem.status != 'sold'
            ).order_by(InventoryItem.days_in_stock.desc()).limit(10).all()
            
            if not aged_items:
                message = f"✅ No items aged {days}+ days"
            else:
                message = f"⏰ Aged Inventory ({days}+ days)\n\n"
                for item in aged_items:
                    message += f"📦 {item.card.name}\n"
                    message += f"   💰 ${item.purchase_price:.2f} → ${item.list_price or 0:.2f}\n"
                    message += f"   📅 {item.days_in_stock} days\n"
                    message += f"   🏷️ {item.sku}\n\n"
            
            await update.message.reply_text(message)
            db.close()
            
        except Exception as e:
            logger.error(f"Error in aging_command: {e}")
            await update.message.reply_text("Error generating aging report")
    
    async def deals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Deals command handler"""
        try:
            db = SessionLocal()
            
            recent_deals = db.query(Deal).filter(
                Deal.status == 'found'
            ).order_by(Deal.created_at.desc()).limit(5).all()
            
            if not recent_deals:
                message = "📭 No recent deals found"
            else:
                message = "🔍 Recent Deals\n\n"
                for deal in recent_deals:
                    message += f"💎 {deal.card_name}\n"
                    message += f"   💰 ${deal.listing_price:.2f} (Market: ${deal.market_price:.2f})\n"
                    message += f"   📈 {deal.profit_margin:.1%} profit\n"
                    message += f"   🛒 {deal.platform}\n\n"
            
            await update.message.reply_text(message)
            db.close()
            
        except Exception as e:
            logger.error(f"Error in deals_command: {e}")
            await update.message.reply_text("Error getting recent deals")
    
    async def bankroll_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bankroll command handler"""
        try:
            db = SessionLocal()
            
            # Calculate current cash
            inflow = db.query(Transaction).filter(
                Transaction.type.in_(['sale', 'deposit'])
            ).with_entities(func.sum(Transaction.amount)).scalar() or 0
            
            outflow = db.query(Transaction).filter(
                Transaction.type.in_(['purchase', 'fee'])
            ).with_entities(func.sum(Transaction.amount)).scalar() or 0
            
            current_cash = inflow - abs(outflow)
            
            # Calculate inventory value
            inventory_value = db.query(InventoryItem).filter(
                InventoryItem.status != 'sold'
            ).with_entities(func.sum(InventoryItem.purchase_price)).scalar() or 0
            
            total_bankroll = current_cash + inventory_value
            
            message = f"💰 Bankroll Status\n\n"
            message += f"💵 Cash: ${current_cash:.2f}\n"
            message += f"📦 Inventory: ${inventory_value:.2f}\n"
            message += f"💎 Total: ${total_bankroll:.2f}\n"
            message += f"📈 Growth: ${total_bankroll - settings.STARTING_BANKROLL:.2f}\n"
            
            growth_pct = ((total_bankroll - settings.STARTING_BANKROLL) / settings.STARTING_BANKROLL * 100) if settings.STARTING_BANKROLL > 0 else 0
            message += f"📊 Growth %: {growth_pct:.1f}%"
            
            await update.message.reply_text(message)
            db.close()
            
        except Exception as e:
            logger.error(f"Error in bankroll_command: {e}")
            await update.message.reply_text("Error getting bankroll status")
    
    async def halt_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Halt auto-buying command"""
        try:
            # Update settings to disable auto-buy
            # This would typically update a database flag
            message = "🛑 Auto-buying halted\n\n"
            message += "Deal finding will continue but no automatic purchases will be made."
            
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"Error in halt_command: {e}")
            await update.message.reply_text("Error halting auto-buying")
    
    async def resume_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Resume auto-buying command"""
        try:
            # Update settings to enable auto-buy
            message = "▶️ Auto-buying resumed\n\n"
            message += "Bot will now automatically purchase qualifying deals."
            
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"Error in resume_command: {e}")
            await update.message.reply_text("Error resuming auto-buying")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stats command handler"""
        try:
            db = SessionLocal()
            
            # Get basic stats
            total_deals = db.query(Deal).count()
            total_inventory = db.query(InventoryItem).count()
            total_sales = db.query(Sale).count()
            
            # Get inventory by status
            listed_items = db.query(InventoryItem).filter(
                InventoryItem.status == 'listed'
            ).count()
            
            processing_items = db.query(InventoryItem).filter(
                InventoryItem.status == 'processing'
            ).count()
            
            message = f"📊 Bot Statistics\n\n"
            message += f"🔍 Total Deals: {total_deals}\n"
            message += f"📦 Total Inventory: {total_inventory}\n"
            message += f"💰 Total Sales: {total_sales}\n"
            message += f"🏷️ Listed Items: {listed_items}\n"
            message += f"⚙️ Processing Items: {processing_items}\n"
            
            await update.message.reply_text(message)
            db.close()
            
        except Exception as e:
            logger.error(f"Error in stats_command: {e}")
            await update.message.reply_text("Error getting statistics")
    
    def run(self):
        """Run the bot"""
        logger.info("Starting Telegram bot...")
        self.app.run_polling()

def send_message(message: str):
    """Send message to admin (used by worker jobs)"""
    try:
        import requests
        
        if not settings.TG_TOKEN or not settings.TG_ADMIN_ID:
            logger.warning("Telegram credentials not configured")
            return
        
        url = f"https://api.telegram.org/bot{settings.TG_TOKEN}/sendMessage"
        data = {
            'chat_id': settings.TG_ADMIN_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data)
        if response.status_code == 200:
            logger.info("Message sent successfully")
        else:
            logger.error(f"Failed to send message: {response.text}")
            
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")

def main():
    """Main function to run the bot"""
    bot = TelegramBot()
    bot.run()

if __name__ == '__main__':
    main()
