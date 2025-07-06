"""
Enhanced Deal Discovery Service - Community Insights Integration

Based on latest Pokemon card arbitrage research from trading communities
"""

import asyncio
import discord
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.deal_finder import DealFinder
from app.services.external_apis import EbayAPI, TCGPlayerAPI

logger = logging.getLogger(__name__)

class EnhancedDealFinder(DealFinder):
    """Enhanced deal finder with community insights and automation"""
    
    def __init__(self, db):
        super().__init__(db)
        self.discord_client = None
        self.reprint_blacklist = set()
        self.setup_discord_feeds()
    
    def setup_discord_feeds(self):
        """Setup Discord bot to monitor deal feeds"""
        if not settings.DISCORD_BOT_TOKEN:
            logger.warning("Discord bot token not configured")
            return
            
        # This would connect to Discord deal feed channels
        # Implementation would depend on specific Discord bots/channels
        pass
    
    async def find_enhanced_deals(self) -> List[Dict]:
        """Enhanced deal finding with community heuristics"""
        all_deals = []
        
        # 1. Off-peak auction scanning (midnight-noon advantage)
        current_hour = datetime.now().hour
        if 0 <= current_hour <= 12:
            logger.info("Running off-peak auction scan")
            auction_deals = await self._scan_ending_auctions()
            all_deals.extend(auction_deals)
        
        # 2. Wide filter scanning for mis-titled listings
        wide_filter_deals = await self._scan_with_wide_filters()
        all_deals.extend(wide_filter_deals)
        
        # 3. Bulk lot opportunities
        lot_deals = await self._scan_bulk_lots()
        all_deals.extend(lot_deals)
        
        # 4. Discord feed integration
        discord_deals = await self._get_discord_deals()
        all_deals.extend(discord_deals)
        
        # 5. Filter against reprint blacklist
        filtered_deals = self._filter_reprint_risk(all_deals)
        
        return filtered_deals
    
    async def _scan_ending_auctions(self) -> List[Dict]:
        """Scan eBay auctions ending soon for off-peak opportunities"""
        try:
            # Search for auctions ending in next 4 hours
            end_time_from = datetime.now()
            end_time_to = end_time_from + timedelta(hours=4)
            
            search_params = {
                'keywords': 'pokemon card',
                'categoryId': '2536',  # Trading Card Games
                'itemFilter': [
                    {'name': 'ListingType', 'value': 'Auction'},
                    {'name': 'EndTimeTo', 'value': end_time_to.isoformat()},
                    {'name': 'MinPrice', 'value': '5'},
                    {'name': 'MaxPrice', 'value': '200'}
                ],
                'sortOrder': 'EndTimeSoonest'
            }
            
            # This would use eBay Finding API for auctions
            # For now, return sample data
            return [
                {
                    'source': 'ebay_auction',
                    'card_name': 'Charizard VMAX',
                    'current_bid': 45.00,
                    'market_price': 75.00,
                    'ends_at': end_time_to,
                    'auction_id': 'sample_123'
                }
            ]
            
        except Exception as e:
            logger.error(f"Error scanning ending auctions: {e}")
            return []
    
    async def _scan_with_wide_filters(self) -> List[Dict]:
        """Scan with broad filters to catch mis-titled listings"""
        try:
            # Use vague search terms to find mis-titled listings
            vague_searches = [
                'pokemon holo',
                'pokemon rare',
                'pokemon vintage',
                'pokemon card lot',
                'pokemon collection',
                'tcg pokemon'
            ]
            
            deals = []
            for search_term in vague_searches:
                items = self.ebay_api.search_items(
                    keywords=search_term,
                    max_price=100,
                    condition="1000"
                )
                
                for item in items[:10]:  # Limit to avoid rate limits
                    deal = self._evaluate_wide_filter_item(item)
                    if deal:
                        deals.append(deal)
            
            return deals
            
        except Exception as e:
            logger.error(f"Error scanning with wide filters: {e}")
            return []
    
    async def _scan_bulk_lots(self) -> List[Dict]:
        """Scan for bulk lot opportunities"""
        try:
            bulk_searches = [
                'pokemon card lot',
                'pokemon collection',
                'pokemon cards bulk',
                'pokemon binder'
            ]
            
            deals = []
            for search_term in bulk_searches:
                items = self.ebay_api.search_items(
                    keywords=search_term,
                    max_price=500  # Higher limit for lots
                )
                
                for item in items[:5]:  # Even more selective for lots
                    deal = self._evaluate_bulk_lot(item)
                    if deal:
                        deals.append(deal)
            
            return deals
            
        except Exception as e:
            logger.error(f"Error scanning bulk lots: {e}")
            return []
    
    async def _get_discord_deals(self) -> List[Dict]:
        """Get deals from Discord bot feeds"""
        try:
            # This would integrate with Discord deal bots like PokeDeals
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting Discord deals: {e}")
            return []
    
    def _evaluate_wide_filter_item(self, item: Dict) -> Optional[Dict]:
        """Evaluate items from wide filter searches"""
        try:
            title = item.get('title', '').lower()
            price = float(item.get('price', {}).get('value', 0))
            
            # Look for valuable keywords in title
            valuable_keywords = [
                'charizard', 'pikachu', 'lugia', 'rayquaza', 'mewtwo',
                'first edition', '1st edition', 'shadowless', 'base set',
                'psa', 'bgs', 'holo', 'holographic', 'secret rare'
            ]
            
            keyword_matches = sum(1 for keyword in valuable_keywords if keyword in title)
            
            # If multiple valuable keywords and reasonable price, flag for review
            if keyword_matches >= 2 and 5 <= price <= 200:
                return {
                    'source': 'wide_filter',
                    'card_name': item.get('title', 'Unknown'),
                    'listing_price': price,
                    'market_price': price * 1.5,  # Estimate for wide filter
                    'profit_margin': 0.33,  # Conservative estimate
                    'platform': 'ebay',
                    'listing_url': item.get('itemWebUrl'),
                    'confidence': 'medium'  # Lower confidence for wide filter
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error evaluating wide filter item: {e}")
            return None
    
    def _evaluate_bulk_lot(self, item: Dict) -> Optional[Dict]:
        """Evaluate bulk lot opportunities"""
        try:
            title = item.get('title', '').lower()
            price = float(item.get('price', {}).get('value', 0))
            
            # Look for lot indicators
            lot_indicators = ['lot', 'collection', 'binder', 'bulk', 'cards']
            has_lot_indicator = any(indicator in title for indicator in lot_indicators)
            
            # Look for quantity indicators
            import re
            quantity_match = re.search(r'(\d+)\s*(cards?|pokemon)', title)
            estimated_cards = int(quantity_match.group(1)) if quantity_match else 10
            
            # Calculate per-card cost
            per_card_cost = price / estimated_cards if estimated_cards > 0 else price
            
            # If per-card cost is very low, it might be profitable
            if has_lot_indicator and per_card_cost < 2.0 and price >= 20:
                return {
                    'source': 'bulk_lot',
                    'card_name': f"Bulk Lot ({estimated_cards} cards)",
                    'listing_price': price,
                    'market_price': price * 2,  # Conservative 2x estimate
                    'profit_margin': 0.50,  # Higher margin for lots
                    'platform': 'ebay',
                    'listing_url': item.get('itemWebUrl'),
                    'estimated_cards': estimated_cards,
                    'per_card_cost': per_card_cost
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error evaluating bulk lot: {e}")
            return None
    
    def _filter_reprint_risk(self, deals: List[Dict]) -> List[Dict]:
        """Filter out deals with high reprint risk"""
        filtered = []
        
        for deal in deals:
            card_name = deal.get('card_name', '').lower()
            
            # Check against reprint blacklist
            if any(blacklisted in card_name for blacklisted in self.reprint_blacklist):
                logger.info(f"Filtering {card_name} due to reprint risk")
                continue
            
            # Add reprint risk score
            deal['reprint_risk'] = self._calculate_reprint_risk(card_name)
            
            # Only include deals with low-medium reprint risk
            if deal['reprint_risk'] <= 0.7:
                filtered.append(deal)
        
        return filtered
    
    def _calculate_reprint_risk(self, card_name: str) -> float:
        """Calculate reprint risk score (0.0 = no risk, 1.0 = high risk)"""
        high_risk_indicators = [
            'charizard',  # Frequently reprinted
            'pikachu',    # Very frequently reprinted
            'mewtwo',     # Often reprinted
        ]
        
        medium_risk_indicators = [
            'vmax', 'v card', 'gx',  # Modern mechanics
            'sword shield', 'sun moon',  # Recent sets
        ]
        
        low_risk_indicators = [
            'first edition', '1st edition',
            'shadowless', 'base set unlimited',
            'neo', 'gym', 'team rocket'  # Vintage sets
        ]
        
        risk_score = 0.5  # Base risk
        
        for indicator in high_risk_indicators:
            if indicator in card_name:
                risk_score += 0.3
        
        for indicator in medium_risk_indicators:
            if indicator in card_name:
                risk_score += 0.2
        
        for indicator in low_risk_indicators:
            if indicator in card_name:
                risk_score -= 0.3
        
        return max(0.0, min(1.0, risk_score))
    
    async def update_reprint_blacklist(self):
        """Update reprint blacklist from Pokemon news sources"""
        try:
            # This would scrape Pokemon news sites for reprint announcements
            # For now, use a static list of known reprints
            new_reprints = {
                'pokemon go charizard',
                'celebrations charizard',
                'classic collection'
            }
            
            self.reprint_blacklist.update(new_reprints)
            logger.info(f"Updated reprint blacklist: {len(self.reprint_blacklist)} items")
            
        except Exception as e:
            logger.error(f"Error updating reprint blacklist: {e}")

class AutoBuyService:
    """Service for automatic purchase execution"""
    
    def __init__(self, db):
        self.db = db
        self.ebay_api = EbayAPI()
        self.enabled = False
        self.daily_limit = settings.DAILY_SPEND_LIMIT
        self.daily_spent = 0.0
    
    async def auto_purchase_deal(self, deal: Dict) -> bool:
        """Automatically purchase a qualifying deal"""
        try:
            if not self.enabled:
                logger.info("Auto-buy disabled, skipping purchase")
                return False
            
            # Check daily spending limit
            if self.daily_spent + deal['listing_price'] > self.daily_limit:
                logger.warning(f"Daily limit exceeded, skipping purchase")
                return False
            
            # Additional safety checks
            if not self._passes_safety_checks(deal):
                return False
            
            # Execute purchase (this would use eBay Buy API)
            success = await self._execute_purchase(deal)
            
            if success:
                self.daily_spent += deal['listing_price']
                logger.info(f"Auto-purchased: {deal['card_name']} for ${deal['listing_price']}")
                
                # Update deal status in database
                self._update_deal_status(deal, 'purchased')
                
                # Send Telegram notification
                await self._send_purchase_notification(deal)
            
            return success
            
        except Exception as e:
            logger.error(f"Error in auto-purchase: {e}")
            return False
    
    def _passes_safety_checks(self, deal: Dict) -> bool:
        """Run safety checks before auto-purchase"""
        # Check profit margin threshold
        if deal.get('profit_margin', 0) < settings.MIN_PROFIT_MARGIN:
            return False
        
        # Check position size limit
        max_position = settings.STARTING_BANKROLL * (settings.MAX_POSITION_PERCENT / 100)
        if deal['listing_price'] > max_position:
            return False
        
        # Check reprint risk
        if deal.get('reprint_risk', 0) > 0.7:
            return False
        
        # Check seller feedback (for eBay)
        if deal.get('platform') == 'ebay':
            seller_feedback = deal.get('seller_feedback', 0)
            if seller_feedback < 98:  # Require 98%+ feedback
                return False
        
        return True
    
    async def _execute_purchase(self, deal: Dict) -> bool:
        """Execute the actual purchase"""
        try:
            # This would implement actual eBay purchase API calls
            # For now, simulate success
            await asyncio.sleep(1)  # Simulate API call
            return True
            
        except Exception as e:
            logger.error(f"Error executing purchase: {e}")
            return False
    
    def _update_deal_status(self, deal: Dict, status: str):
        """Update deal status in database"""
        # Implementation would update the deal record
        pass
    
    async def _send_purchase_notification(self, deal: Dict):
        """Send Telegram notification about purchase"""
        from app.telegram.bot import send_message
        
        message = f"🤖 AUTO-PURCHASE EXECUTED\n\n"
        message += f"Card: {deal['card_name']}\n"
        message += f"Price: ${deal['listing_price']:.2f}\n"
        message += f"Market: ${deal['market_price']:.2f}\n"
        message += f"Profit: {deal['profit_margin']:.1%}\n"
        message += f"Platform: {deal['platform']}\n"
        message += f"Daily Spent: ${self.daily_spent:.2f} / ${self.daily_limit:.2f}"
        
        send_message(message)
    
    def enable_auto_buy(self, daily_limit: float = None):
        """Enable auto-buying with optional daily limit"""
        self.enabled = True
        if daily_limit:
            self.daily_limit = daily_limit
        logger.info(f"Auto-buy enabled with ${self.daily_limit} daily limit")
    
    def disable_auto_buy(self):
        """Disable auto-buying"""
        self.enabled = False
        logger.info("Auto-buy disabled")
    
    def reset_daily_spending(self):
        """Reset daily spending counter (called daily at midnight)"""
        self.daily_spent = 0.0
        logger.info("Daily spending counter reset")
