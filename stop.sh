#!/bin/bash

# Pokemon Card Arbitrage Bot - Stop Script

echo "🎴 Stopping Pokemon Card Arbitrage Bot..."

# Stop all services
docker-compose down

echo "✅ All services stopped."
echo ""
echo "💡 To start again, run:"
echo "   ./start.sh"
