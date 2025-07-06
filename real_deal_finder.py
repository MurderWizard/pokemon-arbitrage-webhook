#!/usr/bin/env python3
"""
Real Deal Finder - Basic Implementation

This finds real Pokemon card deals using web scraping and free APIs.
Perfect for getting started with real alerts before setting up paid APIs.
"""

import asyncio
import requests
import re
import logging
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import TelegramError
import os
from dotenv import load_dotenv
import json
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealDealFinder:
    """Real deal finder using web scraping and free APIs"""
    
    def __init__(self):
        self.bot = Bot(token=os.getenv('TG_TOKEN'))
        self.chat_id = os.getenv('TG_ADMIN_ID')
        
        # Free pricing sources
        self.price_sources = {
            'tcgplayer': 'https://www.tcgplayer.com/search/pokemon/',
            'pricecharting': 'https://www.pricecharting.com/search-products'
        }
        
        # Popular Pokemon cards to search for
        self.search_terms = [
            'charizard vmax',
            'pikachu v',
            'rayquaza vmax',
            'umbreon vmax',
            'lugia v',
            'mewtwo gx',
            'alakazam ex',
            'gengar ex',
            'dragonite v',
            'gyarados gx',
            'base set charizard',
            'first edition',
            'shadowless',
            'psa 10'
        ]
        
        # Headers for web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    async def find_real_deals(self) -> List[Dict]:
        """Find real deals from multiple sources"""
        logger.info("Starting real deal search...")
        
        all_deals = []
        
        # Search eBay for ending auctions
        ebay_deals = await self._search_ebay_auctions()
        all_deals.extend(ebay_deals)
        
        # Search for Buy It Now deals
        bin_deals = await self._search_ebay_bin()
        all_deals.extend(bin_deals)
        
        # Filter and sort deals
        qualified_deals = self._filter_deals(all_deals)
        
        logger.info(f"Found {len(qualified_deals)} qualified deals")
        return qualified_deals
    
    async def _search_ebay_auctions(self) -> List[Dict]:
        """Search eBay for ending auctions"""
        deals = []
        
        try:
            # eBay search URL for auctions ending soon
            base_url = "https://www.ebay.com/sch/i.html"
            
            for term in self.search_terms[:5]:  # Search first 5 terms
                params = {
                    '_nkw': f'pokemon card {term}',
                    '_sacat': '2536',  # Trading Card Games
                    'LH_Auction': '1',  # Auction only
                    'LH_Time': '1',     # Ending within 24 hours
                    '_sop': '1',        # Sort by ending soonest
                    '_pgn': '1',        # First page
                    '_ipg': '25'        # 25 items per page
                }
                
                try:
                    response = self.session.get(base_url, params=params, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    items = soup.find_all('div', class_='s-item')
                    
                    for item in items[:5]:  # Process first 5 items
                        deal = self._extract_ebay_item(item, 'auction')
                        if deal:
                            deals.append(deal)
                            
                    # Wait between requests to be respectful
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error searching eBay auctions for {term}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in eBay auction search: {e}")
            
        return deals
    
    async def _search_ebay_bin(self) -> List[Dict]:
        """Search eBay for Buy It Now deals"""
        deals = []
        
        try:
            base_url = "https://www.ebay.com/sch/i.html"
            
            for term in self.search_terms[:3]:  # Search first 3 terms
                params = {
                    '_nkw': f'pokemon card {term}',
                    '_sacat': '2536',  # Trading Card Games
                    'LH_BIN': '1',      # Buy It Now only
                    '_sop': '15',       # Sort by price + shipping
                    '_pgn': '1',        # First page
                    '_ipg': '25'        # 25 items per page
                }
                
                try:
                    response = self.session.get(base_url, params=params, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    items = soup.find_all('div', class_='s-item')
                    
                    for item in items[:3]:  # Process first 3 items
                        deal = self._extract_ebay_item(item, 'bin')
                        if deal:
                            deals.append(deal)
                            
                    # Wait between requests
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error searching eBay BIN for {term}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in eBay BIN search: {e}")
            
        return deals
    
    def _extract_ebay_item(self, item, listing_type) -> Optional[Dict]:
        """Extract deal information from eBay item"""
        try:
            # Extract title
            title_elem = item.find('h3', class_='s-item__title')
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            
            # Skip if not a card listing
            if 'new listing' in title.lower() or 'pokemon' not in title.lower():
                return None
            
            # Extract price
            price_elem = item.find('span', class_='s-item__price')
            if not price_elem:
                return None
            
            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r'\$(\d+(?:\.\d{2})?)', price_text)
            if not price_match:
                return None
            
            price = float(price_match.group(1))
            
            # Skip very cheap or very expensive items
            if price < 5 or price > 500:
                return None
            
            # Extract URL
            link_elem = item.find('a', class_='s-item__link')
            url = link_elem.get('href', '') if link_elem else ''
            
            # Extract condition
            condition_elem = item.find('span', class_='SECONDARY_INFO')
            condition = condition_elem.get_text(strip=True) if condition_elem else 'Unknown'
            
            # Estimate market price (simplified)
            estimated_market = self._estimate_market_price(title, price)
            
            if estimated_market and estimated_market > price:
                profit_margin = (estimated_market - price) / price
                
                # Only include deals with decent profit potential
                if profit_margin > 0.25:  # 25% minimum
                    return {
                        'card_name': title,
                        'listing_price': price,
                        'market_price': estimated_market,
                        'profit_margin': profit_margin,
                        'platform': 'eBay',
                        'listing_type': listing_type,
                        'condition': condition,
                        'url': url,
                        'found_at': datetime.now(),
                        'confidence': self._calculate_confidence(title, profit_margin)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting eBay item: {e}")
            return None
    
    def _estimate_market_price(self, title: str, listing_price: float) -> Optional[float]:
        """Estimate market price using price database"""
        try:
            # First try to get exact match from price database
            from pokemon_price_system import get_card_market_price
            
            # Clean the title to extract card name
            card_name = self._extract_card_name(title)
            set_name = self._extract_set_name(title)
            
            # Get price from database
            market_price, confidence = get_card_market_price(card_name, set_name or "Unknown")
            
            if market_price and confidence > 0.5:
                return market_price
            
            # Fall back to keyword-based estimation
            return self._keyword_price_estimation(title, listing_price)
            
        except Exception as e:
            logger.error(f"Error estimating market price: {e}")
            return self._keyword_price_estimation(title, listing_price)
    
    def _extract_card_name(self, title: str) -> str:
        """Extract card name from title"""
        title_lower = title.lower()
        
        # Common card patterns
        patterns = [
            r'(charizard\s*(?:vmax|v|gx|ex)?)',
            r'(pikachu\s*(?:vmax|v|gx|ex)?)',
            r'(rayquaza\s*(?:vmax|v|gx|ex)?)',
            r'(umbreon\s*(?:vmax|v|gx|ex)?)',
            r'(lugia\s*(?:vmax|v|gx|ex)?)',
            r'(mewtwo\s*(?:gx|ex)?)',
            r'(alakazam\s*(?:ex)?)',
            r'(gengar\s*(?:ex)?)',
            r'(dragonite\s*(?:v)?)',
            r'(gyarados\s*(?:gx)?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title_lower)
            if match:
                return match.group(1).strip()
        
        # Extract first few words as card name
        words = title.split()[:3]
        return ' '.join(words)
    
    def _extract_set_name(self, title: str) -> Optional[str]:
        """Extract set name from title"""
        title_lower = title.lower()
        
        # Common set patterns
        sets = {
            'champions path': 'Champions Path',
            'darkness ablaze': 'Darkness Ablaze',
            'vivid voltage': 'Vivid Voltage',
            'evolving skies': 'Evolving Skies',
            'silver tempest': 'Silver Tempest',
            'base set': 'Base Set',
            'jungle': 'Jungle',
            'fossil': 'Fossil',
            'hidden fates': 'Hidden Fates',
            'shining legends': 'Shining Legends',
            'first edition': 'Base Set 1st Edition',
            '1st edition': 'Base Set 1st Edition',
            'shadowless': 'Base Set Shadowless'
        }
        
        for pattern, set_name in sets.items():
            if pattern in title_lower:
                return set_name
        
        return None
    
    def _keyword_price_estimation(self, title: str, listing_price: float) -> Optional[float]:
        """Estimate market price based on title keywords"""
        title_lower = title.lower()
        
        # Simple price estimation based on keywords
        base_multiplier = 1.5  # Conservative baseline
        
        # High-value keywords
        if any(keyword in title_lower for keyword in ['charizard', 'pikachu', 'lugia', 'rayquaza']):
            base_multiplier += 0.3
        
        if any(keyword in title_lower for keyword in ['vmax', 'gx', 'ex']):
            base_multiplier += 0.2
        
        if any(keyword in title_lower for keyword in ['psa', 'bgs', 'cgc']):
            base_multiplier += 0.4
        
        if any(keyword in title_lower for keyword in ['first edition', '1st edition', 'shadowless']):
            base_multiplier += 0.5
        
        if any(keyword in title_lower for keyword in ['base set', 'jungle', 'fossil']):
            base_multiplier += 0.3
        
        # Quality indicators
        if any(keyword in title_lower for keyword in ['mint', 'nm', 'near mint']):
            base_multiplier += 0.1
        
        if any(keyword in title_lower for keyword in ['holo', 'holographic', 'foil']):
            base_multiplier += 0.1
        
        # Negative indicators
        if any(keyword in title_lower for keyword in ['damaged', 'poor', 'played']):
            base_multiplier -= 0.2
        
        estimated_price = listing_price * base_multiplier
        
        # Sanity check
        if estimated_price > listing_price * 3:  # Cap at 3x
            estimated_price = listing_price * 3
        
        return estimated_price
    
    def _calculate_confidence(self, title: str, profit_margin: float) -> float:
        """Calculate confidence score for a deal"""
        confidence = 0.5  # Base confidence
        
        title_lower = title.lower()
        
        # High-confidence keywords
        if any(keyword in title_lower for keyword in ['psa', 'bgs', 'cgc']):
            confidence += 0.2
        
        if any(keyword in title_lower for keyword in ['first edition', '1st edition']):
            confidence += 0.15
        
        if any(keyword in title_lower for keyword in ['charizard', 'pikachu']):
            confidence += 0.1
        
        # Profit margin boost
        if profit_margin > 0.5:
            confidence += 0.1
        
        # Title quality
        if len(title.split()) > 5:  # Detailed title
            confidence += 0.05
        
        return min(confidence, 0.95)  # Cap at 95%
    
    def _filter_deals(self, deals: List[Dict]) -> List[Dict]:
        """Filter and sort deals"""
        # Remove duplicates
        seen_titles = set()
        unique_deals = []
        
        for deal in deals:
            if deal['card_name'] not in seen_titles:
                seen_titles.add(deal['card_name'])
                unique_deals.append(deal)
        
        # Filter by minimum criteria
        filtered_deals = [
            deal for deal in unique_deals
            if deal['profit_margin'] > 0.25 and deal['confidence'] > 0.6
        ]
        
        # Sort by profit margin descending
        filtered_deals.sort(key=lambda x: x['profit_margin'], reverse=True)
        
        return filtered_deals[:10]  # Return top 10
    
    def _format_deal_alert(self, deal: Dict) -> str:
        """Format deal as alert message"""
        urgency = "🔥 HIGH MARGIN" if deal['profit_margin'] > 0.5 else "💎 GOOD DEAL"
        
        message = f"{urgency} - REAL DEAL FOUND\n\n"
        message += f"🎴 Card: {deal['card_name'][:50]}...\n"
        message += f"💰 Price: ${deal['listing_price']:.2f}\n"
        message += f"📊 Est. Market: ${deal['market_price']:.2f}\n"
        message += f"📈 Profit: {deal['profit_margin']:.1%}\n"
        message += f"🏪 Platform: {deal['platform']}\n"
        message += f"📋 Type: {deal['listing_type'].upper()}\n"
        message += f"🎯 Confidence: {deal['confidence']:.1%}\n"
        message += f"🔍 Condition: {deal['condition']}\n"
        message += f"⏰ Found: {deal['found_at'].strftime('%H:%M:%S')}\n"
        
        if deal['url']:
            message += f"🔗 Link: {deal['url'][:100]}...\n"
        
        return message
    
    async def send_alert(self, message: str):
        """Send alert to Telegram"""
        try:
            await self.bot.send_message(
                chat_id=int(self.chat_id or 0),
                text=message,
                disable_web_page_preview=True
            )
            logger.info("Alert sent successfully")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send alert: {e}")
            return False
    
    async def run_deal_scanner(self, max_runs: Optional[int] = None):
        """Run the deal scanner continuously"""
        logger.info("🚀 Starting Real Deal Scanner")
        
        # Send startup message
        startup_msg = "🎴 REAL POKEMON DEAL SCANNER STARTED\n\n"
        startup_msg += "🔍 Scanning eBay for real deals...\n"
        startup_msg += "📊 Looking for 25%+ profit margins\n"
        startup_msg += "⏰ Scanning every 5 minutes\n"
        startup_msg += "🛑 Send /stop to pause\n\n"
        startup_msg += "Ready to find real money-making opportunities!"
        
        await self.send_alert(startup_msg)
        
        run_count = 0
        
        while max_runs is None or run_count < max_runs:
            try:
                logger.info(f"Starting scan #{run_count + 1}")
                
                # Find deals
                deals = await self.find_real_deals()
                
                if deals:
                    logger.info(f"Found {len(deals)} deals to alert")
                    
                    # Send alerts for top deals
                    for deal in deals[:3]:  # Top 3 deals
                        alert_message = self._format_deal_alert(deal)
                        await self.send_alert(alert_message)
                        await asyncio.sleep(2)  # Space out alerts
                
                else:
                    logger.info("No qualifying deals found this scan")
                    
                    # Send status update every 5 scans
                    if run_count % 5 == 0 and run_count > 0:
                        status_msg = f"📊 SCAN UPDATE #{run_count + 1}\n\n"
                        status_msg += f"🔍 Scanner is active and working\n"
                        status_msg += f"⏰ Last scan: {datetime.now().strftime('%H:%M:%S')}\n"
                        status_msg += f"🎯 Looking for 25%+ profit deals\n"
                        status_msg += f"📈 Next scan in 5 minutes..."
                        
                        await self.send_alert(status_msg)
                
                run_count += 1
                
                # Wait 5 minutes between scans
                logger.info("Waiting 5 minutes until next scan...")
                await asyncio.sleep(300)  # 5 minutes
                
            except KeyboardInterrupt:
                logger.info("Scanner stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in scan #{run_count + 1}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
        
        # Send shutdown message
        shutdown_msg = f"🛑 DEAL SCANNER STOPPED\n\n"
        shutdown_msg += f"📊 Completed {run_count} scans\n"
        shutdown_msg += f"⏰ Stopped at: {datetime.now().strftime('%H:%M:%S')}\n"
        shutdown_msg += f"🔄 Restart with: python3 real_deal_finder.py"
        
        await self.send_alert(shutdown_msg)

async def main():
    """Main function"""
    # Check configuration
    if not os.getenv('TG_TOKEN') or not os.getenv('TG_ADMIN_ID'):
        print("❌ Telegram not configured!")
        print("Please set TG_TOKEN and TG_ADMIN_ID in .env file")
        return
    
    print("🎴 Real Pokemon Deal Scanner")
    print("=" * 30)
    print(f"📱 Telegram Bot: {'✅ Configured' if os.getenv('TG_TOKEN') else '❌ Missing'}")
    print(f"👤 User ID: {os.getenv('TG_ADMIN_ID')}")
    print()
    
    # Ask for scan duration
    try:
        duration = input("How many scans to run? (blank for continuous): ").strip()
        max_runs = int(duration) if duration else None
    except ValueError:
        max_runs = None
    
    print(f"🚀 Starting {'continuous' if max_runs is None else f'{max_runs} scan'} mode...")
    print("📱 Check your Telegram for real deal alerts!")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    # Start the scanner
    scanner = RealDealFinder()
    
    try:
        await scanner.run_deal_scanner(max_runs)
    except KeyboardInterrupt:
        print("\n🛑 Scanner stopped by user")

if __name__ == "__main__":
    asyncio.run(main())
