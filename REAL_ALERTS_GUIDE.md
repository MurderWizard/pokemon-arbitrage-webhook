# 🎴 Real Deal Alerts - Quick Start

## Get real Pokemon card deal alerts in 3 minutes!

### Step 1: Create Telegram Bot (2 minutes)

1. **Open Telegram** and message **@BotFather**
2. **Send**: `/newbot`
3. **Name your bot**: "Pokemon Deal Bot" (or whatever you want)
4. **Choose username**: something like "your_pokemon_deals_bot"
5. **Copy the token** (looks like: `1234567890:ABCdefGHI...`)
6. **Message @userinfobot** to get your user ID
7. **Copy your user ID** (looks like: `123456789`)

### Step 2: Configure & Start (1 minute)

```bash
# Run setup script
./real_alerts_setup.sh
```

When prompted, edit `.env` with your bot details:
```bash
TG_TOKEN=your_actual_bot_token_here
TG_ADMIN_ID=your_actual_user_id_here
```

### Step 3: Start Finding Real Deals!

```bash
# Start the real deal scanner
python3 real_deal_finder.py
```

**That's it!** You'll start getting real deal alerts in Telegram.

## 📱 What You'll Get

### Real Deal Alerts:
```
🔥 HIGH MARGIN - REAL DEAL FOUND

🎴 Card: Charizard VMAX Champion's Path #74
💰 Price: $45.99
📊 Est. Market: $75.00
📈 Profit: 63.1%
🏪 Platform: eBay
📋 Type: AUCTION
🎯 Confidence: 82.3%
🔍 Condition: Near Mint
⏰ Found: 14:23:45
🔗 Link: https://ebay.com/itm/...
```

### Status Updates:
```
📊 SCAN UPDATE #5

🔍 Scanner is active and working
⏰ Last scan: 14:25:30
🎯 Looking for 25%+ profit deals
📈 Next scan in 5 minutes...
```

## 🎯 How It Works

- **Scans eBay every 5 minutes** for real Pokemon cards
- **Finds auctions ending soon** (less competition)
- **Identifies Buy It Now deals** under market value
- **Calculates profit margins** using keyword analysis
- **Only alerts deals with 25%+ profit** potential
- **Provides direct links** to the listings
- **Runs continuously** until you stop it

## 🛡️ What It Searches For

**High-Value Cards:**
- Charizard variants (VMAX, GX, EX)
- Popular Pokemon (Pikachu, Rayquaza, Lugia)
- Vintage cards (Base Set, First Edition)
- Graded cards (PSA, BGS, CGC)

**Deal Types:**
- Ending auctions with low bids
- Buy It Now listings under market
- Mis-titled listings
- Bulk lots with valuable singles

## 🚀 Getting Better Results

### After 1 Week:
- Watch which alerts turn into profitable purchases
- Note which keywords find the best deals
- Learn to quickly evaluate opportunities

### Scaling Up:
- Add more search terms to `real_deal_finder.py`
- Run multiple instances for different categories
- Set up automatic purchasing (advanced)
- Integrate with COMC for fulfillment

## 🆘 Troubleshooting

**No alerts coming?**
- Check your Telegram bot token and user ID
- Make sure you messaged your bot first
- Verify the scanner is running (should show scan updates)

**Getting too many alerts?**
- Edit `real_deal_finder.py` and increase minimum profit margin
- Adjust confidence threshold higher
- Focus on specific card types

**Want to stop?**
- Press `Ctrl+C` in the terminal
- The bot will send a shutdown message

## ⚠️ Important Notes

- **This finds REAL deals** on real marketplaces
- **Act quickly** - good deals disappear fast
- **Verify listings** before buying (condition, authenticity)
- **Start small** - learn the market before big purchases
- **Check seller feedback** and return policies

## 🎉 Ready to Start?

1. **Set up Telegram bot** (2 minutes)
2. **Run setup script**: `./real_alerts_setup.sh`
3. **Start scanning**: `python3 real_deal_finder.py`
4. **Watch your Telegram** for real money-making opportunities!

The scanner will find real undervalued Pokemon cards and send you direct links to buy them. Perfect for starting your arbitrage business with actual deals!
