# 🚀 Quick Demo Guide - Pokemon Card Alerts

## Get alerts working in 5 minutes to show your friend!

### Step 1: Create a Telegram Bot (2 minutes)

1. **Open Telegram** and message **@BotFather**
2. **Send**: `/newbot`
3. **Follow instructions** to create your bot
4. **Copy the token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. **Message @userinfobot** to get your user ID
6. **Copy your user ID** (looks like: `123456789`)

### Step 2: Configure the System (1 minute)

```bash
# Run the demo setup
./demo_setup.sh
```

When prompted, edit the `.env` file with your bot details:
```bash
TG_TOKEN=your_actual_bot_token_here
TG_ADMIN_ID=your_actual_user_id_here
```

### Step 3: Start the Demo (30 seconds)

```bash
# Run the alert demo
python3 demo_alerts.py
```

Choose how long to run the demo (default 5 minutes).

### Step 4: Watch the Magic! ✨

- **Check your Telegram** - you'll start getting deal alerts!
- **Show your friend** the live alerts as they come in
- **See auto-buy decisions** in real-time
- **System status updates** every few deals

## 📱 What You'll See

### Deal Alerts Look Like:
```
🔥 URGENT - OFF-PEAK AUCTION

🎴 Card: Charizard VMAX
📦 Set: Champion's Path
💰 Listing Price: $54.99
📊 Market Price: $89.99
📈 Profit Margin: 38.9%
🏪 Platform: eBay
🎯 Confidence: 87.3%
⚡ ACTION NEEDED: Time sensitive!

🤖 Auto-Buy: Would purchase
⏰ Found at: 14:32:15
```

### Auto-Buy Notifications:
```
🤖 AUTO-BUY EXECUTED

✅ Purchased: Charizard VMAX
💰 Price: $54.99
📈 Expected Profit: $21.38
🏪 Platform: eBay
🎯 Confidence: 87.3%
```

### System Status Updates:
```
🤖 SYSTEM STATUS UPDATE

✅ Deal Scanner: Active
⏰ Last Scan: 14:35:42
🎯 Scanning: eBay, TCGPlayer, COMC
📊 Found Today: 28 deals
🛒 Auto-Purchased: 5 items
💰 Daily Spending: $287.50
🎉 Success Rate: 89%
```

## 🎯 Perfect for Showing Friends

This demo shows exactly how the real system works:

- **24/7 Scanning**: Continuously finds undervalued cards
- **Smart Filtering**: Only alerts high-confidence deals
- **Auto-Buy Logic**: Shows what the system would purchase
- **Real-Time Updates**: Live system status and metrics
- **Professional Alerts**: Detailed analysis and reasoning

## 🚀 After the Demo

Once your friend sees how it works, you can:

1. **Set up the full system** with real API keys
2. **Start with notifications only** to build confidence
3. **Gradually enable auto-buy** as you get comfortable
4. **Scale up** to serious arbitrage operation

## 🆘 Troubleshooting

**No alerts coming?**
- Check your Telegram bot token and user ID
- Make sure you messaged your bot first
- Restart the demo script

**Demo not starting?**
- Run `./demo_setup.sh` first
- Check that Python and pip are installed
- Verify your .env file has the right values

**Want to customize?**
- Edit `demo_alerts.py` to change card types
- Adjust timing between alerts
- Modify profit margins shown

---

**This demo generates fake deals to show how the system works. The real system scans actual marketplaces for genuine opportunities!**
