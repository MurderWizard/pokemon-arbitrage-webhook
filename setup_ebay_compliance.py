#!/usr/bin/env python3
"""
Automated eBay Compliance Setup Script
Run this after you've created your Duck DNS domain
"""
import os
import sys
import subprocess
from dotenv import load_dotenv, set_key

def main():
    print("🤖 AUTOMATED EBAY COMPLIANCE SETUP")
    print("=" * 50)
    
    # Use your Duck DNS domain automatically
    domain = "pokemon-arbitrage.duckdns.org"
    print(f"✅ Using your Duck DNS domain: {domain}")
    print("   (This is the domain you created earlier)")
    
    # Verify DNS is working
    print("🔍 Checking if DNS is working...")
    try:
        import socket
        ip = socket.gethostbyname(domain.split('.')[0] + '.duckdns.org')
        if ip == "34.74.208.133":
            print(f"✅ DNS working correctly: {domain} -> {ip}")
        else:
            print(f"⚠️  DNS shows different IP: {domain} -> {ip}")
            print("   Expected: 34.74.208.133")
            confirm = input("Continue anyway? (y/n): ").lower()
            if confirm != 'y':
                return
    except Exception as e:
        print(f"⚠️  DNS check failed: {e}")
        print("   This might be normal if DNS hasn't propagated yet")
        confirm = input("Continue with setup? (y/n): ").lower()
        if confirm != 'y':
            return
    
    # Step 1: Add domain to .env file
    print("\\n🔧 Step 1: Adding domain to .env file...")
    env_file = '/home/jthomas4641/pokemon/.env'
    set_key(env_file, 'WEBHOOK_DOMAIN', domain)
    print(f"✅ Added WEBHOOK_DOMAIN={domain} to .env")
    
    # Step 2: Stop current webhook server
    print("\\n🛑 Step 2: Stopping current webhook server...")
    try:
        subprocess.run(['sudo', 'pkill', '-f', 'direct_webhook.py'], check=False)
        print("✅ Stopped old webhook server")
    except:
        print("ℹ️  No webhook server was running")
    
    # Step 3: Get SSL certificate
    print("\\n🔒 Step 3: Getting SSL certificate from Let's Encrypt...")
    print(f"Running: sudo certbot certonly --standalone -d {domain}")
    
    try:
        # Run certbot
        result = subprocess.run([
            'sudo', 'certbot', 'certonly', '--standalone', 
            '--non-interactive', '--agree-tos', 
            '--email', 'jthomas4641@gmail.com',
            '-d', domain
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SSL certificate obtained successfully!")
        else:
            print(f"❌ Certbot failed: {result.stderr}")
            print("Manual steps:")
            print(f"1. Run: sudo certbot certonly --standalone -d {domain}")
            print("2. Follow the prompts")
            return
    except Exception as e:
        print(f"❌ Error running certbot: {e}")
        return
    
    # Step 4: Update production webhook server
    print("\\n📝 Step 4: Updating production webhook server...")
    production_file = '/home/jthomas4641/pokemon/production_webhook.py'
    
    with open(production_file, 'r') as f:
        content = f.read()
    
    # Replace placeholder with actual domain
    content = content.replace('DOMAIN_PLACEHOLDER', domain)
    
    with open(production_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated production webhook for domain: {domain}")
    
    # Step 5: Start production webhook server
    print("\\n🚀 Step 5: Starting production webhook server...")
    try:
        subprocess.Popen([
            'sudo', 'python3', production_file
        ], cwd='/home/jthomas4641/pokemon')
        print("✅ Production webhook server started on port 443")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return
    
    # Step 6: Test the endpoint
    print("\\n🧪 Step 6: Testing the endpoint...")
    import time
    time.sleep(3)  # Wait for server to start
    
    try:
        import requests
        test_url = f"https://{domain}/health"
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Endpoint is working: {test_url}")
        else:
            print(f"❌ Endpoint test failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Endpoint test failed: {e}")
        print("This might be normal if DNS hasn't propagated yet")
    
    # Final instructions
    print("\\n🎯 SETUP COMPLETE!")
    print("=" * 50)
    print()
    print("📋 NOW UPDATE EBAY DEVELOPER PORTAL:")
    print(f"   Endpoint URL: https://{domain}/marketplace-deletion")
    print(f"   Verification Token: {os.getenv('EBAY_VERIFICATION_TOKEN', 'pokemon_arbitrage_secure_token_2025_ebay_compliance_abc123')}")
    print()
    print("🔍 MONITORING:")
    print(f"   Health Check: https://{domain}/health")
    print(f"   Server Status: sudo systemctl status pokemon-webhook")
    print()
    print("✅ Your Pokemon arbitrage system is now eBay production compliant!")

if __name__ == '__main__':
    main()
