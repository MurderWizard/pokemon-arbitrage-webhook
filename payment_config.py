"""
Payment Configuration for eBay Purchases
Handles payment methods and limits for automated buying
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

@dataclass
class PaymentLimits:
    """Payment limits for MVP phase"""
    SINGLE_CARD_LIMIT = float(os.getenv('MAX_PURCHASE', '300.0'))  # Start small
    DAILY_LIMIT = float(os.getenv('DAILY_LIMIT', '500.0'))        # Conservative daily limit
    MIN_BALANCE = float(os.getenv('MIN_BALANCE', '100.0'))        # Keep some reserve
    REQUIRES_APPROVAL = True  # Always require manual approval for MVP

class PaymentConfig:
    """Configure and manage payment methods"""
    
    def __init__(self):
        load_dotenv()
        self.payment_method = os.getenv('EBAY_PAYMENT_METHOD', 'CC')  # Default to card for lower fees
        self.limits = PaymentLimits()
        self.manual_mode = True  # Force manual approval for MVP
        
        # Load fee calculator
        from fee_calculator import TransactionFees
        self.fee_calculator = TransactionFees()
        
    def get_payment_method(self) -> dict:
        """Get configured payment method for eBay"""
        if self.payment_method == 'PP':
            return {
                'method': 'PAYPAL',
                'email': os.getenv('PAYPAL_EMAIL'),
                'is_verified': bool(os.getenv('PAYPAL_EMAIL')),
                'limits': self.limits,
                'requires_approval': True
            }
        else:
            return {
                'method': 'MANUAL',
                'limits': self.limits,
                'requires_approval': True
            }
        
    def verify_payment_setup(self) -> bool:
        """Verify payment method is properly configured"""
        return True  # Always true for MVP manual mode
        
    def can_make_purchase(self, amount: float) -> tuple[bool, str]:
        """Check if purchase amount is within limits"""
        if amount > self.limits.SINGLE_CARD_LIMIT:
            return False, f"Amount ${amount:.2f} exceeds current limit of ${self.limits.SINGLE_CARD_LIMIT:.2f}"
        
        return True, "Requires your approval before purchase"
            
        if not method['is_verified']:
            print("❌ Payment method not verified")
            print(f"Please verify your {method['method']} in .env")
            return False
            
        print("✅ Payment method configured:")
        print(f"Type: {method['method']}")
        if method['method'] == 'CREDIT_CARD':
            print(f"Card: ****{method['last4']}")
        else:
            print(f"PayPal: {method['email']}")
        return True
        
    def can_make_purchase(self, amount: float) -> tuple[bool, str]:
        """Check if a purchase is within limits"""
        limits = PaymentLimits()
        
        if amount > limits.SINGLE_CARD_LIMIT:
            return False, f"Amount ${amount:.2f} exceeds single card limit ${limits.SINGLE_CARD_LIMIT:.2f}"
            
        # Add additional checks here (daily/weekly totals, etc)
        return True, "Purchase within limits"
