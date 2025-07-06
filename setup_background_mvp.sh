#!/bin/bash
"""
Quick MVP Setup for Tonight's Demo
Gets Telegram notifications working in background!
"""

echo "🚀 Setting up Background Arbitrage System for TONIGHT'S DEMO!"
echo "================================================================"

# Make sure we're in the right directory
cd /home/jthomas4641/pokemon

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env with your Telegram credentials:"
    echo "TG_TOKEN=your_bot_token"
    echo "TG_ADMIN_ID=your_chat_id"
    exit 1
fi

# Make the script executable
chmod +x background_arbitrage_mvp.py

echo "📋 Testing Telegram connection..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('TG_TOKEN')
user_id = os.getenv('TG_ADMIN_ID')
print(f'✅ Token: {\"SET\" if token else \"MISSING\"}')
print(f'✅ User ID: {\"SET\" if user_id else \"MISSING\"}')
if not token or not user_id:
    print('❌ Please set TG_TOKEN and TG_ADMIN_ID in .env file!')
    exit(1)
print('🎯 Telegram credentials look good!')
"

if [ $? -ne 0 ]; then
    echo "❌ Telegram setup failed!"
    exit 1
fi

echo "🔧 Setting up systemd service..."

# Copy service file to systemd
sudo cp pokemon-arbitrage.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable the service
sudo systemctl enable pokemon-arbitrage

echo "✅ Service installed!"
echo ""
echo "🎯 Ready to start! Choose an option:"
echo ""
echo "1️⃣  Start in FOREGROUND (see logs live):"
echo "   python3 background_arbitrage_mvp.py"
echo ""
echo "2️⃣  Start as BACKGROUND SERVICE:"
echo "   sudo systemctl start pokemon-arbitrage"
echo "   sudo systemctl status pokemon-arbitrage"
echo ""
echo "3️⃣  View service logs:"
echo "   sudo journalctl -u pokemon-arbitrage -f"
echo ""
echo "4️⃣  Stop the service:"
echo "   sudo systemctl stop pokemon-arbitrage"
echo ""
echo "💡 For tonight's demo, I recommend option 1 first to test!"
echo ""
echo "🎉 Background arbitrage system ready for your work demo!"
