#!/bin/bash

# Pokemon Card Arbitrage Bot - Start Script

echo "🎴 Starting Pokemon Card Arbitrage Bot..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run ./setup.sh first."
    exit 1
fi

# Start all services
echo "🐳 Starting all services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "🔗 Access URLs:"
    echo "   📊 Dashboard: http://localhost:8502"
    echo "   🔧 API: http://localhost:8001"
    echo "   📖 API Docs: http://localhost:8001/docs"
    echo ""
    echo "📱 Don't forget to start your Telegram bot by sending /start"
    echo ""
    echo "📋 To view logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 To stop all services:"
    echo "   docker-compose down"
else
    echo "❌ Some services failed to start. Check logs with:"
    echo "   docker-compose logs"
fi
