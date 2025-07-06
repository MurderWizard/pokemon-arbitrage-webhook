#!/usr/bin/env python3
"""
Pokemon Price Manager - Easy tool to manage your price database

This tool helps you:
- Update card prices manually
- Import prices from CSV/JSON
- View price statistics
- Search for card prices
- Export price data
"""

import argparse
import json
import csv
from datetime import datetime
from pokemon_price_system import price_db, get_card_market_price

class PriceManager:
    """Price management command-line tool"""
    
    def __init__(self):
        self.db = price_db
    
    def search_price(self, card_name: str, set_name: str = None):
        """Search for a card price"""
        print(f"\n🔍 Searching for: {card_name}")
        if set_name:
            print(f"   Set: {set_name}")
        
        price, confidence = get_card_market_price(card_name, set_name)
        
        if price:
            print(f"\n💰 Market Price: ${price:.2f}")
            print(f"🎯 Confidence: {confidence:.1%}")
            
            # Get full price data
            price_data = self.db.get_card_price(card_name, set_name)
            if price_data:
                print(f"📊 Price Range: ${price_data.low_price:.2f} - ${price_data.high_price:.2f}")
                print(f"📅 Last Updated: {price_data.last_updated.strftime('%Y-%m-%d %H:%M')}")
                print(f"📈 Trend: {price_data.price_trend}")
                print(f"🏪 Source: {price_data.source}")
        else:
            print("\n❌ No price data found")
            print("💡 You can add it manually with: --add")
    
    def add_price(self, card_name: str, set_name: str, price: float, condition: str = "Near Mint"):
        """Add/update a card price manually"""
        self.db.update_price_manually(card_name, set_name, price, condition)
        print(f"\n✅ Updated price for {card_name} ({set_name}): ${price:.2f}")
    
    def import_prices(self, file_path: str):
        """Import prices from file"""
        print(f"\n📥 Importing prices from {file_path}...")
        
        try:
            self.db.bulk_update_prices(file_path)
            print("✅ Prices imported successfully!")
        except Exception as e:
            print(f"❌ Error importing prices: {e}")
    
    def export_prices(self, file_path: str, format: str = "json"):
        """Export prices to file"""
        print(f"\n📤 Exporting prices to {file_path}...")
        
        try:
            # Get all prices from database
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM card_prices ORDER BY card_name, set_name')
            rows = cursor.fetchall()
            conn.close()
            
            if format.lower() == 'json':
                self._export_json(rows, file_path)
            elif format.lower() == 'csv':
                self._export_csv(rows, file_path)
            else:
                print("❌ Unsupported format. Use 'json' or 'csv'")
                return
            
            print(f"✅ Exported {len(rows)} price records")
            
        except Exception as e:
            print(f"❌ Error exporting prices: {e}")
    
    def _export_json(self, rows, file_path: str):
        """Export to JSON format"""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_records": len(rows),
            "cards": []
        }
        
        for row in rows:
            export_data["cards"].append({
                "name": row[1],
                "set": row[2],
                "market_price": row[3],
                "low_price": row[4],
                "high_price": row[5],
                "last_updated": row[6],
                "source": row[7],
                "condition": row[8],
                "trend": row[9]
            })
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def _export_csv(self, rows, file_path: str):
        """Export to CSV format"""
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'card_name', 'set_name', 'market_price', 'low_price', 'high_price',
                'last_updated', 'source', 'condition', 'trend'
            ])
            
            # Data
            for row in rows[1:]:  # Skip ID column
                writer.writerow(row[1:])
    
    def show_stats(self):
        """Show price database statistics"""
        stats = self.db.get_price_statistics()
        
        print("\n📊 Price Database Statistics")
        print("=" * 30)
        print(f"Total Price Records: {stats['total_prices']}")
        print(f"Unique Cards: {stats['unique_cards']}")
        print(f"Fresh Prices (24h): {stats['fresh_prices']}")
        print(f"Freshness Ratio: {stats['freshness_ratio']:.1%}")
        
        # Top cards by value
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT card_name, set_name, market_price 
            FROM card_prices 
            ORDER BY market_price DESC 
            LIMIT 10
        ''')
        top_cards = cursor.fetchall()
        
        print(f"\n💎 Top 10 Most Valuable Cards:")
        for i, (name, set_name, price) in enumerate(top_cards, 1):
            print(f"{i:2d}. {name} ({set_name}): ${price:.2f}")
        
        conn.close()
    
    def list_cards(self, limit: int = 20, search: str = None):
        """List cards in database"""
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        if search:
            cursor.execute('''
                SELECT card_name, set_name, market_price, last_updated 
                FROM card_prices 
                WHERE LOWER(card_name) LIKE LOWER(?) 
                ORDER BY market_price DESC 
                LIMIT ?
            ''', (f'%{search}%', limit))
        else:
            cursor.execute('''
                SELECT card_name, set_name, market_price, last_updated 
                FROM card_prices 
                ORDER BY last_updated DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if search:
            print(f"\n🔍 Cards matching '{search}':")
        else:
            print(f"\n📋 Recent Cards (last {limit}):")
        
        print("-" * 80)
        print(f"{'Card Name':<30} {'Set':<20} {'Price':<10} {'Updated':<15}")
        print("-" * 80)
        
        for name, set_name, price, updated in rows:
            updated_date = datetime.fromisoformat(updated).strftime('%m/%d %H:%M')
            print(f"{name[:30]:<30} {set_name[:20]:<20} ${price:<9.2f} {updated_date:<15}")
    
    def create_sample_data(self):
        """Create sample price data for testing"""
        print("\n📝 Creating sample price data...")
        
        # Load manual prices
        try:
            with open('manual_prices.json', 'r') as f:
                data = json.load(f)
            
            count = 0
            for card in data.get('cards', []):
                self.db.update_price_manually(
                    card['name'],
                    card['set'],
                    card['market_price'],
                    card.get('condition', 'Near Mint')
                )
                count += 1
            
            print(f"✅ Created {count} sample price records")
            
        except FileNotFoundError:
            print("❌ manual_prices.json not found")
        except Exception as e:
            print(f"❌ Error creating sample data: {e}")

def main():
    parser = argparse.ArgumentParser(description='Pokemon Card Price Manager')
    parser.add_argument('--search', '-s', help='Search for a card price')
    parser.add_argument('--set', help='Specify set name for search')
    parser.add_argument('--add', '-a', nargs=4, metavar=('NAME', 'SET', 'PRICE', 'CONDITION'),
                       help='Add/update card price: name set price condition')
    parser.add_argument('--import', '-i', dest='import_file', help='Import prices from file')
    parser.add_argument('--export', '-e', nargs=2, metavar=('FILE', 'FORMAT'),
                       help='Export prices to file (json/csv)')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--list', '-l', type=int, default=20, help='List recent cards (default: 20)')
    parser.add_argument('--find', '-f', help='Find cards by name')
    parser.add_argument('--sample', action='store_true', help='Create sample data')
    
    args = parser.parse_args()
    
    manager = PriceManager()
    
    if args.search:
        manager.search_price(args.search, args.set)
    elif args.add:
        name, set_name, price, condition = args.add
        manager.add_price(name, set_name, float(price), condition)
    elif args.import_file:
        manager.import_prices(args.import_file)
    elif args.export:
        file_path, format_type = args.export
        manager.export_prices(file_path, format_type)
    elif args.stats:
        manager.show_stats()
    elif args.find:
        manager.list_cards(args.list, args.find)
    elif args.sample:
        manager.create_sample_data()
    else:
        manager.list_cards(args.list)

if __name__ == "__main__":
    main()
