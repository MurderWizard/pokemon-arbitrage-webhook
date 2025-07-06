#!/bin/bash

# Hands-Off Automation Startup Script
# This script starts the complete hands-off automation system

set -e

echo "🤖 Starting Hands-Off Pokemon Card Arbitrage System"
echo "=================================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure."
    exit 1
fi

# Load environment variables
source .env

# Check critical environment variables
if [ -z "$TG_TOKEN" ]; then
    echo "⚠️  Warning: Telegram bot token not configured. Notifications will be disabled."
fi

if [ "$AUTO_BUY_ENABLED" = "true" ]; then
    echo "🛒 Auto-buy is ENABLED - System will make automatic purchases"
    echo "   Daily limit: $DAILY_AUTO_BUY_LIMIT"
    echo "   Max per item: $MAX_AUTO_BUY_AMOUNT"
else
    echo "👀 Auto-buy is DISABLED - System will only find deals and send alerts"
fi

# Start infrastructure services
echo "🚀 Starting infrastructure services..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Install/update Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Start the main application
echo "🌟 Starting main application..."
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &
APP_PID=$!

# Start the worker
echo "👷 Starting background workers..."
python -m app.workers.main &
WORKER_PID=$!

# Start the scheduler
echo "⏰ Starting automation scheduler..."
python -m app.services.automation_scheduler &
SCHEDULER_PID=$!

# Start the dashboard
echo "📊 Starting dashboard..."
streamlit run app/dashboard/main.py --server.port 8502 --server.address 0.0.0.0 &
DASHBOARD_PID=$!

# Start the Telegram bot
echo "🤖 Starting Telegram bot..."
python -m app.telegram.bot &
BOT_PID=$!

# Save PIDs for cleanup
echo "$APP_PID" > .app.pid
echo "$WORKER_PID" > .worker.pid
echo "$SCHEDULER_PID" > .scheduler.pid
echo "$DASHBOARD_PID" > .dashboard.pid
echo "$BOT_PID" > .bot.pid

echo ""
echo "✅ Hands-Off Automation System Started Successfully!"
echo "=================================================="
echo "🌐 API Server: http://localhost:8001"
echo "📊 Dashboard: http://localhost:8502"
echo "🤖 Telegram Bot: @YourBotName"
echo "⚙️  Worker Status: Background"
echo "⏰ Scheduler Status: Running"
echo ""
echo "The system is now running in hands-off mode!"
echo "You will receive Telegram notifications for:"
echo "  • High-margin deal discoveries"
echo "  • Automatic purchases (if enabled)"
echo "  • Price updates and repricing"
echo "  • System alerts and errors"
echo ""
echo "To stop the system, run: ./stop_automation.sh"
echo "To view logs, run: ./view_logs.sh"
echo ""

# Keep the script running to handle signals
trap 'echo "🛑 Stopping system..."; ./stop_automation.sh; exit 0' SIGINT SIGTERM

# Wait for any of the background processes to exit
wait
