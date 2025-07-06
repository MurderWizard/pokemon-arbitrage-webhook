# 🎴 Pokémon Card Arbitrage Bot

**Automated trading system for achieving financial freedom through Pokémon card arbitrage**

> *"Your automated path to escaping the 9-to-5 grind through smart card trading"*

## 🚀 What This Does

This system completely automates the process of:
- 🔍 **Finding undervalued Pokémon cards** across multiple platforms 24/7
- 🤖 **Auto-buying profitable deals** using advanced community strategies
- 📦 **Routing inventory** to COMC/PSA Vault for hands-off processing
- 💲 **Dynamic repricing** based on market conditions and inventory age
- 📊 **Performance optimization** with machine learning insights
- 💬 **Smart notifications** via Telegram for high-priority items only
- 🎮 **Discord integration** for real-time community deal feeds

## 🎯 Target Returns

- **Raw singles**: ≥20% net profit in 30-60 days
- **Graded slabs**: ≥10% net profit in 30-60 days
- **Monthly overhead**: ~$23 fixed costs
- **Starting bankroll**: $1,000 (scales up to $10k+)

## ⚡ Quick Start

```bash
# 1. Setup the system
./setup.sh

# 2. Configure your API keys and automation settings
nano .env

# 3. Start the hands-off automation system
./start_automation.sh

# 4. Access your dashboard
open http://localhost:8502
```

## 🏗️ System Architecture

```
📱 Telegram Bot ←→ 🤖 Deal Finder ←→ 💰 Pricing Bot
       ↓                 ↓                ↓
📊 Dashboard ←→ 🗄️ PostgreSQL ←→ 🔧 FastAPI
```

## 🔑 Key Features

- **🔍 Enhanced Deal Discovery**: Multi-platform scanning with community insights
- **🤖 Intelligent Auto-Buy**: ML-powered purchase decisions with risk controls
- **📈 Dynamic Pricing**: Market-aware repricing with aging adjustments
- **🎮 Discord Integration**: Real-time community deal feeds
- **🌙 Off-Peak Advantage**: Automated scanning during low-competition hours
- **📦 Bulk Lot Analysis**: Automated evaluation of collections and lots
- **🛡️ Risk Controls**: Position limits, daily caps, emergency stops
- **📱 Smart Notifications**: Priority-based Telegram alerts
- **📊 Performance Analytics**: ML-driven optimization and insights
- **🎯 Compliance Ready**: Tax reporting and automated record keeping

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose
- 4GB+ RAM VPS (DigitalOcean recommended)
- API accounts: eBay, TCGPlayer, Telegram, COMC, PriceCharting

## 📚 Documentation

- **[🚀 Complete Setup Guide](SETUP_GUIDE.md)** - Everything you need to get started
- **[🤖 Hands-Off Automation Guide](AUTOMATION_GUIDE.md)** - Complete automation setup
- **[⚙️ API Configuration](docs/api.md)** - API keys and endpoints
- **[🗄️ Database Schema](docs/schema.md)** - Data structure
- **[🤖 Worker Jobs](docs/workers.md)** - Background automation tasks
- **[📊 Dashboard Guide](docs/dashboard.md)** - Using the interface
- **[💰 Profit Optimization](docs/strategy.md)** - Maximizing returns with automation

## 🎮 Telegram Commands

Control your hands-off system via Telegram:
- `/status` - System status and key metrics
- `/pause` - Pause auto-buy temporarily
- `/resume` - Resume auto-buy operations
- `/limits` - View current spending limits
- `/deals` - Recent high-quality deals found
- `/inventory` - Current inventory summary
- `/emergency` - Emergency stop all automation
- `/pnl` - Profit & Loss summary
- `/aging` - Aged inventory report

## 🌟 Success Roadmap

### Phase 1: Foundation (Months 0-2)
- Stabilize $1k bankroll
- Target $200+ net profit/month
- Learn system operations

### Phase 2: Growth (Months 3-6)
- Scale to $3-4k bankroll
- 1,500+ SKUs on COMC
- Qualify for TCGPlayer Direct

### Phase 3: Business (Months 7+)
- Form LLC with EIN
- Distributor accounts
- $10k+ monthly turnover

## ⚠️ Important Notes

- **Start Conservative** - Begin with notifications only, enable auto-buy after testing
- **Review the [Automation Guide](AUTOMATION_GUIDE.md)** - Essential for hands-off operation
- **Monitor Closely Initially** - Watch system decisions for first few weeks
- **Not Financial Advice** - Do your own research and understand the risks
- **Markets Are Volatile** - Cards can lose value quickly, use risk controls
- **Test Mode First** - Use sandbox/test modes before live operation
- **Compliance Matters** - System handles tax tracking, but verify with professionals

## 🆘 Support

- Check logs: `docker-compose logs -f`
- Database tools: `python scripts/db_manage.py stats`
- Reset system: `./stop.sh && ./start.sh`

**Note**: This system uses ports 8001 (API), 8502 (Dashboard), 5433 (PostgreSQL), and 6380 (Redis) to avoid conflicts with other services.

---

**Ready to start your hands-off journey to financial freedom? Follow the [Complete Setup Guide](SETUP_GUIDE.md) and [Automation Guide](AUTOMATION_GUIDE.md) to get started!**
