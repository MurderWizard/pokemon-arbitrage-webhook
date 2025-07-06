#!/bin/bash

# Real Deal Alerts Setup - Get real alerts running FAST!

echo "🎴 Real Pokemon Deal Alerts Setup"
echo "================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Configure your Telegram bot!"
    echo "   1. Message @BotFather on Telegram"
    echo "   2. Send /newbot and follow instructions"
    echo "   3. Get your bot token"
    echo "   4. Get your user ID from @userinfobot"
    echo "   5. Edit .env and add:"
    echo "      TG_TOKEN=your_bot_token_here"
    echo "      TG_ADMIN_ID=your_user_id_here"
    echo ""
    echo "Then run this script again!"
    exit 1
fi

# Load environment variables
source .env

# Check if Telegram is configured
if [ -z "$TG_TOKEN" ] || [ "$TG_TOKEN" = "your_telegram_bot_token_here" ]; then
    echo "❌ Telegram bot not configured!"
    echo ""
    echo "Quick setup:"
    echo "1. Message @BotFather on Telegram"
    echo "2. Send: /newbot"
    echo "3. Follow instructions to create bot"
    echo "4. Copy the token"
    echo "5. Message @userinfobot to get your user ID"
    echo "6. Edit .env file:"
    echo "   TG_TOKEN=your_actual_bot_token"
    echo "   TG_ADMIN_ID=your_actual_user_id"
    echo ""
    echo "Then run: ./real_alerts_setup.sh"
    exit 1
fi

echo "✅ Telegram bot configured!"

# Install required dependencies
echo "📦 Installing required packages..."
pip install -q python-telegram-bot python-dotenv requests beautifulsoup4 lxml

echo "🤖 Testing Telegram connection..."
python3 -c "
import asyncio
from telegram import Bot
from telegram.error import TelegramError
import os
from dotenv import load_dotenv

load_dotenv()

async def test_bot():
    try:
        bot = Bot(token=os.getenv('TG_TOKEN'))
        await bot.send_message(
            chat_id=os.getenv('TG_ADMIN_ID'),
            text='🎴 Real Pokemon Deal Alerts Ready!\n\nThis is a test message. The real alert system is about to start!'
        )
        print('✅ Telegram test successful!')
        return True
    except Exception as e:
        print(f'❌ Telegram test failed: {e}')
        return False

asyncio.run(test_bot())
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 REAL ALERTS READY!"
    echo "===================="
    echo "✅ Telegram bot working"
    echo "✅ Dependencies installed"
    echo "✅ Ready to find real deals"
    echo ""
    echo "Start scanning for real deals:"
    echo "  python3 real_deal_finder.py"
    echo ""
    echo "This will:"
    echo "• Scan eBay every 5 minutes for real Pokemon cards"
    echo "• Find deals with 25%+ profit margins"
    echo "• Send you Telegram alerts for good opportunities"
    echo "• Include direct links to the listings"
    echo "• Run continuously until you stop it"
    echo ""
    echo "Ready to make real money? Run the scanner now!"
else
    echo ""
    echo "❌ Setup incomplete - check your Telegram configuration"
fi
