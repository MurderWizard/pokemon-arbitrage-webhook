#!/usr/bin/env python3
"""
Demo Alert System - Generate fake deals to demonstrate the alert system

This script generates realistic Pokemon card deals and sends them as Telegram alerts
to demonstrate how the system works.
"""

import asyncio
import random
import time
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DemoAlertSystem:
    def __init__(self):
        self.bot = Bot(token=os.getenv('TG_TOKEN'))
        self.chat_id = os.getenv('TG_ADMIN_ID')
        
        # Demo card data
        self.demo_cards = [
            {
                'name': 'Charizard VMAX',
                'set': 'Champion\'s Path',
                'market_price': 89.99,
                'platforms': ['eBay', 'TCGPlayer', 'COMC']
            },
            {
                'name': 'Pikachu V',
                'set': 'Vivid Voltage',
                'market_price': 45.50,
                'platforms': ['eBay', 'TCGPlayer']
            },
            {
                'name': 'Rayquaza VMAX',
                'set': 'Evolving Skies',
                'market_price': 67.75,
                'platforms': ['eBay', 'COMC']
            },
            {
                'name': 'Umbreon VMAX',
                'set': 'Evolving Skies',
                'market_price': 124.99,
                'platforms': ['eBay', 'TCGPlayer']
            },
            {
                'name': 'Lugia V',
                'set': 'Silver Tempest',
                'market_price': 78.25,
                'platforms': ['eBay', 'COMC']
            },
            {
                'name': 'Base Set Charizard',
                'set': 'Base Set',
                'market_price': 450.00,
                'platforms': ['eBay', 'COMC']
            },
            {
                'name': 'Mewtwo & Mew GX',
                'set': 'Unified Minds',
                'market_price': 35.99,
                'platforms': ['eBay', 'TCGPlayer']
            }
        ]
        
        self.demo_running = False
    
    def generate_deal(self):
        """Generate a realistic deal"""
        card = random.choice(self.demo_cards)
        platform = random.choice(card['platforms'])
        
        # Generate listing price (20-60% below market)
        discount = random.uniform(0.2, 0.6)
        listing_price = card['market_price'] * (1 - discount)
        
        # Calculate profit margin
        profit_margin = discount
        
        # Generate deal type
        deal_types = [
            'Off-Peak Auction',
            'Wide Filter Find',
            'Bulk Lot Discovery',
            'Discord Deal Feed',
            'Ending Soon'
        ]
        
        deal_type = random.choice(deal_types)
        
        # Generate confidence score
        confidence = random.uniform(0.6, 0.95)
        
        return {
            'card_name': card['name'],
            'set_name': card['set'],
            'listing_price': listing_price,
            'market_price': card['market_price'],
            'profit_margin': profit_margin,
            'platform': platform,
            'deal_type': deal_type,
            'confidence': confidence,
            'urgent': random.choice([True, False])
        }
    
    def format_deal_alert(self, deal):
        """Format deal as Telegram alert"""
        urgency = "🔥 URGENT" if deal['urgent'] else "💎 OPPORTUNITY"
        
        message = f"{urgency} - {deal['deal_type'].upper()}\n\n"
        message += f"🎴 Card: {deal['card_name']}\n"
        message += f"📦 Set: {deal['set_name']}\n"
        message += f"💰 Listing Price: ${deal['listing_price']:.2f}\n"
        message += f"📊 Market Price: ${deal['market_price']:.2f}\n"
        message += f"📈 Profit Margin: {deal['profit_margin']:.1%}\n"
        message += f"🏪 Platform: {deal['platform']}\n"
        message += f"🎯 Confidence: {deal['confidence']:.1%}\n"
        
        if deal['urgent']:
            message += f"⚡ ACTION NEEDED: Time sensitive!\n"
        
        message += f"\n🤖 Auto-Buy: {'Would purchase' if deal['confidence'] > 0.8 else 'Manual review required'}\n"
        message += f"⏰ Found at: {datetime.now().strftime('%H:%M:%S')}"
        
        return message
    
    def format_system_status(self):
        """Format system status message"""
        message = "🤖 SYSTEM STATUS UPDATE\n\n"
        message += f"✅ Deal Scanner: Active\n"
        message += f"⏰ Last Scan: {datetime.now().strftime('%H:%M:%S')}\n"
        message += f"🎯 Scanning: eBay, TCGPlayer, COMC\n"
        message += f"📊 Found Today: {random.randint(15, 45)} deals\n"
        message += f"🛒 Auto-Purchased: {random.randint(2, 8)} items\n"
        message += f"💰 Daily Spending: ${random.randint(150, 400):.2f}\n"
        message += f"🎉 Success Rate: {random.randint(85, 95)}%\n"
        
        return message
    
    async def send_alert(self, message):
        """Send alert to Telegram"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            print(f"✅ Alert sent: {message.split()[0]}")
            return True
        except TelegramError as e:
            print(f"❌ Failed to send alert: {e}")
            return False
    
    async def run_demo(self, duration_minutes=5):
        """Run the demo for specified duration"""
        print(f"🚀 Starting demo for {duration_minutes} minutes...")
        print("📱 Check your Telegram for live alerts!")
        print("👥 Perfect for showing your friend how it works!")
        print("")
        
        self.demo_running = True
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Send welcome message
        welcome_msg = "🎴 POKEMON CARD ARBITRAGE DEMO\n\n"
        welcome_msg += "🤖 System is now scanning for deals...\n"
        welcome_msg += "📊 You'll receive alerts for high-margin opportunities\n"
        welcome_msg += f"⏰ Demo running for {duration_minutes} minutes\n\n"
        welcome_msg += "This is how the real system works 24/7!"
        
        await self.send_alert(welcome_msg)
        
        alert_count = 0
        
        while self.demo_running and time.time() < end_time:
            # Generate and send deal alert
            deal = self.generate_deal()
            
            # Only send high-quality deals (like real system)
            if deal['confidence'] > 0.7:
                alert_message = self.format_deal_alert(deal)
                await self.send_alert(alert_message)
                alert_count += 1
                
                # Simulate auto-buy for very high confidence deals
                if deal['confidence'] > 0.85:
                    await asyncio.sleep(2)  # Small delay
                    auto_buy_msg = f"🤖 AUTO-BUY EXECUTED\n\n"
                    auto_buy_msg += f"✅ Purchased: {deal['card_name']}\n"
                    auto_buy_msg += f"💰 Price: ${deal['listing_price']:.2f}\n"
                    auto_buy_msg += f"📈 Expected Profit: ${deal['listing_price'] * deal['profit_margin']:.2f}\n"
                    auto_buy_msg += f"🏪 Platform: {deal['platform']}\n"
                    auto_buy_msg += f"🎯 Confidence: {deal['confidence']:.1%}"
                    
                    await self.send_alert(auto_buy_msg)
            
            # Send system status every few alerts
            if alert_count > 0 and alert_count % 3 == 0:
                await asyncio.sleep(5)
                status_msg = self.format_system_status()
                await self.send_alert(status_msg)
            
            # Wait between alerts (random interval)
            await asyncio.sleep(random.uniform(15, 45))
        
        # Send demo completion message
        completion_msg = "🎉 DEMO COMPLETED\n\n"
        completion_msg += f"📊 Total Alerts Sent: {alert_count}\n"
        completion_msg += f"⏰ Duration: {duration_minutes} minutes\n\n"
        completion_msg += "💡 This demonstrates how the real system works:\n"
        completion_msg += "• Scans 24/7 for opportunities\n"
        completion_msg += "• Only alerts high-confidence deals\n"
        completion_msg += "• Can auto-buy qualified deals\n"
        completion_msg += "• Provides detailed analysis\n\n"
        completion_msg += "Ready to set up the full system? 🚀"
        
        await self.send_alert(completion_msg)
        
        print(f"🎉 Demo completed! Sent {alert_count} alerts.")
        print("💡 Show your friend the Telegram messages!")

async def main():
    demo = DemoAlertSystem()
    
    print("🎴 Pokemon Card Alert Demo")
    print("=" * 30)
    print()
    
    # Check configuration
    if not os.getenv('TG_TOKEN') or not os.getenv('TG_ADMIN_ID'):
        print("❌ Telegram not configured!")
        print("Run: ./demo_setup.sh first")
        return
    
    print("Configuration:")
    print(f"📱 Telegram Bot: {'✅ Configured' if os.getenv('TG_TOKEN') else '❌ Missing'}")
    print(f"👤 User ID: {os.getenv('TG_ADMIN_ID')}")
    print()
    
    # Ask for demo duration
    try:
        duration = input("Demo duration in minutes (default 5): ").strip()
        duration = int(duration) if duration else 5
        duration = max(1, min(duration, 30))  # Limit to 1-30 minutes
    except ValueError:
        duration = 5
    
    print(f"⏰ Running demo for {duration} minutes...")
    print("📱 Check your Telegram now!")
    print("🛑 Press Ctrl+C to stop early")
    print()
    
    try:
        await demo.run_demo(duration)
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
        demo.demo_running = False
        
        # Send stop message
        stop_msg = "🛑 DEMO STOPPED\n\nDemo was manually stopped."
        await demo.send_alert(stop_msg)

if __name__ == "__main__":
    asyncio.run(main())
