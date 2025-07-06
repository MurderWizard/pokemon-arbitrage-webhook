#!/usr/bin/env python3
"""
Pokemon Card Arbitrage Bot - Database Management Script

This script helps manage the database for the Pokemon Card Arbitrage Bot.
"""

import os
import sys
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path so we can import our models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.models.database import Base, Card, Deal, InventoryItem, Sale, Transaction, Settings as SettingsModel
from app.database import engine, SessionLocal

def create_tables():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

def drop_tables():
    """Drop all database tables"""
    try:
        print("Dropping database tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ Database tables dropped successfully!")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")

def reset_database():
    """Reset the database (drop and recreate tables)"""
    drop_tables()
    create_tables()

def seed_data():
    """Seed the database with sample data"""
    try:
        print("Seeding database with sample data...")
        db = SessionLocal()
        
        # Create sample cards
        sample_cards = [
            Card(
                name="Charizard",
                set_name="Base Set",
                number="4/102",
                rarity="Holo Rare",
                condition="NM",
                card_type="raw",
                tcg_product_id="1234"
            ),
            Card(
                name="Pikachu",
                set_name="Base Set",
                number="25/102",
                rarity="Common",
                condition="NM",
                card_type="raw",
                tcg_product_id="1235"
            ),
            Card(
                name="Blastoise",
                set_name="Base Set",
                number="2/102",
                rarity="Holo Rare",
                condition="NM",
                card_type="raw",
                tcg_product_id="1236"
            )
        ]
        
        for card in sample_cards:
            db.add(card)
        
        db.commit()
        
        # Create sample deals
        sample_deals = [
            Deal(
                card_name="Charizard",
                set_name="Base Set",
                condition="NM",
                listing_price=150.00,
                market_price=200.00,
                profit_margin=0.25,
                platform="ebay",
                listing_url="https://example.com/charizard",
                status="found"
            ),
            Deal(
                card_name="Pikachu",
                set_name="Base Set",
                condition="NM",
                listing_price=15.00,
                market_price=25.00,
                profit_margin=0.40,
                platform="ebay",
                listing_url="https://example.com/pikachu",
                status="found"
            )
        ]
        
        for deal in sample_deals:
            db.add(deal)
        
        db.commit()
        
        # Create sample settings
        sample_settings = [
            SettingsModel(
                key="auto_buy_enabled",
                value="false",
                description="Enable automatic purchasing of deals"
            ),
            SettingsModel(
                key="last_deal_check",
                value="2025-01-01 00:00:00",
                description="Timestamp of last deal check"
            )
        ]
        
        for setting in sample_settings:
            db.add(setting)
        
        db.commit()
        db.close()
        
        print("✅ Sample data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")

def show_stats():
    """Show database statistics"""
    try:
        db = SessionLocal()
        
        cards_count = db.query(Card).count()
        deals_count = db.query(Deal).count()
        inventory_count = db.query(InventoryItem).count()
        sales_count = db.query(Sale).count()
        transactions_count = db.query(Transaction).count()
        
        print("📊 Database Statistics:")
        print(f"   Cards: {cards_count}")
        print(f"   Deals: {deals_count}")
        print(f"   Inventory Items: {inventory_count}")
        print(f"   Sales: {sales_count}")
        print(f"   Transactions: {transactions_count}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")

def main():
    parser = argparse.ArgumentParser(description="Database management for Pokemon Card Arbitrage Bot")
    parser.add_argument("command", choices=["create", "drop", "reset", "seed", "stats"], 
                       help="Database command to run")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_tables()
    elif args.command == "drop":
        drop_tables()
    elif args.command == "reset":
        reset_database()
    elif args.command == "seed":
        seed_data()
    elif args.command == "stats":
        show_stats()

if __name__ == "__main__":
    main()
