#!/usr/bin/env python3
"""
Single Deal Lifecycle Manager - Enforces one active deal at a time
Logs all deals but only alerts when no active investment exists
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from ebay_public_search import EbayPublicSearcher
from quick_price import get_card_market_price
from smart_mvp_bot_fixed import send_smart_deal_alert, send_session_summary

def calculate_profit(purchase_price: float, estimated_sale_price: float, grading_cost: float = 25, ebay_fees: float = 0.13) -> Dict:
    """Calculate profit potential for a deal"""
    total_cost = purchase_price + grading_cost
    ebay_fee_amount = estimated_sale_price * ebay_fees
    net_proceeds = estimated_sale_price - ebay_fee_amount
    net_profit = net_proceeds - total_cost
    profit_percentage = (net_profit / total_cost) * 100
    
    return {
        'total_cost': total_cost,
        'net_proceeds': net_proceeds,
        'net_profit': net_profit,
        'profit_percentage': profit_percentage,
        'ebay_fees': ebay_fee_amount
    }

class SingleDealManager:
    """Manages single deal lifecycle with enhanced logging"""
    
    def __init__(self):
        self.deals_log_file = "single_deal_log.json"
        self.active_deals_file = "active_deals.json"
        self.ebay_searcher = EbayPublicSearcher()
        self.session_stats = {
            'deals_found': 0,
            'deals_alerted': 0,
            'deals_skipped': 0,
            'deals_logged': 0,
            'session_start': datetime.now().isoformat()
        }
        
    def load_active_deals(self) -> List[Dict]:
        """Load current active deals"""
        try:
            if os.path.exists(self.active_deals_file):
                with open(self.active_deals_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading active deals: {e}")
        return []
    
    def save_active_deals(self, deals: List[Dict]) -> bool:
        """Save active deals list"""
        try:
            with open(self.active_deals_file, 'w') as f:
                json.dump(deals, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving active deals: {e}")
            return False
    
    def log_deal(self, deal: Dict, status: str) -> bool:
        """Log all deals with status tracking"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'deal': deal,
                'status': status,  # 'found', 'alerted', 'skipped', 'approved', 'rejected'
                'session_id': self.session_stats['session_start']
            }
            
            # Append to log file
            logs = []
            if os.path.exists(self.deals_log_file):
                with open(self.deals_log_file, 'r') as f:
                    logs = json.load(f)
            
            logs.append(log_entry)
            
            # Keep only last 100 deals to prevent huge files
            if len(logs) > 100:
                logs = logs[-100:]
            
            with open(self.deals_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Error logging deal: {e}")
            return False
    
    def has_active_deals(self) -> bool:
        """Check if we have any active deals"""
        active_deals = self.load_active_deals()
        return len(active_deals) > 0
    
    def get_active_deal_count(self) -> int:
        """Get count of active deals"""
        return len(self.load_active_deals())
    
    def get_total_exposure(self) -> float:
        """Calculate total capital at risk"""
        active_deals = self.load_active_deals()
        return sum(deal.get('investment_amount', 0) for deal in active_deals)
    
    async def evaluate_deal(self, listing: Dict) -> Optional[Dict]:
        """Evaluate a single listing for profit potential"""
        try:
            # Extract basic info
            title = listing.get('title', '')
            price_str = listing.get('price', '0')
            
            # Clean price (remove $ and commas)
            price = float(price_str.replace('$', '').replace(',', ''))
            
            # Skip if too cheap (likely not what we want) or too expensive for single deal strategy
            if price < 200 or price > 800:  # Conservative range for single deal focus
                return None
            
            # Extract card info from title
            card_info = self.extract_card_info(title)
            if not card_info:
                return None
            
            # Get price estimate
            price, confidence = get_card_market_price(card_info['card_name'], card_info['set_name'])
            if not price or price < 1000:  # Need minimum PSA 10 value for good deals
                return None
            
            # Use PSA 10 estimate (price is raw, multiply by typical grading premium)
            psa10_price = price * 1.5  # Conservative PSA 10 premium
            
            # Calculate profit potential
            profit_calc = calculate_profit(
                purchase_price=price,
                estimated_sale_price=psa10_price,
                grading_cost=25,
                ebay_fees=0.13  # 13% total fees
            )
            
            # Filter for good opportunities (minimum 150% ROI for single deal focus)
            if profit_calc['profit_percentage'] < 150:
                return None
            
            # Create deal object
            deal = {
                'card_name': card_info['card_name'],
                'set_name': card_info['set_name'],
                'raw_price': price,
                'estimated_psa10_price': psa10_price,
                'potential_profit': profit_calc['net_profit'],
                'roi_percentage': profit_calc['profit_percentage'],
                'condition_notes': title,
                'listing_url': listing.get('url', ''),
                'found_timestamp': datetime.now().isoformat()
            }
            
            return deal
            
        except Exception as e:
            print(f"⚠️ Error evaluating deal: {e}")
            return None
    
    def extract_card_info(self, title: str) -> Optional[Dict]:
        """Extract card name and set from listing title"""
        title_lower = title.lower()
        
        # Popular cards to target
        card_patterns = {
            'charizard': 'Charizard',
            'blastoise': 'Blastoise', 
            'venusaur': 'Venusaur',
            'pikachu': 'Pikachu',
            'alakazam': 'Alakazam',
            'mewtwo': 'Mewtwo',
            'dragonite': 'Dragonite',
            'machamp': 'Machamp'
        }
        
        # Set patterns
        set_patterns = {
            'base set': 'Base Set',
            'shadowless': 'Base Set Shadowless',
            'jungle': 'Jungle',
            'fossil': 'Fossil',
            'team rocket': 'Team Rocket',
            'gym heroes': 'Gym Heroes',
            'gym challenge': 'Gym Challenge'
        }
        
        # Find card
        card_name = None
        for pattern, name in card_patterns.items():
            if pattern in title_lower:
                card_name = name
                break
        
        if not card_name:
            return None
        
        # Find set
        set_name = 'Base Set'  # Default
        for pattern, name in set_patterns.items():
            if pattern in title_lower:
                set_name = name
                break
        
        return {'card_name': card_name, 'set_name': set_name}
    
    async def scan_for_deals(self, max_deals: int = 5) -> List[Dict]:
        """Scan eBay for potential deals"""
        print("🔍 Scanning for Pokemon card deals...")
        
        # Search terms focused on high-value cards
        search_terms = [
            "charizard base set psa ready",
            "blastoise shadowless near mint",
            "venusaur base set raw",
            "pikachu vintage pokemon nm"
        ]
        
        all_deals = []
        
        for term in search_terms:
            try:
                print(f"   Searching: {term}")
                results = self.ebay_searcher.search_pokemon_cards(term, min_price=200, max_price=800, limit=10)
                
                for listing in results:
                    deal = await self.evaluate_deal(listing)
                    if deal:
                        all_deals.append(deal)
                        self.session_stats['deals_found'] += 1
                        self.log_deal(deal, 'found')
                        
                        if len(all_deals) >= max_deals:
                            break
                
                if len(all_deals) >= max_deals:
                    break
                    
            except Exception as e:
                print(f"⚠️ Error searching '{term}': {e}")
                continue
        
        print(f"   Found {len(all_deals)} potential deals")
        return all_deals
    
    async def process_deals(self, deals: List[Dict]) -> bool:
        """Process deals based on single deal strategy"""
        if not deals:
            print("No deals found to process")
            return False
        
        # Check if we have active deals
        active_count = self.get_active_deal_count()
        
        if active_count > 0:
            # Log all deals but don't alert
            print(f"⏸️ Active deal exists. Logging {len(deals)} new deals without alerting")
            for deal in deals:
                self.log_deal(deal, 'skipped')
                self.session_stats['deals_skipped'] += 1
            return False
        
        # No active deals - process the best one
        best_deal = max(deals, key=lambda d: d['roi_percentage'])
        
        # Generate deal ID
        deal_id = f"SDL_{datetime.now().strftime('%m%d_%H%M')}"
        
        # Send alert
        success = await send_smart_deal_alert(best_deal, deal_id)
        
        if success:
            # Log as alerted
            self.log_deal(best_deal, 'alerted')
            self.session_stats['deals_alerted'] += 1
            
            # Add to active deals (waiting for approval)
            active_deals = self.load_active_deals()
            active_deals.append({
                'deal_id': deal_id,
                'deal': best_deal,
                'status': 'pending_approval',
                'alerted_timestamp': datetime.now().isoformat(),
                'investment_amount': best_deal['raw_price'] + 25  # Include grading cost
            })
            self.save_active_deals(active_deals)
            
            print(f"✅ Deal {deal_id} alerted and marked as pending approval")
            
            # Log remaining deals as skipped
            for deal in deals:
                if deal != best_deal:
                    self.log_deal(deal, 'skipped')
                    self.session_stats['deals_skipped'] += 1
            
            return True
        
        return False
    
    async def run_single_scan(self) -> bool:
        """Run a single deal scan cycle"""
        print("🎯 Single Deal Manager - Starting scan")
        print("=" * 40)
        
        # Check current status
        active_count = self.get_active_deal_count()
        total_exposure = self.get_total_exposure()
        
        print(f"📊 Current Status:")
        print(f"   Active deals: {active_count}")
        print(f"   Capital at risk: ${total_exposure:.0f}")
        print()
        
        # Scan for deals
        deals = await self.scan_for_deals()
        
        # Process based on single deal strategy
        if deals:
            await self.process_deals(deals)
        
        # Send session summary
        self.session_stats['active_deals'] = active_count
        self.session_stats['next_scan'] = "Manual (single deal focus)"
        await send_session_summary(self.session_stats)
        
        print("\n📊 Session Complete:")
        print(f"   Found: {self.session_stats['deals_found']}")
        print(f"   Alerted: {self.session_stats['deals_alerted']}")
        print(f"   Skipped: {self.session_stats['deals_skipped']}")
        
        return True

# Manual approval/rejection functions
def approve_deal(deal_id: str) -> bool:
    """Manually approve a deal (move from pending to active)"""
    try:
        manager = SingleDealManager()
        active_deals = manager.load_active_deals()
        
        for deal in active_deals:
            if deal['deal_id'] == deal_id and deal['status'] == 'pending_approval':
                deal['status'] = 'approved'
                deal['approved_timestamp'] = datetime.now().isoformat()
                manager.save_active_deals(active_deals)
                manager.log_deal(deal['deal'], 'approved')
                print(f"✅ Deal {deal_id} approved and activated")
                return True
        
        print(f"❌ Deal {deal_id} not found or not pending")
        return False
        
    except Exception as e:
        print(f"❌ Error approving deal: {e}")
        return False

def reject_deal(deal_id: str) -> bool:
    """Manually reject a deal (remove from active)"""
    try:
        manager = SingleDealManager()
        active_deals = manager.load_active_deals()
        
        for i, deal in enumerate(active_deals):
            if deal['deal_id'] == deal_id:
                rejected_deal = active_deals.pop(i)
                manager.save_active_deals(active_deals)
                manager.log_deal(rejected_deal['deal'], 'rejected')
                print(f"❌ Deal {deal_id} rejected and removed")
                return True
        
        print(f"❌ Deal {deal_id} not found")
        return False
        
    except Exception as e:
        print(f"❌ Error rejecting deal: {e}")
        return False

# CLI interface
async def main():
    """Main CLI interface"""
    manager = SingleDealManager()
    
    print("🎯 Single Deal Lifecycle Manager")
    print("=" * 35)
    print("1. Run deal scan")
    print("2. Check active deals")
    print("3. Approve deal")
    print("4. Reject deal")
    print("5. View deal log")
    
    choice = input("Choose option (1-5): ").strip()
    
    if choice == "1":
        await manager.run_single_scan()
    elif choice == "2":
        active_deals = manager.load_active_deals()
        print(f"\n📊 Active Deals: {len(active_deals)}")
        for deal in active_deals:
            print(f"   {deal['deal_id']}: {deal['status']} - ${deal['investment_amount']:.0f}")
    elif choice == "3":
        deal_id = input("Enter Deal ID to approve: ").strip()
        approve_deal(deal_id)
    elif choice == "4":
        deal_id = input("Enter Deal ID to reject: ").strip()
        reject_deal(deal_id)
    elif choice == "5":
        try:
            if os.path.exists(manager.deals_log_file):
                with open(manager.deals_log_file, 'r') as f:
                    logs = json.load(f)
                print(f"\n📋 Recent Deals ({len(logs)} total):")
                for log in logs[-10:]:  # Show last 10
                    timestamp = log['timestamp'][:16].replace('T', ' ')
                    status = log['status']
                    card = log['deal'].get('card_name', 'Unknown')
                    profit = log['deal'].get('potential_profit', 0)
                    print(f"   {timestamp} | {status:8} | {card:12} | ${profit:4.0f}")
            else:
                print("No deal log found")
        except Exception as e:
            print(f"Error reading log: {e}")

if __name__ == "__main__":
    asyncio.run(main())
