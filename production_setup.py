#!/usr/bin/env python3
"""
🚀 POKEMON ARBITRAGE - PRODUCTION SETUP SCRIPT
==============================================

Streamlined setup for HTTPS webhook server and Telegram integration.
Based on working blow-hole infrastructure, adapted for Pokemon project.

This script:
1. Validates SSL certificates
2. Starts the HTTPS webhook server
3. Sets up the Telegram webhook
4. Tests the complete pipeline
"""

import os
import sys
import ssl
import time
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

class ProductionSetup:
    def __init__(self):
        self.external_ip = "34.74.208.133"
        self.webhook_port = 8080
        self.bot_token = os.getenv('TG_TOKEN')
        self.cert_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.crt'
        self.key_file = '/home/jthomas4641/pokemon/ssl/telegram_webhook.key'
        
        if not self.bot_token:
            print("❌ TG_TOKEN not found in .env file")
            sys.exit(1)
    
    def check_prerequisites(self):
        """Check all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check SSL certificates
        if not os.path.exists(self.cert_file):
            print(f"❌ SSL certificate not found: {self.cert_file}")
            return False
        if not os.path.exists(self.key_file):
            print(f"❌ SSL key not found: {self.key_file}")
            return False
        
        print("✅ SSL certificates found")
        
        # Check webhook server script
        webhook_script = '/home/jthomas4641/pokemon/telegram_webhook_server.py'
        if not os.path.exists(webhook_script):
            print(f"❌ Webhook server script not found: {webhook_script}")
            return False
        
        print("✅ Webhook server script found")
        
        # Check port availability
        try:
            result = subprocess.run(['lsof', '-i', f':{self.webhook_port}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"⚠️  Port {self.webhook_port} is already in use")
                print("   Killing existing processes...")
                # Kill existing processes on the port
                subprocess.run(['sudo', 'fuser', '-k', f'{self.webhook_port}/tcp'], 
                             capture_output=True)
                time.sleep(2)
        except Exception as e:
            print(f"⚠️  Could not check port status: {e}")
        
        print(f"✅ Port {self.webhook_port} available")
        return True
    
    def start_webhook_server(self):
        """Start the HTTPS webhook server"""
        print("🚀 Starting HTTPS webhook server...")
        
        webhook_script = '/home/jthomas4641/pokemon/telegram_webhook_server.py'
        
        # Start the server in background
        process = subprocess.Popen(
            ['python3', webhook_script],
            cwd='/home/jthomas4641/pokemon',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            result = subprocess.run(['lsof', '-i', f':{self.webhook_port}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Webhook server started successfully")
                return process
            else:
                print("❌ Webhook server failed to start")
                return None
        except Exception as e:
            print(f"❌ Error checking server status: {e}")
            return None
    
    def test_webhook_health(self):
        """Test if webhook server is responding"""
        print("🧪 Testing webhook server health...")
        
        health_url = f"https://{self.external_ip}:{self.webhook_port}/health"
        
        try:
            # Use verify=False for self-signed certificates
            response = requests.get(health_url, timeout=10, verify=False)
            
            if response.ok:
                data = response.json()
                print("✅ Webhook server health check passed")
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Service: {data.get('service', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def set_telegram_webhook(self):
        """Set the Telegram webhook with SSL certificate"""
        print("🔗 Setting Telegram webhook...")
        
        webhook_url = f"https://{self.external_ip}:{self.webhook_port}/webhook"
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/setWebhook"
            
            with open(self.cert_file, 'rb') as cert:
                files = {'certificate': cert}
                data = {
                    'url': webhook_url,
                    'max_connections': 40,
                    'allowed_updates': ['message', 'callback_query']
                }
                
                response = requests.post(url, data=data, files=files, timeout=30)
            
            if response.ok:
                result = response.json()
                if result.get('ok'):
                    print("✅ Telegram webhook set successfully")
                    print(f"   URL: {webhook_url}")
                    return True
                else:
                    print(f"❌ Telegram API error: {result.get('description', 'Unknown')}")
                    return False
            else:
                print(f"❌ HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error setting webhook: {e}")
            return False
    
    def check_webhook_status(self):
        """Check current webhook status"""
        print("📊 Checking webhook status...")
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getWebhookInfo"
            response = requests.get(url, timeout=10)
            
            if response.ok:
                result = response.json()
                if result.get('ok'):
                    info = result.get('result', {})
                    print("📋 Current webhook info:")
                    print(f"   URL: {info.get('url', 'Not set')}")
                    print(f"   Has Custom Certificate: {info.get('has_custom_certificate', False)}")
                    print(f"   Pending Updates: {info.get('pending_update_count', 0)}")
                    
                    if info.get('last_error_message'):
                        print(f"   ⚠️  Last Error: {info.get('last_error_message')}")
                    
                    return True
                else:
                    print(f"❌ API error: {result.get('description', 'Unknown')}")
                    return False
            else:
                print(f"❌ HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking webhook: {e}")
            return False
    
    def run_complete_setup(self):
        """Run the complete setup process"""
        print("🎴 POKEMON ARBITRAGE - PRODUCTION SETUP")
        print("=" * 50)
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites check failed")
            return False
        
        # Step 2: Start webhook server
        server_process = self.start_webhook_server()
        if not server_process:
            print("❌ Failed to start webhook server")
            return False
        
        # Step 3: Test webhook health
        if not self.test_webhook_health():
            print("❌ Webhook health check failed")
            server_process.terminate()
            return False
        
        # Step 4: Set Telegram webhook
        if not self.set_telegram_webhook():
            print("❌ Failed to set Telegram webhook")
            server_process.terminate()
            return False
        
        # Step 5: Verify webhook status
        if not self.check_webhook_status():
            print("❌ Webhook status check failed")
            server_process.terminate()
            return False
        
        print("\n" + "=" * 50)
        print("🎉 PRODUCTION SETUP COMPLETE!")
        print("✅ HTTPS webhook server running")
        print("✅ SSL certificates configured")
        print("✅ Telegram webhook active")
        print("✅ System ready for button actions")
        print("\n🚀 NEXT STEPS:")
        print("1. Test button functionality in Telegram")
        print("2. Start deal monitoring: python3 smart_deal_finder.py")
        print("3. Monitor webhook logs for button presses")
        print(f"\n📊 Server running at: https://{self.external_ip}:{self.webhook_port}")
        print(f"📋 Process ID: {server_process.pid}")
        print("=" * 50)
        
        return True

def main():
    """Main entry point"""
    try:
        setup = ProductionSetup()
        success = setup.run_complete_setup()
        
        if success:
            print("\n💡 Keep this terminal open - webhook server is running")
            print("Press Ctrl+C to stop the server")
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n👋 Shutting down webhook server...")
                print("✅ Production setup completed successfully")
        else:
            print("\n❌ Setup failed - check errors above")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
