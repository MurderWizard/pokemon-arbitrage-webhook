#!/bin/bash

# Railway Deployment Script for Pokemon Arbitrage eBay Compliance
# This script will deploy your webhook to Railway for eBay compliance

echo "🚀 Pokemon Arbitrage - Railway Deployment Script"
echo "================================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    curl -fsSL https://railway.app/install.sh | sh
    
    # Add Railway to PATH for current session
    export PATH="$HOME/.railway/bin:$PATH"
    
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI installation failed. Please install manually:"
        echo "   curl -fsSL https://railway.app/install.sh | sh"
        exit 1
    fi
fi

echo "✅ Railway CLI found"

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway..."
    railway login
    
    if ! railway whoami &> /dev/null; then
        echo "❌ Login failed. Please try again."
        exit 1
    fi
fi

echo "✅ Logged in to Railway as: $(railway whoami)"

# Create new Railway project
echo "🏗️  Creating Railway project..."
railway init --name pokemon-arbitrage-webhook

# Set environment variables
echo "🔧 Setting environment variables..."
railway variables set TG_TOKEN="7688729602:AAEoi5jAtR-n3XOxJI7DSonbLoqJSEXaXvA"
railway variables set EBAY_VERIFICATION_TOKEN="pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123"

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

# Get the deployment URL
echo "🌐 Getting deployment URL..."
RAILWAY_URL=$(railway status --json | jq -r '.deployments[0].url' 2>/dev/null)

if [ "$RAILWAY_URL" != "null" ] && [ -n "$RAILWAY_URL" ]; then
    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo "========================="
    echo "📍 Your webhook is now live at:"
    echo "   $RAILWAY_URL"
    echo ""
    echo "🛡️  eBay Marketplace Deletion Endpoint:"
    echo "   $RAILWAY_URL/marketplace-deletion"
    echo ""
    echo "🔍 Health Check:"
    echo "   $RAILWAY_URL/health"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Test the endpoint: curl $RAILWAY_URL/health"
    echo "2. Update eBay Developer Portal with: $RAILWAY_URL/marketplace-deletion"
    echo "3. Test eBay validation in the Developer Portal"
    echo ""
else
    echo "⚠️  Deployment completed, but couldn't get URL automatically."
    echo "   Check Railway dashboard: https://railway.app/dashboard"
    echo "   Your webhook URL will be: https://[your-app].up.railway.app/marketplace-deletion"
fi

echo "✅ Railway deployment complete!"
