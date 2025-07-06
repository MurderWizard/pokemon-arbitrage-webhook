#!/usr/bin/env python3
"""
Verified Price Updater
Updates card prices with cross-referenced verification
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, List, Tuple
from price_verifier import PriceVerifier, VerifiedPrice
from pokemon_price_system import PokemonPriceDB

logger = logging.getLogger(__name__)

class VerifiedPriceUpdater:
    def __init__(self):
        self.verifier = PriceVerifier()
        self.price_db = PokemonPriceDB()
        self.update_log_file = "price_verification_log.json"
        
    def update_card_price(self, card_name: str, set_name: Optional[str] = None) -> Tuple[bool, Dict]:
        """Update a card's price with verification"""
        try:
            # Get verified price from multiple sources
            verified = self.verifier.verify_price(card_name, set_name)
            
            # Log the verification results
            log_entry = {
                "card_name": card_name,
                "set_name": set_name,
                "timestamp": datetime.now().isoformat(),
                "verified_price": verified.market_price,
                "confidence": verified.confidence,
                "sources": verified.sources,
                "outliers": verified.outliers_removed,
                "variance": verified.variance
            }
            
            self._log_verification(log_entry)
            
            # Only update if confidence is high enough
            if verified.confidence >= 0.7:  # 70% confidence threshold
                self.price_db.update_price_manually(
                    card_name=card_name,
                    set_name=set_name or "Unknown",
                    market_price=verified.market_price,
                    notes=f"Verified across {len(verified.sources)} sources"
                )
                return True, log_entry
            else:
                logger.warning(f"Low confidence price for {card_name}: {verified.confidence:.1%}")
                return False, log_entry
                
        except Exception as e:
            logger.error(f"Error updating verified price for {card_name}: {e}")
            return False, {"error": str(e)}
            
    def verify_database_prices(self, confidence_threshold: float = 0.7) -> Dict:
        """Verify all prices in the database"""
        stats = self.price_db.get_price_statistics()
        results = {
            "total_cards": stats["unique_cards"],
            "verified": 0,
            "updated": 0,
            "failed": 0,
            "low_confidence": 0,
            "details": []
        }
        
        # Get all cards from database
        cards = self.price_db.get_all_cards()
        
        for card in cards:
            try:
                success, log = self.update_card_price(card["card_name"], card["set_name"])
                
                results["verified"] += 1
                if success:
                    results["updated"] += 1
                elif log.get("error"):
                    results["failed"] += 1
                else:
                    results["low_confidence"] += 1
                    
                results["details"].append({
                    "card": f"{card['card_name']} ({card['set_name']})",
                    "result": "updated" if success else "failed",
                    "confidence": log.get("confidence", 0),
                    "price_difference": abs(
                        log.get("verified_price", 0) - card.get("market_price", 0)
                    )
                })
                
            except Exception as e:
                logger.error(f"Error verifying {card}: {e}")
                results["failed"] += 1
                
        return results
    
    def _log_verification(self, log_entry: Dict):
        """Log verification results"""
        try:
            logs = []
            if os.path.exists(self.update_log_file):
                with open(self.update_log_file, 'r') as f:
                    logs = json.load(f)
                    
            logs.append(log_entry)
            
            # Keep last 1000 verifications
            if len(logs) > 1000:
                logs = logs[-1000:]
                
            with open(self.update_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error logging verification: {e}")

def test_verified_updater():
    """Test the verified price updater"""
    updater = VerifiedPriceUpdater()
    
    # Test cards
    test_cards = [
        ("Charizard VMAX", "Champions Path"),
        ("Pikachu V", "Vivid Voltage"),
        ("Lugia V", "Silver Tempest"),
        ("Base Set Charizard", "Base Set")
    ]
    
    print("🔍 Testing Verified Price Updates")
    print("=" * 60)
    
    for card_name, set_name in test_cards:
        print(f"\nVerifying {card_name} ({set_name})")
        print("-" * 60)
        
        success, log = updater.update_card_price(card_name, set_name)
        
        if success:
            print("✅ Price verified and updated!")
            print(f"New Price: ${log['verified_price']:.2f}")
            print(f"Confidence: {log['confidence']:.1%}")
            print("\nSource Prices:")
            for source, price in log['sources'].items():
                print(f"  • {source}: ${price:.2f}")
        else:
            if "error" in log:
                print(f"❌ Error: {log['error']}")
            else:
                print("⚠️ Low confidence price - not updated")
                print(f"Confidence: {log['confidence']:.1%}")
    
    print("\n🔍 Running Database Verification")
    print("=" * 60)
    
    results = updater.verify_database_prices()
    print(f"\nVerification Results:")
    print(f"Total Cards: {results['total_cards']}")
    print(f"Verified: {results['verified']}")
    print(f"Updated: {results['updated']}")
    print(f"Failed: {results['failed']}")
    print(f"Low Confidence: {results['low_confidence']}")
    
    # Show biggest price differences
    print("\nBiggest Price Differences:")
    sorted_details = sorted(
        results['details'],
        key=lambda x: x['price_difference'],
        reverse=True
    )
    for detail in sorted_details[:5]:
        print(f"  • {detail['card']}: ${detail['price_difference']:.2f}")

if __name__ == "__main__":
    test_verified_updater()
