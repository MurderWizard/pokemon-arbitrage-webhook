"""
Fee calculator for accurate profit calculations
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict

@dataclass
class TransactionFees:
    """Fee structure for different payment methods"""
    CARD_TRANSACTION_RATE = Decimal('0.0235')  # 2.35%
    CARD_FIXED_FEE = Decimal('0.30')          # $0.30
    
    PAYPAL_TRANSACTION_RATE = Decimal('0.0289')  # 2.89%
    PAYPAL_FIXED_FEE = Decimal('0.49')          # $0.49
    PAYPAL_CROSS_BORDER = Decimal('0.015')       # 1.5% additional
    
    @staticmethod
    def calculate_card_fees(amount: float) -> Dict[str, float]:
        """Calculate fees for direct card payment"""
        amount_dec = Decimal(str(amount))
        fee = (amount_dec * TransactionFees.CARD_TRANSACTION_RATE) + TransactionFees.CARD_FIXED_FEE
        
        return {
            'base_amount': float(amount_dec),
            'fees': float(fee),
            'total': float(amount_dec + fee)
        }
    
    @staticmethod
    def calculate_paypal_fees(amount: float, international: bool = False) -> Dict[str, float]:
        """Calculate PayPal fees"""
        amount_dec = Decimal(str(amount))
        base_fee = (amount_dec * TransactionFees.PAYPAL_TRANSACTION_RATE) + TransactionFees.PAYPAL_FIXED_FEE
        
        if international:
            cross_border_fee = amount_dec * TransactionFees.PAYPAL_CROSS_BORDER
            total_fee = base_fee + cross_border_fee
        else:
            total_fee = base_fee
            
        return {
            'base_amount': float(amount_dec),
            'fees': float(total_fee),
            'total': float(amount_dec + total_fee)
        }
    
    @staticmethod
    def compare_payment_methods(amount: float) -> Dict[str, Dict[str, float]]:
        """Compare costs between payment methods"""
        card = TransactionFees.calculate_card_fees(amount)
        paypal_domestic = TransactionFees.calculate_paypal_fees(amount)
        paypal_international = TransactionFees.calculate_paypal_fees(amount, international=True)
        
        return {
            'card': card,
            'paypal_domestic': paypal_domestic,
            'paypal_international': paypal_international
        }
