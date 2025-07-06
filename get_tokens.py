#!/usr/bin/env python3
"""
Token Helper Script for Railway Environment Variables

This script helps you:
1. Get your Telegram bot token (with instructions)
2. Generate a secure eBay verification token
3. Show you exactly what to set in Railway
"""

import secrets
import string
import os
from datetime import datetime

def generate_secure_token(length=32):
    """Generate a cryptographically secure token"""
    alphabet = string.ascii_letters + string.digits + '_-'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_telegram_bot_token():
    """Guide user through getting Telegram bot token"""
    print("🤖 TELEGRAM BOT TOKEN SETUP")
    print("=" * 50)
    print()
    print("To get your Telegram bot token:")
    print("1. Open Telegram app")
    print("2. Search for @BotFather")
    print("3. Send one of these commands:")
    print("   • /mybots - to see existing bots")
    print("   • /newbot - to create a new bot")
    print()
    print("4. If creating new bot:")
    print("   • Choose a name (e.g., 'Pokemon Arbitrage Bot')")
    print("   • Choose a username (e.g., 'pokemon_arbitrage_bot')")
    print()
    print("5. BotFather will give you a token like:")
    print("   123456789:ABCdefGHIjklMNOpqrSTUvwxyz")
    print()
    
    # Check if user already has a token
    existing_token = input("Do you already have a Telegram bot token? (Enter it, or press Enter to skip): ").strip()
    
    if existing_token:
        if ':' in existing_token and len(existing_token) > 20:
            print(f"✅ Token looks valid: {existing_token[:10]}...{existing_token[-10:]}")
            return existing_token
        else:
            print("❌ That doesn't look like a valid Telegram bot token")
            print("   Valid tokens have format: 123456789:ABCdefGHIjklMNOpqrSTUvwxyz")
    
    return None

def generate_ebay_verification_token():
    """Generate a secure eBay verification token"""
    print("\n🔐 EBAY VERIFICATION TOKEN")
    print("=" * 50)
    print()
    
    # Generate a secure token
    secure_token = f"pokemon_webhook_{generate_secure_token(16)}"
    
    print("Generated secure eBay verification token:")
    print(f"   {secure_token}")
    print()
    print("This token will be used to verify eBay webhook requests.")
    print("Keep this secret and use it in both:")
    print("1. Railway environment variables")
    print("2. eBay Developer Portal webhook configuration")
    print()
    
    return secure_token

def show_railway_setup_instructions(tg_token, ebay_token):
    """Show Railway setup instructions"""
    print("\n🚀 RAILWAY ENVIRONMENT VARIABLES SETUP")
    print("=" * 50)
    print()
    print("Go to your Railway project dashboard and add these variables:")
    print()
    print("Variable Name: TG_TOKEN")
    print(f"Value: {tg_token if tg_token else 'YOUR_TELEGRAM_BOT_TOKEN_HERE'}")
    print()
    print("Variable Name: EBAY_VERIFICATION_TOKEN")
    print(f"Value: {ebay_token}")
    print()
    print("Steps:")
    print("1. Open Railway dashboard: https://railway.app/dashboard")
    print("2. Click on your Pokemon project")
    print("3. Click 'Variables' tab")
    print("4. Click 'New Variable' button")
    print("5. Add each variable above")
    print("6. Railway will automatically redeploy with new variables")
    print()

def save_tokens_to_file(tg_token, ebay_token):
    """Save tokens to a local file for reference"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"railway_tokens_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("# Railway Environment Variables\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
        f.write("# Add these to Railway dashboard:\n\n")
        f.write(f"TG_TOKEN={tg_token if tg_token else 'YOUR_TELEGRAM_BOT_TOKEN_HERE'}\n")
        f.write(f"EBAY_VERIFICATION_TOKEN={ebay_token}\n\n")
        f.write("# Instructions:\n")
        f.write("# 1. Go to Railway dashboard\n")
        f.write("# 2. Select your project\n")
        f.write("# 3. Click Variables tab\n")
        f.write("# 4. Add both variables above\n")
    
    print(f"💾 Tokens saved to: {filename}")
    return filename

def test_current_environment():
    """Test if tokens are already set in current environment"""
    print("\n🔍 CURRENT ENVIRONMENT CHECK")
    print("=" * 50)
    
    tg_token = os.getenv('TG_TOKEN')
    ebay_token = os.getenv('EBAY_VERIFICATION_TOKEN')
    
    if tg_token:
        print(f"✅ TG_TOKEN is set: {tg_token[:10]}...{tg_token[-10:]}")
    else:
        print("❌ TG_TOKEN is not set")
    
    if ebay_token:
        print(f"✅ EBAY_VERIFICATION_TOKEN is set: {ebay_token}")
    else:
        print("❌ EBAY_VERIFICATION_TOKEN is not set")
    
    return tg_token, ebay_token

def main():
    """Main script execution"""
    print("🎯 POKEMON ARBITRAGE WEBHOOK TOKENS")
    print("=" * 50)
    print("This script helps you set up environment variables for Railway")
    print()
    
    # Check current environment
    current_tg, current_ebay = test_current_environment()
    
    # Get Telegram token
    if current_tg:
        use_current = input(f"\nUse current TG_TOKEN? (y/n): ").lower().startswith('y')
        tg_token = current_tg if use_current else get_telegram_bot_token()
    else:
        tg_token = get_telegram_bot_token()
    
    # Generate eBay verification token
    if current_ebay:
        use_current = input(f"\nUse current EBAY_VERIFICATION_TOKEN? (y/n): ").lower().startswith('y')
        ebay_token = current_ebay if use_current else generate_ebay_verification_token()
    else:
        ebay_token = generate_ebay_verification_token()
    
    # Show Railway setup instructions
    show_railway_setup_instructions(tg_token, ebay_token)
    
    # Save to file
    saved_file = save_tokens_to_file(tg_token, ebay_token)
    
    print("\n✅ READY FOR RAILWAY DEPLOYMENT!")
    print("=" * 50)
    print("Next steps:")
    print("1. Add the variables to Railway dashboard")
    print("2. Wait for automatic redeploy")
    print("3. Test the webhook endpoint")
    print("4. Configure eBay Developer Portal")
    print()
    print(f"Token file saved: {saved_file}")

if __name__ == "__main__":
    main()
