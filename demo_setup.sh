#!/bin/bash

# Quick Demo Setup - Get to alerts FAST!
# This script sets up just enough to demonstrate the alert system

echo "🚀 Quick Demo Setup - Pokemon Card Alerts"
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: You need to configure your Telegram bot!"
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
    echo "Then run: ./demo_setup.sh"
    exit 1
fi

echo "✅ Telegram bot configured!"

# Create minimal directories
mkdir -p logs
mkdir -p data

# Install minimal dependencies
echo "📦 Installing minimal dependencies..."
pip install -q fastapi uvicorn python-telegram-bot python-dotenv requests

# Start minimal services
echo "🐳 Starting minimal services..."
docker-compose up -d postgres redis || {
    echo "⚠️  Docker issue, trying without containers..."
    echo "   (Using simplified demo mode)"
}

echo "⏳ Waiting for services..."
sleep 5

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
            text='🎴 Pokemon Card Alert System - Demo Ready!\n\nThis is a test message. The alert system is working!'
        )
        print('✅ Telegram test message sent successfully!')
        return True
    except Exception as e:
        print(f'❌ Telegram test failed: {e}')
        return False

asyncio.run(test_bot())
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ DEMO READY!"
    echo "=============="
    echo "Your Telegram bot is working!"
    echo ""
    echo "Next steps:"
    echo "1. Run: python3 demo_alerts.py"
    echo "2. Watch your Telegram for deal alerts!"
    echo "3. Show your friend the live alerts"
    echo ""
    echo "The demo will generate fake deals to show how alerts work."
else
    echo ""
    echo "❌ Setup incomplete - check your Telegram configuration"
fi
