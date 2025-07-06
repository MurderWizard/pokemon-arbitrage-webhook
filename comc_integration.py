#!/usr/bin/env python3
"""
COMC (Card Market) Integration Module
Handles COMC pricing, storage fees, and profit calculations
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class COMCStorageRules:
    """COMC Storage Fee Rules"""
    BASIC_ACCOUNT = {
        'monthly_cost': 0,
        'free_storage_threshold': 0.75,  # Items $0.75 or less store free
        'storage_fee': 0.01,  # $0.01 per card per month over threshold
        'shipping_flagged': True,  # Free storage for items flagged to ship
        'not_for_sale': True  # Free storage for items marked not for sale
    }
    
    PREMIUM_ACCOUNT = {
        'monthly_cost': 50.00,
        'free_storage_threshold': 2.50,  # Items $2.50 or less store free
        'storage_fee': 0.01,
        'shipping_flagged': True,
        'not_for_sale': True
    }

class COMCProfitCalculator:
    def __init__(self, is_premium: bool = False):
        self.is_premium = is_premium
        self.rules = COMCStorageRules.PREMIUM_ACCOUNT if is_premium else COMCStorageRules.BASIC_ACCOUNT
        
    def calculate_storage_fees(self, price: float, months: int = 1) -> float:
        """Calculate storage fees for a card"""
        if price <= self.rules['free_storage_threshold']:
            return 0.0
        return self.rules['storage_fee'] * months
        
    def calculate_profit_margin(self, 
                              buy_price: float, 
                              sell_price: float,
                              holding_months: int = 1) -> Dict:
        """
        Calculate potential profit margin including all COMC fees
        """
        # COMC fees
        storage_fee = self.calculate_storage_fees(sell_price, holding_months)
        processing_fee = 0.50  # Standard card processing fee
        cash_out_fee = sell_price * 0.10  # 10% cash out fee
        monthly_account_fee = self.rules['monthly_cost'] / 100  # Assume 100 cards/month to distribute cost
        
        # Total fees
        total_fees = storage_fee + processing_fee + cash_out_fee + monthly_account_fee
        
        # Profit calculation
        gross_profit = sell_price - buy_price
        net_profit = gross_profit - total_fees
        roi = (net_profit / buy_price) * 100 if buy_price > 0 else 0
        
        return {
            'buy_price': buy_price,
            'sell_price': sell_price,
            'storage_fee': storage_fee,
            'processing_fee': processing_fee,
            'cash_out_fee': cash_out_fee,
            'monthly_account_fee': monthly_account_fee,
            'total_fees': total_fees,
            'gross_profit': gross_profit,
            'net_profit': net_profit,
            'roi': roi,
            'holding_months': holding_months
        }
    
    def suggest_optimal_price(self, 
                            buy_price: float, 
                            target_roi: float = 30.0,
                            max_holding_months: int = 3) -> Dict:
        """
        Suggest optimal selling price to achieve target ROI
        """
        test_price = buy_price * (1 + (target_roi / 100))
        
        # Try different prices until we find one that meets target ROI
        while test_price <= buy_price * 3:  # Cap at 3x buy price
            for months in range(1, max_holding_months + 1):
                result = self.calculate_profit_margin(buy_price, test_price, months)
                if result['roi'] >= target_roi:
                    return {
                        'suggested_price': test_price,
                        'optimal_holding_months': months,
                        **result
                    }
            test_price += 0.25  # Increment by 25 cents
            
        return None  # No price found meeting target ROI

def test_comc_calculator():
    """Test COMC profit calculations"""
    print("🏪 COMC Profit Calculator Test")
    print("=" * 60)
    
    # Test both account types
    accounts = [
        ("Basic Account", False),
        ("Premium Account", True)
    ]
    
    test_cards = [
        ("Budget Card", 0.50, 2.00),
        ("Mid-Range Card", 15.00, 25.00),
        ("Chase Card", 85.00, 120.00)
    ]
    
    for account_name, is_premium in accounts:
        print(f"\n📊 Testing {account_name}")
        print("-" * 60)
        
        calc = COMCProfitCalculator(is_premium=is_premium)
        
        for card_type, buy, sell in test_cards:
            print(f"\n{card_type} (Buy: ${buy:.2f}, Sell: ${sell:.2f})")
            
            # Calculate actual profit
            result = calc.calculate_profit_margin(buy, sell)
            print(f"Storage Fee: ${result['storage_fee']:.2f}")
            print(f"Total Fees: ${result['total_fees']:.2f}")
            print(f"Net Profit: ${result['net_profit']:.2f}")
            print(f"ROI: {result['roi']:.1f}%")
            
            # Get optimal price suggestion
            optimal = calc.suggest_optimal_price(buy, target_roi=30.0)
            if optimal:
                print(f"Suggested Price: ${optimal['suggested_price']:.2f}")
                print(f"Hold Time: {optimal['optimal_holding_months']} months")
                print(f"Expected ROI: {optimal['roi']:.1f}%")

if __name__ == "__main__":
    test_comc_calculator()
