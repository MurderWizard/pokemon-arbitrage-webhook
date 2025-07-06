#!/usr/bin/env python3
"""
Test Population-Adjusted Pricing
This script demonstrates how population data affects card prices
"""
from pokemon_price_system import PokemonPriceSystem
from population_tracker import PopulationTracker

def test_population_pricing():
    """Test population-based price adjustments"""
    price_system = PokemonPriceSystem()
    pop_tracker = PopulationTracker()
    
    # Test cards with different population scenarios
    test_cards = [
        {
            "name": "Charizard VMAX",
            "set": "Champions Path",
            "psa_data": {
                "10": 250,  # Common in PSA 10
                "9": 150,
                "8": 50,
                "7": 25,
                "total": 475
            }
        },
        {
            "name": "Lugia V",
            "set": "Silver Tempest",
            "psa_data": {
                "10": 5,    # Very rare in PSA 10
                "9": 15,
                "8": 10,
                "7": 5,
                "total": 35
            }
        },
        {
            "name": "Pikachu VMAX",
            "set": "Vivid Voltage",
            "psa_data": {
                "10": 1500,  # Very common
                "9": 1000,
                "8": 500,
                "7": 250,
                "total": 3250
            }
        }
    ]
    
    print("🔍 Population-Based Price Analysis")
    print("=" * 60)
    
    for card in test_cards:
        # Update population data
        pop_tracker.update_population(
            card["name"], 
            card["set"], 
            "PSA", 
            card["psa_data"]
        )
        
        # Get raw price first
        base_price = price_system.get_card_price(card["name"], card["set"])
        if not base_price or not base_price.market_price:
            print(f"\n❌ No base price found for {card['name']} ({card['set']})")
            continue
            
        # Get population-adjusted price
        adj_price, confidence, pop_info = price_system.get_population_adjusted_price(
            card["name"],
            card["set"]
        )
        
        print(f"\n📊 {card['name']} ({card['set']})")
        print("-" * 60)
        print(f"Base Price: ${base_price.market_price:.2f}")
        print(f"Population Adjusted: ${adj_price:.2f}")
        print(f"Population Multiplier: {pop_info['population_multiplier']:.2f}x")
        print(f"Total Graded: {pop_info['total_graded']}")
        print(f"Gem Mint Pop: {pop_info['gem_mint_population']}")
        print(f"Confidence: {confidence:.1%}")
        
        # Print population summary
        print("\nDetailed Population Report:")
        print(pop_tracker.get_population_summary(card["name"], card["set"]))

if __name__ == "__main__":
    test_population_pricing()
