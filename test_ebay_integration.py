#!/usr/bin/env python3
"""Test script for enhanced eBay integration"""

import os
from ebay_browse_api_integration import EbayBrowseAPI as EbaySDK
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ebay_integration():
    """Test the enhanced eBay SDK integration"""
    
    # Initialize SDK
    sdk = EbaySDK()
    
    # Verify eBay credentials
    app_id = os.getenv('EBAY_APP_ID')
    dev_id = os.getenv('EBAY_DEV_ID')
    cert_id = os.getenv('EBAY_CERT_ID')
    environment = os.getenv('EBAY_ENVIRONMENT', 'production')
    
    print("\n🔑 eBay Configuration:")
    print(f"App ID: {app_id}")
    print(f"Dev ID: {dev_id}")
    print(f"Cert ID: {cert_id}")
    print(f"Environment: {environment}")
    
    if not all([app_id, dev_id, cert_id]):
        print("\n❌ Error: Missing required eBay credentials")
        return False
        
    print("\n🔍 Testing High-Value Pokemon Card Search...")
    try:
        # Search for high-value raw cards
        results = sdk.search_pokemon_cards(
            keywords="charizard 1st edition",
            min_price=250,  # High-value focus
            raw_only=True,
            limit=5
        )
        
        if not results:
            print("ℹ️  No cards found matching criteria")
            return True
            
        print(f"Found {len(results)} high-value raw cards")
        for idx, card in enumerate(results, 1):
            print(f"\n📌 Card {idx}:")
            print(f"Title: {card['title']}")
            print(f"Price: ${card['price']:.2f}")
            print(f"Condition: {card['condition']}")
            print(f"Seller: {card['seller']} ({card['seller_feedback']}% positive)")
            print(f"URL: {card['url']}")
            
            try:
                # Test PSA eligibility
                is_eligible = sdk.is_psa_eligible(card['id'])
                print(f"PSA Eligible: {'✅' if is_eligible else '❌'}")
                
                if is_eligible:
                    # Test adding to cart with grading
                    cart = sdk.add_to_cart_with_grading(
                        item_id=card['id'],
                        grading_tier='BASIC',
                        auto_vault=True
                    )
                    print("\n🛒 Added to cart with grading:")
                    print(f"Order ID: {cart.get('OrderID', 'N/A')}")
                    print(f"Status: {cart.get('Status', 'N/A')}")
                    
                    if 'error' not in cart:
                        # Test grading status tracking
                        status = sdk.track_grading_status(cart['OrderID'])
                        print("\n📊 Grading Status:")
                        print(f"Stage: {status.get('Stage', 'N/A')}")
                        print(f"Est. Completion: {status.get('EstimatedCompletion', 'N/A')}")
                        print("\nRecent Updates:")
                        for update in status.get('Updates', []):
                            print(f"- {update['status']} ({update['timestamp']})")
            except Exception as e:
                print(f"⚠️  Error processing card: {e}")
                continue
                    
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        return False
        
    print("\n✅ All tests completed!")
    return True

if __name__ == "__main__":
    test_ebay_integration()
