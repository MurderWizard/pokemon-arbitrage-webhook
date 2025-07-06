#!/usr/bin/env python3
"""
Pokemon Card List Downloader
Download comprehensive card lists from various online sources

Sources:
1. Pokemon TCG API (free, comprehensive)
2. Community databases (GitHub repos)
3. Scrape card databases (respectfully)
4. Official set lists
"""

import requests
import json
import csv
import os
import time
from typing import List, Dict
from datetime import datetime

class CardListDownloader:
    """Download card lists from multiple sources"""
    
    def __init__(self):
        self.download_dir = "card_lists"
        os.makedirs(self.download_dir, exist_ok=True)
        self.downloaded_files = []
    
    def download_pokemon_tcg_api_cards(self):
        """Download cards from Pokemon TCG API (free, no key needed)"""
        print("🃏 Downloading from Pokemon TCG API...")
        
        base_url = "https://api.pokemontcg.io/v2/cards"
        all_cards = []
        page = 1
        page_size = 250
        
        while True:
            try:
                print(f"   📄 Fetching page {page}...")
                params = {
                    'page': page,
                    'pageSize': page_size
                }
                
                response = requests.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                cards = data.get('data', [])
                
                if not cards:
                    break
                
                for card in cards:
                    card_info = {
                        'name': card.get('name', ''),
                        'set': card.get('set', {}).get('name', ''),
                        'set_id': card.get('set', {}).get('id', ''),
                        'rarity': card.get('rarity', ''),
                        'number': card.get('number', ''),
                        'artist': card.get('artist', ''),
                        'types': card.get('types', []),
                        'subtypes': card.get('subtypes', []),
                        'hp': card.get('hp', ''),
                        'series': card.get('set', {}).get('series', ''),
                        'tcg_player_url': card.get('tcgplayer', {}).get('url', '') if card.get('tcgplayer') else '',
                        'images': card.get('images', {}),
                        'market_price': self._extract_market_price(card)
                    }
                    all_cards.append(card_info)
                
                print(f"   ✅ Got {len(cards)} cards (total: {len(all_cards)})")
                page += 1
                
                # Be respectful - small delay
                time.sleep(0.5)
                
                # Safety limit
                if len(all_cards) >= 15000:
                    break
                    
            except Exception as e:
                print(f"❌ Error on page {page}: {e}")
                break
        
        # Save to JSON
        filename = f"{self.download_dir}/pokemon_tcg_api_cards.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_cards, f, indent=2, ensure_ascii=False)
        
        self.downloaded_files.append(filename)
        print(f"💾 Saved {len(all_cards)} cards to {filename}")
        
        # Also save as CSV for easy import
        csv_filename = f"{self.download_dir}/pokemon_tcg_api_cards.csv"
        self._save_as_csv(all_cards, csv_filename)
        self.downloaded_files.append(csv_filename)
        
        return all_cards
    
    def _extract_market_price(self, card: dict) -> float:
        """Extract market price from card data"""
        try:
            tcgplayer = card.get('tcgplayer', {})
            if tcgplayer and 'prices' in tcgplayer:
                prices = tcgplayer['prices']
                
                # Try different price categories
                for category in ['holofoil', 'reverseHolofoil', 'normal', '1stEditionHolofoil']:
                    if category in prices and 'market' in prices[category]:
                        price = prices[category]['market']
                        if price and price > 0:
                            return float(price)
        except:
            pass
        return 0.0
    
    def download_github_card_databases(self):
        """Download card databases from GitHub repos"""
        print("📁 Downloading from GitHub repositories...")
        
        # Known GitHub repos with Pokemon card data
        repos = [
            {
                'url': 'https://raw.githubusercontent.com/PokemonTCG/pokemon-tcg-data/master/cards/en.json',
                'filename': 'github_pokemon_tcg_data.json'
            },
            # Add more repos as you find them
        ]
        
        for repo in repos:
            try:
                print(f"   📥 Downloading: {repo['url']}")
                response = requests.get(repo['url'], timeout=30)
                response.raise_for_status()
                
                filename = f"{self.download_dir}/{repo['filename']}"
                
                if repo['url'].endswith('.json'):
                    data = response.json()
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                
                self.downloaded_files.append(filename)
                print(f"   ✅ Saved to {filename}")
                
            except Exception as e:
                print(f"   ❌ Failed to download {repo['url']}: {e}")
    
    def create_comprehensive_set_list(self):
        """Create a comprehensive list of all Pokemon sets"""
        print("📚 Creating comprehensive set list...")
        
        sets = [
            # Base Era (1998-2003)
            {'name': 'Base Set', 'year': 1998, 'era': 'Classic', 'cards': 102},
            {'name': 'Jungle', 'year': 1999, 'era': 'Classic', 'cards': 64},
            {'name': 'Fossil', 'year': 1999, 'era': 'Classic', 'cards': 62},
            {'name': 'Base Set 2', 'year': 2000, 'era': 'Classic', 'cards': 130},
            {'name': 'Team Rocket', 'year': 2000, 'era': 'Classic', 'cards': 82},
            {'name': 'Gym Heroes', 'year': 2000, 'era': 'Classic', 'cards': 132},
            {'name': 'Gym Challenge', 'year': 2000, 'era': 'Classic', 'cards': 132},
            
            # Neo Era (2000-2001)
            {'name': 'Neo Genesis', 'year': 2000, 'era': 'Neo', 'cards': 111},
            {'name': 'Neo Discovery', 'year': 2001, 'era': 'Neo', 'cards': 75},
            {'name': 'Neo Revelation', 'year': 2001, 'era': 'Neo', 'cards': 66},
            {'name': 'Neo Destiny', 'year': 2001, 'era': 'Neo', 'cards': 113},
            
            # e-Card Era (2002-2003)
            {'name': 'Expedition Base Set', 'year': 2002, 'era': 'e-Card', 'cards': 165},
            {'name': 'Aquapolis', 'year': 2003, 'era': 'e-Card', 'cards': 186},
            {'name': 'Skyridge', 'year': 2003, 'era': 'e-Card', 'cards': 182},
            
            # EX Era (2003-2007)
            {'name': 'Ruby & Sapphire', 'year': 2003, 'era': 'EX', 'cards': 109},
            {'name': 'Sandstorm', 'year': 2003, 'era': 'EX', 'cards': 100},
            {'name': 'Dragon', 'year': 2003, 'era': 'EX', 'cards': 97},
            {'name': 'Team Magma vs Team Aqua', 'year': 2004, 'era': 'EX', 'cards': 97},
            {'name': 'Hidden Legends', 'year': 2004, 'era': 'EX', 'cards': 102},
            {'name': 'FireRed & LeafGreen', 'year': 2004, 'era': 'EX', 'cards': 116},
            {'name': 'Team Rocket Returns', 'year': 2004, 'era': 'EX', 'cards': 111},
            {'name': 'Deoxys', 'year': 2005, 'era': 'EX', 'cards': 108},
            {'name': 'Emerald', 'year': 2005, 'era': 'EX', 'cards': 107},
            {'name': 'Unseen Forces', 'year': 2005, 'era': 'EX', 'cards': 145},
            {'name': 'Delta Species', 'year': 2005, 'era': 'EX', 'cards': 113},
            {'name': 'Legend Maker', 'year': 2006, 'era': 'EX', 'cards': 92},
            {'name': 'Holon Phantoms', 'year': 2006, 'era': 'EX', 'cards': 110},
            {'name': 'Crystal Guardians', 'year': 2006, 'era': 'EX', 'cards': 100},
            {'name': 'Dragon Frontiers', 'year': 2006, 'era': 'EX', 'cards': 101},
            {'name': 'Power Keepers', 'year': 2007, 'era': 'EX', 'cards': 108},
            
            # Diamond & Pearl Era (2007-2009)
            {'name': 'Diamond & Pearl', 'year': 2007, 'era': 'Diamond & Pearl', 'cards': 130},
            {'name': 'Mysterious Treasures', 'year': 2007, 'era': 'Diamond & Pearl', 'cards': 123},
            {'name': 'Secret Wonders', 'year': 2007, 'era': 'Diamond & Pearl', 'cards': 132},
            {'name': 'Great Encounters', 'year': 2008, 'era': 'Diamond & Pearl', 'cards': 106},
            {'name': 'Majestic Dawn', 'year': 2008, 'era': 'Diamond & Pearl', 'cards': 100},
            {'name': 'Legends Awakened', 'year': 2008, 'era': 'Diamond & Pearl', 'cards': 146},
            {'name': 'Stormfront', 'year': 2008, 'era': 'Diamond & Pearl', 'cards': 106},
            
            # Platinum Era (2009-2010)
            {'name': 'Platinum', 'year': 2009, 'era': 'Platinum', 'cards': 133},
            {'name': 'Rising Rivals', 'year': 2009, 'era': 'Platinum', 'cards': 120},
            {'name': 'Supreme Victors', 'year': 2009, 'era': 'Platinum', 'cards': 153},
            {'name': 'Arceus', 'year': 2009, 'era': 'Platinum', 'cards': 111},
            
            # HeartGold & SoulSilver Era (2010-2011)
            {'name': 'HeartGold & SoulSilver', 'year': 2010, 'era': 'HGSS', 'cards': 124},
            {'name': 'Unleashed', 'year': 2010, 'era': 'HGSS', 'cards': 96},
            {'name': 'Undaunted', 'year': 2010, 'era': 'HGSS', 'cards': 91},
            {'name': 'Triumphant', 'year': 2010, 'era': 'HGSS', 'cards': 103},
            
            # Black & White Era (2011-2013)
            {'name': 'Black & White', 'year': 2011, 'era': 'Black & White', 'cards': 114},
            {'name': 'Emerging Powers', 'year': 2011, 'era': 'Black & White', 'cards': 98},
            {'name': 'Noble Victories', 'year': 2011, 'era': 'Black & White', 'cards': 102},
            {'name': 'Next Destinies', 'year': 2012, 'era': 'Black & White', 'cards': 103},
            {'name': 'Dark Explorers', 'year': 2012, 'era': 'Black & White', 'cards': 111},
            {'name': 'Dragons Exalted', 'year': 2012, 'era': 'Black & White', 'cards': 128},
            {'name': 'Boundaries Crossed', 'year': 2012, 'era': 'Black & White', 'cards': 153},
            {'name': 'Plasma Storm', 'year': 2013, 'era': 'Black & White', 'cards': 138},
            {'name': 'Plasma Freeze', 'year': 2013, 'era': 'Black & White', 'cards': 122},
            {'name': 'Plasma Blast', 'year': 2013, 'era': 'Black & White', 'cards': 105},
            {'name': 'Legendary Treasures', 'year': 2013, 'era': 'Black & White', 'cards': 140},
            
            # XY Era (2014-2016)
            {'name': 'XY', 'year': 2014, 'era': 'XY', 'cards': 146},
            {'name': 'Flashfire', 'year': 2014, 'era': 'XY', 'cards': 109},
            {'name': 'Furious Fists', 'year': 2014, 'era': 'XY', 'cards': 114},
            {'name': 'Phantom Forces', 'year': 2014, 'era': 'XY', 'cards': 124},
            {'name': 'Primal Clash', 'year': 2015, 'era': 'XY', 'cards': 164},
            {'name': 'Roaring Skies', 'year': 2015, 'era': 'XY', 'cards': 110},
            {'name': 'Ancient Origins', 'year': 2015, 'era': 'XY', 'cards': 100},
            {'name': 'BREAKthrough', 'year': 2015, 'era': 'XY', 'cards': 164},
            {'name': 'BREAKpoint', 'year': 2016, 'era': 'XY', 'cards': 126},
            {'name': 'Fates Collide', 'year': 2016, 'era': 'XY', 'cards': 129},
            {'name': 'Steam Siege', 'year': 2016, 'era': 'XY', 'cards': 116},
            {'name': 'Evolutions', 'year': 2016, 'era': 'XY', 'cards': 113},
            
            # Sun & Moon Era (2017-2019)
            {'name': 'Sun & Moon', 'year': 2017, 'era': 'Sun & Moon', 'cards': 173},
            {'name': 'Guardians Rising', 'year': 2017, 'era': 'Sun & Moon', 'cards': 180},
            {'name': 'Burning Shadows', 'year': 2017, 'era': 'Sun & Moon', 'cards': 177},
            {'name': 'Shining Legends', 'year': 2017, 'era': 'Sun & Moon', 'cards': 81},
            {'name': 'Crimson Invasion', 'year': 2017, 'era': 'Sun & Moon', 'cards': 124},
            {'name': 'Ultra Prism', 'year': 2018, 'era': 'Sun & Moon', 'cards': 178},
            {'name': 'Forbidden Light', 'year': 2018, 'era': 'Sun & Moon', 'cards': 150},
            {'name': 'Celestial Storm', 'year': 2018, 'era': 'Sun & Moon', 'cards': 187},
            {'name': 'Dragon Majesty', 'year': 2018, 'era': 'Sun & Moon', 'cards': 80},
            {'name': 'Lost Thunder', 'year': 2018, 'era': 'Sun & Moon', 'cards': 236},
            {'name': 'Team Up', 'year': 2019, 'era': 'Sun & Moon', 'cards': 198},
            {'name': 'Detective Pikachu', 'year': 2019, 'era': 'Sun & Moon', 'cards': 26},
            {'name': 'Unbroken Bonds', 'year': 2019, 'era': 'Sun & Moon', 'cards': 234},
            {'name': 'Unified Minds', 'year': 2019, 'era': 'Sun & Moon', 'cards': 258},
            {'name': 'Hidden Fates', 'year': 2019, 'era': 'Sun & Moon', 'cards': 163},
            {'name': 'Cosmic Eclipse', 'year': 2019, 'era': 'Sun & Moon', 'cards': 272},
            
            # Sword & Shield Era (2020-2022)
            {'name': 'Sword & Shield', 'year': 2020, 'era': 'Sword & Shield', 'cards': 216},
            {'name': 'Rebel Clash', 'year': 2020, 'era': 'Sword & Shield', 'cards': 209},
            {'name': 'Darkness Ablaze', 'year': 2020, 'era': 'Sword & Shield', 'cards': 201},
            {'name': 'Champions Path', 'year': 2020, 'era': 'Sword & Shield', 'cards': 80},
            {'name': 'Vivid Voltage', 'year': 2020, 'era': 'Sword & Shield', 'cards': 203},
            {'name': 'Shining Fates', 'year': 2021, 'era': 'Sword & Shield', 'cards': 73},
            {'name': 'Battle Styles', 'year': 2021, 'era': 'Sword & Shield', 'cards': 183},
            {'name': 'Chilling Reign', 'year': 2021, 'era': 'Sword & Shield', 'cards': 233},
            {'name': 'Evolving Skies', 'year': 2021, 'era': 'Sword & Shield', 'cards': 237},
            {'name': 'Celebrations', 'year': 2021, 'era': 'Sword & Shield', 'cards': 50},
            {'name': 'Fusion Strike', 'year': 2021, 'era': 'Sword & Shield', 'cards': 284},
            {'name': 'Brilliant Stars', 'year': 2022, 'era': 'Sword & Shield', 'cards': 216},
            {'name': 'Astral Radiance', 'year': 2022, 'era': 'Sword & Shield', 'cards': 236},
            {'name': 'Pokémon GO', 'year': 2022, 'era': 'Sword & Shield', 'cards': 88},
            {'name': 'Lost Origin', 'year': 2022, 'era': 'Sword & Shield', 'cards': 247},
            {'name': 'Silver Tempest', 'year': 2022, 'era': 'Sword & Shield', 'cards': 245},
            {'name': 'Crown Zenith', 'year': 2023, 'era': 'Sword & Shield', 'cards': 159},
            
            # Scarlet & Violet Era (2023+)
            {'name': 'Scarlet & Violet', 'year': 2023, 'era': 'Scarlet & Violet', 'cards': 198},
            {'name': 'Paldea Evolved', 'year': 2023, 'era': 'Scarlet & Violet', 'cards': 279},
            {'name': 'Obsidian Flames', 'year': 2023, 'era': 'Scarlet & Violet', 'cards': 230},
            {'name': 'Paradox Rift', 'year': 2023, 'era': 'Scarlet & Violet', 'cards': 266},
            {'name': 'Paldean Fates', 'year': 2024, 'era': 'Scarlet & Violet', 'cards': 91},
            {'name': 'Temporal Forces', 'year': 2024, 'era': 'Scarlet & Violet', 'cards': 218}
        ]
        
        filename = f"{self.download_dir}/comprehensive_sets.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sets, f, indent=2, ensure_ascii=False)
        
        self.downloaded_files.append(filename)
        print(f"💾 Saved {len(sets)} sets to {filename}")
        
        # Also save as CSV
        csv_filename = f"{self.download_dir}/comprehensive_sets.csv"
        self._save_sets_as_csv(sets, csv_filename)
        self.downloaded_files.append(csv_filename)
        
        return sets
    
    def _save_as_csv(self, cards: List[Dict], filename: str):
        """Save cards as CSV file"""
        if not cards:
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=cards[0].keys())
            writer.writeheader()
            writer.writerows(cards)
        
        print(f"💾 Saved CSV: {filename}")
    
    def _save_sets_as_csv(self, sets: List[Dict], filename: str):
        """Save sets as CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['name', 'year', 'era', 'cards']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sets)
        
        print(f"💾 Saved sets CSV: {filename}")
    
    def run_all_downloads(self):
        """Download from all available sources"""
        print("🚀 Starting comprehensive card list downloads...")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Download from all sources
        self.create_comprehensive_set_list()
        self.download_pokemon_tcg_api_cards()
        self.download_github_card_databases()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("=" * 60)
        print("🎉 ALL DOWNLOADS COMPLETE!")
        print(f"📁 Downloaded files:")
        for file in self.downloaded_files:
            print(f"   ✅ {file}")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print("\n🎯 Next step: Run universal_card_importer.py with these files!")

def main():
    """Run the card list downloader"""
    downloader = CardListDownloader()
    downloader.run_all_downloads()

if __name__ == "__main__":
    main()
