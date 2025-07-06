# 🎴 Pokemon Card Arbitrage Bot - Complete Setup Guide

This is your fully automated Pokemon card trading system! Here's everything you need to get started on your journey to financial freedom through card arbitrage.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- Docker & Docker Compose
- 4GB+ RAM VPS (recommended: DigitalOcean $20/month droplet)
- API accounts for:
  - eBay Developer Program
  - TCGPlayer Partner API
  - Telegram Bot API
  - COMC account
  - PriceCharting API

### 2. Installation

```bash
# Clone/download the project
cd pokemon

# Run setup script
./setup.sh

# Edit your environment variables
nano .env

# Start all services
./start.sh
```

### 3. Access Your Dashboard
- **Dashboard**: http://localhost:8502
- **API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## 📋 Required API Keys & Setup

### eBay API
1. Go to https://developer.ebay.com/
2. Create an application
3. Get your App ID, Cert ID, and User Token
4. Add to `.env` file

### TCGPlayer API
1. Apply for TCGPlayer Partner API at https://tcgplayer.com/
2. Get Client ID and Client Secret
3. Add to `.env` file

### Telegram Bot
1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Get your bot token
4. Get your user ID (message @userinfobot)
5. Add to `.env` file

### COMC Account
1. Create account at https://comc.com/
2. Set up mailbox service
3. Get your credentials
4. Add to `.env` file

### PriceCharting API
1. Sign up at https://www.pricecharting.com/
2. Subscribe to API tier ($12/month)
3. Get API key
4. Add to `.env` file

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Deal Finder   │    │   Pricing Bot   │    │  Telegram Bot   │
│   (Every 5min)  │    │   (Every hour)  │    │   (Commands)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   (Database)    │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   FastAPI       │
                    │   (REST API)    │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Streamlit     │
                    │   (Dashboard)   │
                    └─────────────────┘
```

## 🔧 Configuration

### Trading Parameters (in `.env`)
```bash
STARTING_BANKROLL=1000          # Your starting capital
MAX_POSITION_PERCENT=5          # Max 5% per card
DEAL_THRESHOLD=0.75             # Buy if price ≤ 75% of market
MIN_PROFIT_MARGIN=0.25          # Minimum 25% profit margin
ENABLE_AUTO_BUY=false           # Set to true when ready
DAILY_SPEND_LIMIT=200           # Max daily spend
```

### Risk Controls
```bash
RAW_AGING_DAYS=45               # Markdown raw cards after 45 days
SLAB_AGING_DAYS=30              # Markdown slabs after 30 days
STOP_LOSS_THRESHOLD=0.6         # Auto-auction at 60% of market
```

### Payment Setup
1. Choose your payment method (Credit Card or PayPal)
2. Add to `.env` file:

For Credit Card:
```bash
EBAY_PAYMENT_METHOD=CC
CC_LAST_4=1234  # Last 4 digits of your card
```

For PayPal:
```bash
EBAY_PAYMENT_METHOD=PP
PAYPAL_EMAIL=your@email.com
```

Important Payment Limits:
- Single card limit: $1,000
- Daily limit: $2,500
- Weekly limit: $10,000
- Minimum balance: $500

These limits help manage risk for high-value cards. You can adjust them in `payment_config.py`.

## 📱 Telegram Commands

Once your bot is running, message it:

- `/start` - Welcome message and command list
- `/pnl [days]` - Profit & Loss summary (default 30 days)
- `/aging [days]` - Show aged inventory (default 60+ days)
- `/deals` - Recent deals found
- `/bankroll` - Current bankroll status
- `/stats` - Performance statistics  
- `/halt` - Halt auto-buying (safety)
- `/resume` - Resume auto-buying

## 🎯 How It Works

### 1. Deal Discovery
- Scans eBay every 5 minutes for undervalued Pokemon cards
- Compares prices against TCGPlayer market data
- Alerts you via Telegram for high-margin deals (50%+)
- Automatically purchases deals if auto-buy is enabled

### 2. Inventory Routing
- **Raw Cards** → COMC Mailbox for processing and listing
- **Graded Cards** → PSA Vault for secure storage and fulfillment
- **High-Value Raw** → PSA for grading consideration

### 3. Pricing Strategy
```python
# Raw cards: 2% below market, 5% markdown after 45 days
if card_type == "raw":
    target_price = market_price * 0.98
    if days_in_stock > 45:
        target_price *= 0.95

# Graded cards: 5% above recent sales, 3% markdown after 30 days  
elif card_type == "psa10":
    target_price = avg_7d_sold * 1.05
    if days_in_stock > 30:
        target_price *= 0.97
```

### 4. Risk Management
- Maximum 5% of bankroll per single card
- Stop-loss at 60% of market price after 90 days
- Daily spend limits to prevent runaway buying
- Manual halt command for emergency stops

## 📊 Expected Performance

### Target Metrics
- **Raw Singles**: ≥20% net profit in 30-60 days
- **Graded Slabs**: ≥10% net profit in 30-60 days
- **Turnover**: 60% of inventory sells within 30 days
- **Monthly Overhead**: ~$23 fixed costs

### Scale-Up Roadmap
- **Months 0-2**: Stabilize $1k bankroll, $200+ net/month
- **Month 3**: Reach 1,500 SKUs, qualify for TCGPlayer Direct
- **Months 4-6**: Grow to $3-4k bankroll
- **Month 7+**: Form LLC, get distributor accounts, $10k+ monthly turnover

## 🛠️ Management Commands

### Database Management
```bash
# Create database tables
python scripts/db_manage.py create

# Reset database (careful!)
python scripts/db_manage.py reset

# Seed with sample data
python scripts/db_manage.py seed

# Show statistics
python scripts/db_manage.py stats
```

### Service Management
```bash
# Start all services
./start.sh

# Stop all services  
./stop.sh

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart api
```

## 🔍 Monitoring & Alerts

### Daily Telegram Summary (11 PM)
- Revenue and profit for the day
- Number of deals found
- Sales completed
- Aged inventory count

### Real-time Alerts
- High-margin deals (50%+ profit)
- Stop-loss triggers
- Cash balance warnings
- System errors

## 💰 Profit Tracking

### Dashboard Metrics
- **P&L Summary**: Revenue, costs, net profit, margins
- **Inventory Aging**: Items by days in stock
- **Performance**: Turnover rates, ROI, growth
- **Top Performers**: Best cards by profit

### Tax Compliance
- All transactions logged with timestamps
- COGS tracking for Schedule C
- 1099-K handling for each platform
- Sales tax collection for in-state shipments

## 🚨 Safety Features

### Auto-Halt Triggers
- Cash balance below 10% of bankroll
- Daily spend limit exceeded
- Consecutive failed API calls
- Manual halt command

### Position Limits
- Maximum 5% of bankroll per card
- Blacklist for reprinted sets
- Minimum profit margin enforcement
- Stop-loss thresholds

## 🔧 Troubleshooting

### Common Issues

**Services won't start**
```bash
# Check logs
docker-compose logs

# Restart services
./stop.sh && ./start.sh
```

**Database connection issues**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Reset database
python scripts/db_manage.py reset
```

**API rate limits**
- TCGPlayer: 300 requests per 5 minutes
- eBay: Varies by tier
- Telegram: 30 messages per second

### Performance Optimization
- Use SSD storage for database
- At least 4GB RAM for smooth operation
- Monitor API call budgets
- Regular database maintenance

## 📈 Success Metrics

### Weekly KPIs
- Deal finding rate: 20+ deals/week
- Purchase rate: 5-10 cards/week  
- Sale rate: 3-7 cards/week
- Profit margin: 20%+ average

### Monthly Goals
- Revenue: $500-1000
- Net profit: $200-500
- Inventory turnover: 1-2x
- ROI: 20-40%

## 🎯 Next Steps

1. **Configure all API keys** in `.env`
2. **Test with small amounts** first
3. **Monitor for 1-2 weeks** before enabling auto-buy
4. **Scale up gradually** as you gain confidence
5. **Track performance** and adjust parameters

## 🆘 Support

### Documentation
- Check `docs/` folder for detailed API docs
- Review `app/` code for implementation details
- Monitor logs in `logs/` directory

### Community
- Join Pokemon card trading communities
- Follow market trends and news
- Network with other traders

## ⚠️ Disclaimers

- **This is not financial advice**
- **Start small and test thoroughly**
- **Card markets are volatile**
- **Regulations vary by location**
- **Past performance doesn't guarantee future results**

---

**Remember**: The goal is financial freedom through automation. Start conservative, monitor closely, and scale up as you gain experience. The bot handles the tedious work so you can focus on strategy and growth.

Good luck on your journey to escaping the 9-to-5! 🚀
