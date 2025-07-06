# 📈 Pokemon Card Price Update Strategy

## 🎯 How Often to Update Prices

### **Daily Updates** (Most Important)
**Cards to update DAILY**:
- Cards you currently own (for accurate P&L)
- Cards you're actively watching/bidding on
- Recent deal alerts (verify prices after purchases)

### **Weekly Updates** (High-Value Cards)
**Update WEEKLY** (Sundays work well):
- **Modern Chase Cards**: Charizard VMAX, Alt Arts, Secret Rares
- **Cards $50+**: High-value cards fluctuate more
- **Trending Cards**: Cards getting social media buzz
- **New Set Releases**: Prices are volatile first few weeks

### **Monthly Updates** (Stable Cards)
**Update MONTHLY** (1st of month):
- **Base Set Classics**: Charizard, Blastoise, Venusaur
- **Established Cards $10-50**: More stable pricing
- **Older Sets**: Ex, GX, older VMAX cards

### **Quarterly Updates** (Low-Value Cards)
**Update QUARTERLY** (every 3 months):
- **Commons/Uncommons**: Very stable pricing
- **Cards under $5**: Low impact on profit calculations
- **Bulk lot pricing**: Average per-card estimates

## ⚡ Smart Update Priorities

### **Priority 1: Cards You Own**
```bash
# Update cards in your inventory daily
python3 price_manager.py --search "Charizard VMAX" --set "Champions Path"
# Research current market, then update:
python3 price_manager.py --add "Charizard VMAX" "Champions Path" 85.00 "Near Mint"
```

### **Priority 2: Alert Verification**
When you get deal alerts, verify the price:
```bash
# System says: "Charizard VMAX for $65, market price $85"
# Double-check on TCGPlayer/eBay sold listings
# Update if needed
```

### **Priority 3: Market Movers**
Cards that are trending up/down rapidly.

## 📊 Update Frequency by Card Type

| Card Type | Value Range | Update Frequency | Why |
|-----------|-------------|------------------|-----|
| **Chase Cards** | $100+ | Daily | High volatility, big profit impact |
| **Modern Staples** | $20-100 | Weekly | Regular market movement |
| **Classic Cards** | $50+ | Monthly | Stable but valuable |
| **Mid-Range** | $5-20 | Monthly | Moderate impact |
| **Low-Value** | Under $5 | Quarterly | Low impact on profits |

## 🔄 Automated Update Workflow

### **Sunday Evening Routine** (30 minutes)
```bash
# 1. Check stats
python3 price_manager.py --stats

# 2. Update top 10 most valuable cards
python3 price_manager.py --search "Charizard"
# Research → Update

# 3. Add any new trending cards
python3 price_manager.py --add "New Hot Card" "Latest Set" 120.00 "Near Mint"

# 4. Export backup
python3 price_manager.py --export backup_$(date +%Y%m%d).json json
```

### **Daily Quick Check** (5 minutes)
```bash
# Check cards you own
python3 price_manager.py --search "cards_i_own"

# Verify any deal alerts you got
python3 price_manager.py --search "recent_alerts"
```

## 📈 Price Research Sources (In Order)

### **1. TCGPlayer Market Price** (Most Reliable)
- Go to tcgplayer.com
- Search exact card name + set
- Use "Market Price" (not lowest listing)
- Check recent sales data

### **2. eBay Sold Listings** (Real Market Data)
- Search: Card name + "sold"
- Filter: Last 30 days, same condition
- Average the recent sales
- Ignore outliers (damaged, international)

### **3. COMC/Other Platforms**
- COMC.com current listings
- Mercari recent sales
- Facebook group sales

### **4. PriceCharting** (Good for Trends)
- Shows price history graphs
- Good for vintage cards
- Less reliable for modern cards

## 🎯 Strategic Update Schedule

### **Week 1: High-Value Focus**
- Update all cards $100+
- Research trending cards
- Verify recent purchases

### **Week 2: Modern Staples**
- Update current standard cards
- Check new set prices
- Popular VMAX/V cards

### **Week 3: Classic Cards**
- Base Set, Jungle, Fossil
- Popular vintage cards
- Established graded cards

### **Week 4: Cleanup & Analysis**
- Update remaining cards
- Remove outdated entries
- Analyze price trends

## 🔍 Quality Control

### **Red Flags to Watch**
- Price changes >50% (double-check)
- Cards selling much faster/slower
- New reprints or announcements
- Social media trends affecting prices

### **Verification Checklist**
```bash
# Before updating a card price:
1. Check at least 2 sources
2. Verify set name is correct
3. Confirm condition (NM vs LP vs HP)
4. Check for recent reprints
5. Consider market timing (weekend vs weekday)
```

## 📱 Mobile-Friendly Updates

### **Quick Research on Phone**
1. **TCGPlayer App**: Best for quick price checks
2. **eBay App**: Easy to check sold listings
3. **Discord/Reddit**: Community price discussions
4. **Notes App**: Keep list of cards to update later

### **Batch Updates**
```bash
# Research 5-10 cards on phone, then batch update:
python3 price_manager.py --add "Card 1" "Set 1" 25.00 "Near Mint"
python3 price_manager.py --add "Card 2" "Set 2" 45.00 "Near Mint"
python3 price_manager.py --add "Card 3" "Set 3" 15.00 "Near Mint"
```

## 🎲 Example Update Session

### **Sunday Price Update (30 min)**
```bash
# 1. Check what needs updating (5 min)
python3 price_manager.py --stats

# 2. Research top 5 cards (15 min)
# - Open TCGPlayer
# - Check each card's current market price
# - Note any big changes

# 3. Update prices (5 min)
python3 price_manager.py --add "Charizard VMAX" "Champions Path" 88.00 "Near Mint"
python3 price_manager.py --add "Umbreon VMAX" "Evolving Skies" 115.00 "Near Mint"
# ... etc

# 4. Add new trending cards (5 min)
python3 price_manager.py --add "New Hot Card" "Latest Set" 75.00 "Near Mint"

# 5. Backup (1 min)
python3 price_manager.py --export backup.json json
```

## 🚀 Pro Tips

### **Efficiency Hacks**
- **Bookmark**: TCGPlayer advanced search
- **Spreadsheet**: Track cards to research
- **Calendar**: Set weekly update reminders
- **Discord**: Join price discussion channels

### **Market Timing**
- **Best Research Time**: Sunday evenings
- **Avoid**: During big tournaments (prices spike)
- **Watch**: New set release schedules
- **Monitor**: Reprint announcements

### **Accuracy Improvements**
- Always use exact set names
- Specify condition clearly
- Check for alternate arts/variants
- Verify card numbers if needed

## 🎯 Bottom Line

**Start Simple**: Update daily any cards you care about
**Build Gradually**: Add more cards as you learn the market
**Stay Current**: Weekly updates for cards $20+
**Automate**: Use the price manager for easy updates

The more accurate your prices, the better your deal detection will be!
