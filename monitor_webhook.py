#!/usr/bin/env python3
"""
Real-time webhook monitoring for Pokemon arbitrage
"""
import time
import subprocess
import sys

def monitor_webhook():
    """Monitor webhook activity in real-time"""
    print("🔍 POKEMON ARBITRAGE - WEBHOOK MONITOR")
    print("=" * 50)
    print("📊 Monitoring webhook activity...")
    print("🔘 Button clicks will appear below")
    print("⏹️  Press Ctrl+C to stop monitoring")
    print("=" * 50)
    
    try:
        # Use tail -f to follow the log file
        process = subprocess.Popen(
            ['tail', '-f', '/home/jthomas4641/pokemon/webhook_service.log'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                # Highlight important events
                if "Button pressed:" in line:
                    print(f"🔘 {line.strip()}")
                elif "APPROVED" in line:
                    print(f"✅ {line.strip()}")
                elif "PASSED" in line:
                    print(f"❌ {line.strip()}")
                elif "Webhook received:" in line:
                    print(f"📨 {line.strip()}")
                else:
                    print(line.strip())
                    
    except KeyboardInterrupt:
        print("\n\n👋 Webhook monitoring stopped")
        process.terminate()
    except Exception as e:
        print(f"❌ Error monitoring webhook: {e}")

if __name__ == "__main__":
    monitor_webhook()
