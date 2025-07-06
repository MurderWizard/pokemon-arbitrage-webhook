#!/bin/bash
"""
Add Telegram credentials to .env file
Usage: ./add_telegram_to_env.sh YOUR_BOT_TOKEN YOUR_CHAT_ID
"""

if [ $# -ne 2 ]; then
    echo "Usage: $0 BOT_TOKEN CHAT_ID"
    echo "Example: $0 123456789:ABCdef... 987654321"
    exit 1
fi

BOT_TOKEN=$1
CHAT_ID=$2

echo ""
echo "🔧 Adding Telegram credentials to .env file..."

# Add to .env file
echo "" >> .env
echo "# Telegram Bot Configuration" >> .env
echo "TG_TOKEN=$BOT_TOKEN" >> .env
echo "TG_ADMIN_ID=$CHAT_ID" >> .env

echo "✅ Credentials added to .env file!"
echo ""
echo "🧪 Testing connection..."
python3 test_telegram_demo.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! Ready for background system!"
    echo "Run: python3 background_arbitrage_mvp.py"
else
    echo ""
    echo "❌ Test failed. Check your credentials."
fi
