# 🏷️ Pokemon Card Pricing System Guide

## How the Pricing System Works

The pricing system is the **brain** of your deal detection. It determines whether a listing is actually profitable by comparing the listing price to the real market value.

## 🎯 Why You Need Accurate Prices

Without accurate pricing:
- **Miss good deals** - System thinks expensive cards are cheap
- **False alerts** - Get excited about bad deals
- **Lost profits** - Buy cards thinking they're worth more than they are
- **Wasted time** - Constantly checking prices manually

## 🏗️ How Our System Works

### 1. **Multi-Source Price Database**
```
📊 Price Sources (in order of preference):
├── Manual Updates (highest confidence)
├── TCGPlayer Scraping (if available)
├── Sold Listings Analysis
├── PriceCharting API (if available)
└── Base Price Estimation (fallback)
```

### 2. **Local SQLite Database**
- Stores prices locally for fast lookups
- Tracks price history and trends
- Caches fresh data to avoid API limits
- Works offline once populated

### 3. **Smart Price Estimation**
- Analyzes card names and sets
- Uses keyword detection for valuable cards
- Applies condition and rarity modifiers
- Provides confidence scores

## 🚀 Getting Started with Pricing

### Step 1: Create Sample Data
```bash
python3 price_manager.py --sample
```
This loads ~15 popular cards with current market prices.

### Step 2: Check What's Available
```bash
python3 price_manager.py --stats
```
Shows how many prices you have and database health.

### Step 3: Search for Specific Cards
```bash
python3 price_manager.py --search "Charizard VMAX"
python3 price_manager.py --search "Pikachu V" --set "Vivid Voltage"
```

### Step 4: Add Missing Cards
```bash
python3 price_manager.py --add "Alakazam EX" "Fates Collide" 8.00 "Near Mint"
```

## 📋 Price Manager Commands

### Search Prices
```bash
# Basic search
python3 price_manager.py --search "Charizard"

# Search with specific set
python3 price_manager.py --search "Charizard VMAX" --set "Champions Path"

# Find all cards with keyword
python3 price_manager.py --find "Charizard"
```

### Add/Update Prices
```bash
# Add new price
python3 price_manager.py --add "Card Name" "Set Name" 25.50 "Near Mint"

# Examples
python3 price_manager.py --add "Rayquaza VMAX" "Evolving Skies" 70.00 "Near Mint"
python3 price_manager.py --add "Base Set Charizard" "Base Set" 450.00 "Near Mint"
```

### Import Bulk Data
```bash
# From JSON file
python3 price_manager.py --import manual_prices.json

# From CSV file (if you have one)
python3 price_manager.py --import prices.csv
```

### Export Your Data
```bash
# Export to JSON
python3 price_manager.py --export backup.json json

# Export to CSV
python3 price_manager.py --export prices.csv csv
```

### Database Management
```bash
# Show statistics
python3 price_manager.py --stats

# List recent cards
python3 price_manager.py --list 50

# Create sample data
python3 price_manager.py --sample
```

## 📊 Understanding Price Data

Each card price includes:
- **Market Price**: Current fair market value
- **Low/High Range**: Expected price variations
- **Confidence Score**: How reliable the price is
- **Last Updated**: Freshness of the data
- **Source**: Where the price came from
- **Trend**: "up", "down", or "stable"

### Confidence Scoring
- **90%+**: Recent manual update or API data
- **70-89%**: Fresh automated data
- **50-69%**: Older data or estimation
- **<50%**: Very uncertain, needs updating

## 🎯 Manual Price Updates

### When to Update Manually
- **After buying a card** - Record actual purchase/sale prices
- **Seeing market changes** - Notice prices moving up/down
- **Finding new popular cards** - Add trending cards
- **Before major purchases** - Verify prices for expensive cards

### How to Research Prices
1. **TCGPlayer**: Check current market price
2. **eBay Sold Listings**: Look at recent sales
3. **COMC**: Check their pricing
4. **PriceCharting**: Historical data
5. **Reddit/Discord**: Community insights

### Quick Research Workflow
```bash
# 1. Search current price
python3 price_manager.py --search "Umbreon VMAX"

# 2. Research on TCGPlayer/eBay
# (Check current listings and sold items)

# 3. Update with researched price
python3 price_manager.py --add "Umbreon VMAX" "Evolving Skies" 120.00 "Near Mint"
```

## 📈 Price Trends and Market Intelligence

### Tracking Trends
The system tracks whether card prices are:
- **"up"**: Recently increasing in value
- **"down"**: Recently decreasing in value  
- **"stable"**: No significant change

### Using Trends for Better Deals
- **"up" trend cards**: Buy quickly, prices rising
- **"down" trend cards**: Wait for better deals
- **"stable" cards**: Good for consistent profits

## 🔄 Automated Price Updates

### Future Enhancements
The system is designed to support:
- **API Integration**: TCGPlayer, PriceCharting APIs
- **Web Scraping**: Automated price collection
- **Sold Listing Analysis**: Real market data
- **Community Integration**: Discord price sharing

### Current Automation
- **Caching**: Stores prices locally for speed
- **Freshness Tracking**: Knows when to refresh
- **Fallback Estimation**: Always provides a price
- **Bulk Operations**: Easy import/export

## 📝 Creating Your Own Price Database

### Option 1: Start Small
```bash
# Create sample data
python3 price_manager.py --sample

# Add cards you care about
python3 price_manager.py --add "Your Favorite Card" "Set Name" 50.00 "Near Mint"
```

### Option 2: Import from Spreadsheet
1. Create CSV with columns: `card_name,set_name,market_price,condition`
2. Import: `python3 price_manager.py --import your_prices.csv`

### Option 3: Manual Research Session
Spend 30 minutes adding popular cards:
```bash
python3 price_manager.py --add "Charizard VMAX" "Champions Path" 85.00 "Near Mint"
python3 price_manager.py --add "Pikachu VMAX" "Vivid Voltage" 25.00 "Near Mint"
python3 price_manager.py --add "Rayquaza VMAX" "Evolving Skies" 70.00 "Near Mint"
# ... continue with cards you see often
```

## 🎯 Integration with Deal Finder

The real deal finder automatically:
1. **Extracts card names** from eBay listings
2. **Looks up prices** in your database
3. **Calculates profit margins** using real data
4. **Assigns confidence scores** based on price quality
5. **Only alerts good deals** with accurate pricing

### Example Flow:
```
eBay Listing: "Charizard VMAX Champions Path PSA 10" - $65
                ↓
Price Database: Charizard VMAX (Champions Path) = $85
                ↓
Calculation: $85 - $65 = $20 profit (30.8% margin)
                ↓
Alert: 🔥 HIGH MARGIN DEAL - 30.8% profit!
```

## 🔧 Maintenance Tips

### Weekly Tasks
- Check price freshness: `python3 price_manager.py --stats`
- Update any cards you bought/sold
- Research 2-3 new popular cards

### Monthly Tasks
- Export backup: `python3 price_manager.py --export backup.json json`
- Review and update trending cards
- Clean out very old price data

### Before Big Purchases
Always verify prices manually:
```bash
python3 price_manager.py --search "Expensive Card Name"
# Then research current market before buying
```

## 🚀 Next Steps

1. **Start with sample data**: `python3 price_manager.py --sample`
2. **Test the system**: `python3 price_manager.py --search "Charizard"`
3. **Add your favorite cards**: Research and add cards you see often
4. **Run real deal finder**: `python3 real_deal_finder.py`
5. **Improve over time**: Add prices as you learn the market

The pricing system gets more accurate as you use it. Start simple, then build up your database as you gain experience with the market!
