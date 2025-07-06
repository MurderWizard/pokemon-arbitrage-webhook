#!/usr/bin/env python3
"""
Test script to verify the Pokemon Card Arbitrage Bot setup
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        # Test core imports
        from app.core.config import settings
        from app.database import SessionLocal
        from app.models.database import Card, Deal, InventoryItem
        from app.models.schemas import CardCreate, DealCreate
        print("✅ Core modules imported successfully")
        
        # Test service imports
        from app.services.deal_finder import DealFinder
        from app.services.pricing import PricingService
        from app.services.external_apis import TCGPlayerAPI, EbayAPI
        print("✅ Service modules imported successfully")
        
        # Test API imports
        from app.api.routes import deals, inventory, pricing, analytics
        print("✅ API modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing database connection...")
    
    try:
        from app.database import engine, SessionLocal
        from sqlalchemy import text
        
        # Test connection
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).scalar()
        db.close()
        
        if result == 1:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from app.core.config import settings
        
        # Check if essential settings are loaded
        essential_settings = [
            'DB_URL',
            'STARTING_BANKROLL',
            'MAX_POSITION_PERCENT',
            'DEAL_THRESHOLD'
        ]
        
        missing_settings = []
        for setting in essential_settings:
            if not hasattr(settings, setting):
                missing_settings.append(setting)
        
        if missing_settings:
            print(f"❌ Missing settings: {', '.join(missing_settings)}")
            return False
        
        print("✅ Configuration loaded successfully")
        print(f"   Starting bankroll: ${settings.STARTING_BANKROLL}")
        print(f"   Deal threshold: {settings.DEAL_THRESHOLD}")
        print(f"   Max position: {settings.MAX_POSITION_PERCENT}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints (if running)"""
    print("\n🔌 Testing API endpoints...")
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:8001/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ API health check successful")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Bankroll: ${data.get('bankroll')}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection error: {e}")
        print("   (This is expected if services aren't running)")
        return False

def test_sample_data():
    """Test creating sample data"""
    print("\n📊 Testing sample data creation...")
    
    try:
        from app.database import SessionLocal
        from app.models.database import Card, Deal
        from datetime import datetime
        
        db = SessionLocal()
        
        # Create a sample card
        sample_card = Card(
            name="Test Charizard",
            set_name="Test Set",
            number="1/100",
            rarity="Holo Rare",
            condition="NM",
            card_type="raw",
            tcg_product_id="test_123"
        )
        
        db.add(sample_card)
        db.commit()
        db.refresh(sample_card)
        
        # Create a sample deal
        sample_deal = Deal(
            card_name="Test Charizard",
            set_name="Test Set",
            condition="NM",
            listing_price=100.00,
            market_price=150.00,
            profit_margin=0.33,
            platform="ebay",
            listing_url="https://example.com/test",
            status="found"
        )
        
        db.add(sample_deal)
        db.commit()
        
        # Clean up
        db.delete(sample_deal)
        db.delete(sample_card)
        db.commit()
        db.close()
        
        print("✅ Sample data creation successful")
        return True
        
    except Exception as e:
        print(f"❌ Sample data creation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🎴 Pokemon Card Arbitrage Bot - System Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_database_connection,
        test_sample_data,
        test_api_endpoints
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Your system is ready to go.")
        print("\n🚀 Next steps:")
        print("   1. Configure your API keys in .env")
        print("   2. Start the services with ./start.sh")
        print("   3. Access the dashboard at http://localhost:8502")
        print("   4. Send /start to your Telegram bot")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("\n🔧 Common fixes:")
        print("   - Run ./setup.sh to install dependencies")
        print("   - Check your .env file configuration")
        print("   - Start services with ./start.sh")
        print("   - Check Docker containers are running")

if __name__ == "__main__":
    main()
