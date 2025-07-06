"""
Discord Deal Feed Integration

This module integrates with Discord servers and bots that share Pokemon card deals,
providing real-time access to community-sourced opportunities.
"""

import discord
import asyncio
import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from app.core.config import settings
from app.database import SessionLocal
from app.services.pricing import PricingService

logger = logging.getLogger(__name__)

class DiscordDealFeed:
    """Discord bot to monitor deal feed channels"""
    
    def __init__(self):
        self.client = None
        self.db = SessionLocal()
        self.pricing_service = PricingService(self.db)
        
        # Common deal patterns in Discord messages
        self.deal_patterns = {
            'price': r'\$(\d+(?:\.\d{2})?)',
            'card_name': r'([A-Za-z\s]+(?:ex|EX|GX|V|VMAX|VSTAR|Prime|Lv\.X))',
            'set': r'(Base Set|Jungle|Fossil|Team Rocket|Neo|Gym|E-Card|EX|Diamond|Pearl|Platinum|HeartGold|SoulSilver|Black|White|XY|Sun|Moon|Sword|Shield|Brilliant|Fusion|Astral|Lost|Silver|Paldea|Obsidian|Stellar)',
            'condition': r'(NM|LP|MP|HP|DMG|PSA|BGS|CGC)',
            'platform': r'(eBay|TCGPlayer|COMC|Mercari|Facebook|Local)',
            'urgency': r'(ending soon|few hours|minutes left|BIN|OBO)'
        }
    
    async def start_discord_monitoring(self):
        """Start Discord bot to monitor deal feeds"""
        if not settings.DISCORD_BOT_TOKEN:
            logger.warning("Discord bot token not configured")
            return
            
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            
            self.client = discord.Client(intents=intents)
            
            @self.client.event
            async def on_ready():
                logger.info(f"Discord bot logged in as {self.client.user}")
                
                # Join relevant channels
                await self._join_deal_channels()
            
            @self.client.event
            async def on_message(message):
                if message.author == self.client.user:
                    return
                
                # Process deal messages
                await self._process_deal_message(message)
            
            # Start the bot
            await self.client.start(settings.DISCORD_BOT_TOKEN)
            
        except Exception as e:
            logger.error(f"Error starting Discord bot: {e}")
    
    async def _join_deal_channels(self):
        """Join relevant deal feed channels"""
        if not settings.DISCORD_DEAL_CHANNELS:
            return
            
        channel_ids = settings.DISCORD_DEAL_CHANNELS.split(',')
        
        for channel_id in channel_ids:
            try:
                channel = self.client.get_channel(int(channel_id.strip()))
                if channel:
                    logger.info(f"Monitoring channel: {channel.name}")
                else:
                    logger.warning(f"Could not find channel: {channel_id}")
            except Exception as e:
                logger.error(f"Error joining channel {channel_id}: {e}")
    
    async def _process_deal_message(self, message):
        """Process potential deal messages"""
        try:
            content = message.content.lower()
            
            # Skip if message doesn't contain deal indicators
            deal_indicators = ['pokemon', 'card', 'deal', '$', 'price', 'sale', 'auction']
            if not any(indicator in content for indicator in deal_indicators):
                return
            
            # Extract deal information
            deal_info = self._extract_deal_info(message.content)
            
            if deal_info:
                # Evaluate the deal
                evaluation = await self._evaluate_discord_deal(deal_info)
                
                if evaluation['is_good_deal']:
                    # Save deal to database
                    await self._save_discord_deal(deal_info, evaluation, message)
                    
                    # Send notification for high-quality deals
                    if evaluation['confidence'] > 0.7:
                        await self._send_discord_deal_notification(deal_info, evaluation, message)
                        
        except Exception as e:
            logger.error(f"Error processing Discord message: {e}")
    
    def _extract_deal_info(self, content: str) -> Optional[Dict]:
        """Extract deal information from Discord message"""
        try:
            deal_info = {}
            
            # Extract price
            price_match = re.search(self.deal_patterns['price'], content)
            if price_match:
                deal_info['price'] = float(price_match.group(1))
            
            # Extract card name
            card_match = re.search(self.deal_patterns['card_name'], content, re.IGNORECASE)
            if card_match:
                deal_info['card_name'] = card_match.group(1).strip()
            
            # Extract set
            set_match = re.search(self.deal_patterns['set'], content, re.IGNORECASE)
            if set_match:
                deal_info['set_name'] = set_match.group(1)
            
            # Extract condition
            condition_match = re.search(self.deal_patterns['condition'], content, re.IGNORECASE)
            if condition_match:
                deal_info['condition'] = condition_match.group(1)
            
            # Extract platform
            platform_match = re.search(self.deal_patterns['platform'], content, re.IGNORECASE)
            if platform_match:
                deal_info['platform'] = platform_match.group(1).lower()
            
            # Check for urgency indicators
            urgency_match = re.search(self.deal_patterns['urgency'], content, re.IGNORECASE)
            deal_info['urgent'] = bool(urgency_match)
            
            # Only return if we have minimum required info
            if 'price' in deal_info and ('card_name' in deal_info or 'set_name' in deal_info):
                return deal_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting deal info: {e}")
            return None
    
    async def _evaluate_discord_deal(self, deal_info: Dict) -> Dict:
        """Evaluate if Discord deal is worth pursuing"""
        try:
            evaluation = {
                'is_good_deal': False,
                'confidence': 0.0,
                'profit_margin': 0.0,
                'market_price': 0.0,
                'reasons': []
            }
            
            # Get market price
            if 'card_name' in deal_info:
                market_price = await self.pricing_service.get_market_price(
                    deal_info['card_name'],
                    deal_info.get('set_name', 'Unknown')
                )
                
                if market_price:
                    evaluation['market_price'] = market_price
                    
                    # Calculate profit margin
                    listing_price = deal_info['price']
                    profit_margin = (market_price - listing_price) / listing_price
                    evaluation['profit_margin'] = profit_margin
                    
                    # Evaluate deal quality
                    if profit_margin > 0.3:  # 30%+ margin
                        evaluation['is_good_deal'] = True
                        evaluation['confidence'] = min(0.9, profit_margin)
                        evaluation['reasons'].append(f"High profit margin: {profit_margin:.1%}")
                    
                    # Boost confidence for certain conditions
                    if deal_info.get('condition') in ['NM', 'PSA', 'BGS']:
                        evaluation['confidence'] += 0.1
                        evaluation['reasons'].append("High-grade condition")
                    
                    # Boost confidence for urgency
                    if deal_info.get('urgent'):
                        evaluation['confidence'] += 0.1
                        evaluation['reasons'].append("Time-sensitive opportunity")
                    
                    # Boost confidence for reliable platforms
                    if deal_info.get('platform') in ['ebay', 'tcgplayer']:
                        evaluation['confidence'] += 0.1
                        evaluation['reasons'].append("Trusted platform")
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating Discord deal: {e}")
            return {'is_good_deal': False, 'confidence': 0.0, 'profit_margin': 0.0, 'market_price': 0.0, 'reasons': []}
    
    async def _save_discord_deal(self, deal_info: Dict, evaluation: Dict, message):
        """Save Discord deal to database"""
        try:
            from app.models.database import Deal
            
            deal = Deal(
                card_name=deal_info.get('card_name', 'Unknown'),
                set_name=deal_info.get('set_name', 'Unknown'),
                listing_price=deal_info['price'],
                market_price=evaluation['market_price'],
                profit_margin=evaluation['profit_margin'],
                platform='discord',
                listing_url=f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}",
                condition=deal_info.get('condition', 'Unknown'),
                source='discord_feed',
                confidence=evaluation['confidence'],
                found_at=datetime.utcnow()
            )
            
            self.db.add(deal)
            self.db.commit()
            
            logger.info(f"Saved Discord deal: {deal_info.get('card_name', 'Unknown')} - {evaluation['profit_margin']:.1%} margin")
            
        except Exception as e:
            logger.error(f"Error saving Discord deal: {e}")
    
    async def _send_discord_deal_notification(self, deal_info: Dict, evaluation: Dict, message):
        """Send notification for high-quality Discord deals"""
        try:
            from app.telegram.bot import send_message
            
            notification = f"🎮 DISCORD DEAL ALERT\n\n"
            notification += f"Card: {deal_info.get('card_name', 'Unknown')}\n"
            notification += f"Set: {deal_info.get('set_name', 'Unknown')}\n"
            notification += f"Price: ${deal_info['price']:.2f}\n"
            notification += f"Market: ${evaluation['market_price']:.2f}\n"
            notification += f"Profit: {evaluation['profit_margin']:.1%}\n"
            notification += f"Confidence: {evaluation['confidence']:.1%}\n"
            notification += f"Platform: {deal_info.get('platform', 'Unknown')}\n"
            notification += f"Condition: {deal_info.get('condition', 'Unknown')}\n"
            
            if deal_info.get('urgent'):
                notification += f"⚡ URGENT: Time-sensitive!\n"
            
            notification += f"Source: {message.guild.name} #{message.channel.name}\n"
            notification += f"Link: https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}\n"
            
            await send_message(notification)
            
        except Exception as e:
            logger.error(f"Error sending Discord deal notification: {e}")
    
    async def stop_discord_monitoring(self):
        """Stop Discord bot"""
        if self.client:
            await self.client.close()
            logger.info("Discord bot stopped")

# Global Discord feed instance
discord_feed = DiscordDealFeed()

async def start_discord_feed():
    """Start Discord deal feed monitoring"""
    logger.info("Starting Discord deal feed monitoring...")
    await discord_feed.start_discord_monitoring()

async def stop_discord_feed():
    """Stop Discord deal feed monitoring"""
    logger.info("Stopping Discord deal feed monitoring...")
    await discord_feed.stop_discord_monitoring()

if __name__ == "__main__":
    # For testing
    asyncio.run(start_discord_feed())
