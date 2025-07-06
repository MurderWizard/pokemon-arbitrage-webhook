"""
Manual approval alert formatter for Telegram
"""
from typing import Dict
from datetime import datetime

def format_deal_alert(deal: Dict) -> str:
    """
    Format a deal alert for Telegram with approval buttons
    """
    profit_roi = (deal['potential_profit'] / deal['raw_price']) * 100
    
    alert = (
        "🎯 *Potential Deal Found!*\n\n"
        f"*Card:* {deal['card_name']}\n"
        f"*Set:* {deal['set_name']}\n"
        f"*Price:* ${deal['raw_price']:.2f}\n"
        f"*Condition:* {deal.get('condition_notes', 'Not specified')}\n\n"
        
        "💰 *Profit Analysis*\n"
        f"Est. PSA 10: ${deal['estimated_psa10_price']:.2f}\n"
        f"Potential Profit: ${deal['potential_profit']:.2f}\n"
        f"ROI: {profit_roi:.1f}%\n\n"
        
        "📊 *Market Info*\n"
        f"Recent Sales: {deal.get('recent_sales_count', 'N/A')}\n"
        f"Market Trend: {deal.get('price_trend', 'Stable')}\n\n"
        
        "🔍 *Verification Needed*\n"
        "1. Check card condition in listing\n"
        "2. Verify seller rating/history\n"
        "3. Confirm grading potential\n\n"
        
        f"View Listing: {deal['listing_url']}\n\n"
        
        "Reply with:\n"
        "👍 /approve to buy this card\n"
        "👎 /pass to skip this deal\n"
        "⏸ /pause to pause alerts"
    )
    
    return alert

def format_approval_confirmation(deal: Dict) -> str:
    """
    Format approval confirmation message
    """
    return (
        "✅ *Purchase Approved!*\n\n"
        f"Card: {deal['card_name']}\n"
        f"Price: ${deal['raw_price']:.2f}\n"
        "Processing purchase...\n\n"
        "_I'll update you when the transaction is complete._"
    )

def format_skip_confirmation(deal: Dict) -> str:
    """
    Format skip confirmation message
    """
    return (
        "⏭ *Deal Skipped*\n\n"
        f"_{deal['card_name']} has been logged but won't be purchased._\n"
        "I'll keep looking for more deals!"
    )
