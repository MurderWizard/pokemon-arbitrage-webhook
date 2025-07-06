#!/usr/bin/env python3
"""
Background webhook service launcher for Pokemon arbitrage
"""
import os
import sys
import time
import subprocess
import signal

def is_port_in_use(port):
    """Check if a port is in use"""
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def start_webhook_background():
    """Start webhook server in background"""
    webhook_script = '/home/jthomas4641/pokemon/direct_webhook.py'
    log_file = '/home/jthomas4641/pokemon/webhook_service.log'
    pid_file = '/home/jthomas4641/pokemon/webhook.pid'
    
    print("🚀 Starting Pokemon Arbitrage Webhook Service")
    print("=" * 50)
    
    # Check if already running
    if os.path.exists(pid_file):
        with open(pid_file, 'r') as f:
            old_pid = f.read().strip()
        try:
            os.kill(int(old_pid), 0)  # Check if process exists
            print(f"⚠️  Webhook already running (PID: {old_pid})")
            print("   Use 'stop' to stop it first")
            return False
        except OSError:
            # Process doesn't exist, remove stale pid file
            os.remove(pid_file)
    
    # Check port availability
    if is_port_in_use(8443):
        print("❌ Port 8443 is already in use")
        print("   Run: sudo fuser -k 8443/tcp")
        return False
    
    # Start the webhook server
    print("🔧 Starting webhook server...")
    process = subprocess.Popen(
        ['python3', webhook_script],
        stdout=open(log_file, 'w'),
        stderr=subprocess.STDOUT,
        cwd='/home/jthomas4641/pokemon'
    )
    
    # Save PID
    with open(pid_file, 'w') as f:
        f.write(str(process.pid))
    
    # Wait a moment to check if it started successfully
    time.sleep(3)
    
    if process.poll() is None:  # Process is still running
        print(f"✅ Webhook service started successfully")
        print(f"   PID: {process.pid}")
        print(f"   Log: {log_file}")
        print(f"   Endpoint: https://34.74.208.133:8443/webhook")
        print(f"   Health: https://34.74.208.133:8443/health")
        return True
    else:
        print("❌ Webhook failed to start")
        print(f"   Check log: {log_file}")
        if os.path.exists(pid_file):
            os.remove(pid_file)
        return False

def stop_webhook():
    """Stop the webhook service"""
    pid_file = '/home/jthomas4641/pokemon/webhook.pid'
    
    print("🛑 Stopping Pokemon Arbitrage Webhook Service")
    print("=" * 50)
    
    if not os.path.exists(pid_file):
        print("❌ No webhook service running (no PID file)")
        return False
    
    with open(pid_file, 'r') as f:
        pid = f.read().strip()
    
    try:
        os.kill(int(pid), signal.SIGTERM)
        time.sleep(2)
        
        # Check if it's still running
        try:
            os.kill(int(pid), 0)
            print(f"⚠️  Process {pid} still running, force killing...")
            os.kill(int(pid), signal.SIGKILL)
        except OSError:
            pass
        
        os.remove(pid_file)
        print(f"✅ Webhook service stopped (PID: {pid})")
        return True
        
    except OSError:
        print(f"❌ Process {pid} not found")
        os.remove(pid_file)
        return False

def status_webhook():
    """Check webhook service status"""
    pid_file = '/home/jthomas4641/pokemon/webhook.pid'
    
    print("📊 Pokemon Arbitrage Webhook Service Status")
    print("=" * 50)
    
    if not os.path.exists(pid_file):
        print("❌ Service not running (no PID file)")
        return False
    
    with open(pid_file, 'r') as f:
        pid = f.read().strip()
    
    try:
        os.kill(int(pid), 0)  # Check if process exists
        print(f"✅ Service running (PID: {pid})")
        
        # Check if port is listening
        if is_port_in_use(8443):
            print("✅ Port 8443 is listening")
            print("🌐 Webhook endpoint: https://34.74.208.133:8443/webhook")
        else:
            print("⚠️  Process running but port 8443 not listening")
        
        return True
        
    except OSError:
        print(f"❌ Process {pid} not found (stale PID file)")
        os.remove(pid_file)
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 webhook_service.py [start|stop|status|restart]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        start_webhook_background()
    elif command == 'stop':
        stop_webhook()
    elif command == 'status':
        status_webhook()
    elif command == 'restart':
        print("🔄 Restarting webhook service...")
        stop_webhook()
        time.sleep(2)
        start_webhook_background()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: start, stop, status, restart")
        sys.exit(1)

if __name__ == "__main__":
    main()
