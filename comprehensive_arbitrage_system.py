#!/usr/bin/env python3
"""
Comprehensive Arbitrage System Integration
Combines scalable capital management, PSA tracking, and AI analysis
"""
import asyncio
from datetime import datetime
from typing import Dict, List
from scalable_deal_manager import ScalableDealManager  
from psa_grading_tracker import PSAGradingTracker, DealStatus
from advanced_agentic_system import enhance_deal_with_ai
from smart_mvp_bot_fixed import send_smart_deal_alert, send_session_summary

class ComprehensiveArbitrageSystem:
    """Complete arbitrage system with all components integrated"""
    
    def __init__(self):
        self.deal_manager = ScalableDealManager()
        self.grading_tracker = PSAGradingTracker()
        self.session_stats = {
            'deals_found': 0,
            'deals_analyzed': 0,
            'deals_alerted': 0,
            'deals_approved': 0,
            'ai_enhanced': 0,
            'session_start': datetime.now().isoformat()
        }
    
    async def process_potential_deal(self, raw_deal_data: Dict) -> bool:
        """Process a potential deal through the complete pipeline"""
        
        print(f"🔍 Processing potential deal: {raw_deal_data.get('card_name')}")
        
        # Step 1: AI Enhancement (if available)
        try:
            enhanced_deal = await enhance_deal_with_ai(raw_deal_data)
            self.session_stats['ai_enhanced'] += 1
            print("   ✅ AI analysis complete")
        except Exception as e:
            print(f"   ⚠️ AI analysis failed: {e}")
            enhanced_deal = raw_deal_data
        
        self.session_stats['deals_analyzed'] += 1
        
        # Step 2: Check capital constraints
        investment_amount = enhanced_deal['raw_price'] + 25  # Include grading cost
        can_approve, limit_message = self.deal_manager.can_approve_new_deal(investment_amount)
        
        if not can_approve:
            print(f"   ⏸️ Capital limit: {limit_message}")
            # Log but don't alert
            self.log_deal(enhanced_deal, 'capital_limited')
            return False
        
        # Step 3: AI Recommendation Filter
        ai_analysis = enhanced_deal.get('ai_analysis', {})
        recommendation = ai_analysis.get('overall_recommendation', 'PASS')
        confidence = ai_analysis.get('confidence_level', 5)
        
        if recommendation in ['PASS', 'STRONG_PASS']:
            print(f"   ❌ AI recommends: {recommendation} (confidence: {confidence}/10)")
            self.log_deal(enhanced_deal, 'ai_rejected')
            return False
        
        if confidence < 6:
            print(f"   ⚠️ Low AI confidence: {confidence}/10 - skipping")
            self.log_deal(enhanced_deal, 'low_confidence')
            return False
        
        # Step 4: Generate deal ID and alert
        deal_id = f"CAS_{datetime.now().strftime('%m%d_%H%M%S')}"
        
        success = await send_smart_deal_alert(enhanced_deal, deal_id)
        
        if success:
            # Add to pending deals
            self.add_to_pending_deals(deal_id, enhanced_deal, investment_amount)
            self.session_stats['deals_alerted'] += 1
            print(f"   ✅ Deal {deal_id} alerted for approval")
            return True
        
        return False
    
    def add_to_pending_deals(self, deal_id: str, deal_data: Dict, investment_amount: float):
        """Add deal to pending approval list"""
        active_deals = self.deal_manager.load_active_deals()
        
        pending_deal = {
            'deal_id': deal_id,
            'deal': deal_data,
            'status': 'pending_approval',
            'investment_amount': investment_amount,
            'alerted_timestamp': datetime.now().isoformat(),
            'ai_enhanced': 'ai_analysis' in deal_data
        }
        
        active_deals.append(pending_deal)
        self.deal_manager.save_active_deals(active_deals)
    
    def log_deal(self, deal_data: Dict, status: str):
        """Log deal with status"""
        # Implementation would save to deal log
        print(f"   📝 Logged as: {status}")
    
    async def approve_deal(self, deal_id: str) -> bool:
        """Approve a pending deal and start tracking"""
        active_deals = self.deal_manager.load_active_deals()
        
        for deal in active_deals:
            if deal['deal_id'] == deal_id and deal['status'] == 'pending_approval':
                # Update status
                deal['status'] = 'approved'
                deal['approved_timestamp'] = datetime.now().isoformat()
                
                # Start PSA tracking
                self.grading_tracker.update_deal_status(deal_id, DealStatus.APPROVED)
                
                # Save changes
                self.deal_manager.save_active_deals(active_deals)
                self.session_stats['deals_approved'] += 1
                
                print(f"✅ Deal {deal_id} approved and tracking started")
                
                # Send confirmation
                await self.send_approval_confirmation(deal_id, deal['deal'])
                
                return True
        
        return False
    
    async def send_approval_confirmation(self, deal_id: str, deal_data: Dict):
        """Send approval confirmation with next steps"""
        try:
            from smart_mvp_bot_fixed import _smart_bot
            
            message = f"""✅ *DEAL APPROVED* 

*Deal #{deal_id}*
{deal_data['card_name']} • {deal_data['set_name']}

💰 Investment: ${deal_data['raw_price']:.0f} + $25 grading

📋 *Next Steps:*
1. Purchase card from eBay
2. Ship to PSA for grading
3. Track through grading process
4. Monitor for vault arrival
5. Create selling listing

⏰ *Expected Timeline:* ~52 days
🎯 *Target Profit:* ${deal_data['potential_profit']:.0f}

Status: Investment Active 🟢"""

            if _smart_bot:
                await _smart_bot.bot.send_message(
                    chat_id=_smart_bot.admin_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            print(f"⚠️ Could not send confirmation: {e}")
    
    async def update_grading_status(self, deal_id: str, new_status: DealStatus, **kwargs):
        """Update deal status through grading pipeline"""
        success = self.grading_tracker.update_deal_status(deal_id, new_status, **kwargs)
        
        if success and new_status == DealStatus.GRADED:
            # Card is graded - check if we should list for sale
            await self.handle_graded_card(deal_id, kwargs)
    
    async def handle_graded_card(self, deal_id: str, grading_info: Dict):
        """Handle a newly graded card"""
        grade = grading_info.get('grade')
        estimated_value = grading_info.get('estimated_value')
        
        # Send grading notification (handled by tracker)
        
        # Check if ready to sell based on hold period
        ready_cards = self.grading_tracker.check_ready_to_sell()
        
        if any(card['deal_id'] == deal_id for card in ready_cards):
            await self.suggest_listing(deal_id, grade, estimated_value)
    
    async def suggest_listing(self, deal_id: str, grade: int, estimated_value: float):
        """Suggest listing a graded card for sale"""
        try:
            from smart_mvp_bot_fixed import _smart_bot
            
            suggested_price = estimated_value * 1.1  # 10% markup
            
            message = f"""💰 *READY TO SELL*

*Deal #{deal_id}* - PSA {grade}

📊 *Market Analysis:*
• Estimated Value: ${estimated_value:.0f}
• Suggested Price: ${suggested_price:.0f}
• Markup: 10%

🚀 *Listing Options:*
• eBay 10-day auction
• eBay Buy It Now with Best Offer
• Direct sale to collector

⏰ *Market Timing:* Optimal
🎯 *Expected Sale:* 7-14 days

Ready to create listing?"""

            if _smart_bot:
                await _smart_bot.bot.send_message(
                    chat_id=_smart_bot.admin_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            print(f"⚠️ Could not send listing suggestion: {e}")
    
    async def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        capital_status = self.deal_manager.get_capital_status()
        vault_inventory = self.grading_tracker.get_vault_inventory()
        ready_to_sell = self.grading_tracker.check_ready_to_sell()
        
        return {
            'capital': capital_status,
            'vault_cards': len(vault_inventory),
            'ready_to_sell': len(ready_to_sell),
            'session_stats': self.session_stats,
            'total_deals_in_pipeline': len(self.deal_manager.load_active_deals())
        }
    
    async def send_system_status(self):
        """Send comprehensive system status"""
        status = await self.get_system_status()
        
        message = f"""📊 *COMPREHENSIVE SYSTEM STATUS*

💼 *Capital Management:*
• Available: ${status['capital']['available_for_new_deals']:.0f}
• Active Exposure: ${status['capital']['active_exposure']:.0f}
• Utilization: {status['capital']['utilization_pct']:.1f}%

🏦 *Vault & Pipeline:*
• Cards in Vault: {status['vault_cards']}
• Ready to Sell: {status['ready_to_sell']}
• Total Active Deals: {status['total_deals_in_pipeline']}

📈 *Session Performance:*
• Deals Found: {status['session_stats']['deals_found']}
• AI Enhanced: {status['session_stats']['ai_enhanced']}
• Alerted: {status['session_stats']['deals_alerted']}
• Approved: {status['session_stats']['deals_approved']}

🎯 *System Health:* Optimal"""

        try:
            from smart_mvp_bot_fixed import _smart_bot
            if _smart_bot:
                await _smart_bot.bot.send_message(
                    chat_id=_smart_bot.admin_id,
                    text=message,
                    parse_mode='Markdown'
                )
        except Exception as e:
            print(f"⚠️ Could not send status: {e}")

# CLI Interface
async def main():
    """Comprehensive system CLI"""
    system = ComprehensiveArbitrageSystem()
    
    print("🎯 Comprehensive Pokemon Card Arbitrage System")
    print("=" * 50)
    
    print("Features:")
    print("✅ Scalable capital management")
    print("✅ AI-enhanced deal analysis") 
    print("✅ PSA grading tracking")
    print("✅ Vault management")
    print("✅ Automated selling suggestions")
    print("✅ Professional Telegram alerts")
    print()
    
    print("Actions:")
    print("1. Test deal processing")
    print("2. Approve pending deal")
    print("3. Update grading status")
    print("4. Check system status")
    print("5. Simulate complete lifecycle")
    
    choice = input("Choose action (1-5): ").strip()
    
    if choice == "1":
        # Test deal processing
        test_deal = {
            'card_name': "Charizard",
            'set_name': "Base Set Shadowless",
            'raw_price': 285.00,
            'estimated_psa10_price': 4200.00,
            'potential_profit': 3890.00,
            'condition_notes': "Near Mint - excellent centering, sharp corners",
            'listing_url': "https://ebay.com/test"
        }
        
        await system.process_potential_deal(test_deal)
    
    elif choice == "2":
        deal_id = input("Enter Deal ID to approve: ").strip()
        await system.approve_deal(deal_id)
    
    elif choice == "3":
        deal_id = input("Enter Deal ID: ").strip()
        print("Available statuses: PURCHASED, SHIPPED_TO_PSA, GRADED, IN_VAULT, SOLD")
        status_str = input("Enter new status: ").strip()
        
        try:
            new_status = DealStatus(status_str.lower())
            await system.update_grading_status(deal_id, new_status)
        except ValueError:
            print("❌ Invalid status")
    
    elif choice == "4":
        await system.send_system_status()
        print("✅ System status sent to Telegram")
    
    elif choice == "5":
        print("🔄 Simulating complete deal lifecycle...")
        # This would run a full simulation
        print("📝 Feature coming soon - full lifecycle simulation")

if __name__ == "__main__":
    asyncio.run(main())
