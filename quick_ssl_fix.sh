#!/bin/bash
# Quick Let's Encrypt setup for eBay compliance
# Run this script to get a trusted SSL certificate

echo "🚀 Quick Let's Encrypt Setup for eBay Compliance"
echo "================================================"

# Stop the webhook server first
echo "🛑 Stopping webhook server..."
sudo pkill -f "python.*direct_webhook.py" || true
sleep 3

# Install certbot if not already installed
echo "📦 Installing certbot..."
sudo apt update
sudo apt install -y certbot

# Get certificate using standalone mode
echo "🔒 Getting Let's Encrypt certificate..."
sudo certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email admin@pokemon-arbitrage.duckdns.org \
    --domains pokemon-arbitrage.duckdns.org

if [ $? -eq 0 ]; then
    echo "✅ Certificate obtained successfully!"
    
    # Copy certificates to webhook directory
    echo "📋 Copying certificates..."
    sudo mkdir -p /home/jthomas4641/pokemon/ssl
    sudo cp /etc/letsencrypt/live/pokemon-arbitrage.duckdns.org/fullchain.pem /home/jthomas4641/pokemon/ssl/telegram_webhook.crt
    sudo cp /etc/letsencrypt/live/pokemon-arbitrage.duckdns.org/privkey.pem /home/jthomas4641/pokemon/ssl/telegram_webhook.key
    sudo chown $(whoami):$(whoami) /home/jthomas4641/pokemon/ssl/*
    sudo chmod 600 /home/jthomas4641/pokemon/ssl/telegram_webhook.key
    sudo chmod 644 /home/jthomas4641/pokemon/ssl/telegram_webhook.crt
    
    echo "✅ Certificates copied and permissions set!"
    
    # Restart webhook
    echo "🔄 Restarting webhook server..."
    cd /home/jthomas4641/pokemon
    sudo python3 direct_webhook.py &
    
    echo "🎉 Setup complete!"
    echo "Your webhook now has a trusted SSL certificate!"
    echo "Test it: curl https://pokemon-arbitrage.duckdns.org/health"
    
else
    echo "❌ Certificate generation failed!"
    echo "💡 Try the Railway deployment option instead"
fi
