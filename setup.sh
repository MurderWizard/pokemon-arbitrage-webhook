#!/bin/bash

# Pokemon Card Arbitrage Bot - Setup Script

echo "🎴 Setting up Pokemon Card Arbitrage Bot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create logs directory
mkdir -p logs

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your API keys and settings."
else
    echo "✅ .env file already exists."
fi

# Install Python dependencies (for development)
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🐳 Starting Docker containers..."
docker-compose up -d postgres redis

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🗄️ Running database migrations..."
# You would run alembic upgrade head here
# alembic upgrade head

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   docker-compose up -d"
echo ""
echo "📊 Access the dashboard at: http://localhost:8502"
echo "🔧 Access the API at: http://localhost:8001"
echo ""
echo "💡 Don't forget to:"
echo "   1. Configure your API keys in .env"
echo "   2. Set up your Telegram bot token"
echo "   3. Configure your COMC and eBay accounts"
echo ""
echo "📖 Check the README.md for more information."
