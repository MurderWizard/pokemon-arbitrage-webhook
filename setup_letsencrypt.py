#!/usr/bin/env python3
"""
Let's Encrypt SSL Setup for eBay Compliance
This script will set up a trusted SSL certificate using Let's Encrypt
"""
import os
import subprocess

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ Success: {description}")
        if result.stdout:
            print(f"   📄 Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {description}")
        print(f"   📄 Error: {e.stderr}")
        return False

def install_certbot():
    """Install certbot for Let's Encrypt"""
    print("📦 Installing Certbot...")
    
    commands = [
        ("sudo apt update", "Updating package list"),
        ("sudo apt install -y snapd", "Installing snapd"),
        ("sudo snap install core; sudo snap refresh core", "Installing snap core"),
        ("sudo snap install --classic certbot", "Installing certbot via snap"),
        ("sudo ln -sf /snap/bin/certbot /usr/bin/certbot", "Creating certbot symlink")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    return True

def stop_webhook_server():
    """Stop the webhook server to free up port 443"""
    print("🛑 Stopping webhook server...")
    
    # Find processes using port 443
    try:
        result = subprocess.run("sudo lsof -ti:443", shell=True, capture_output=True, text=True)
        if result.stdout:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                run_command(f"sudo kill {pid}", f"Stopping process {pid}")
        print("   ✅ Port 443 is now available")
        return True
    except Exception as e:
        print(f"   ⚠️  Could not stop processes on port 443: {e}")
        return False

def get_letsencrypt_certificate():
    """Get Let's Encrypt certificate"""
    domain = "pokemon-arbitrage.duckdns.org"
    print(f"🔒 Getting Let's Encrypt certificate for {domain}...")
    
    # Use standalone mode since we'll temporarily stop the webhook
    cmd = f"""sudo certbot certonly \\
        --standalone \\
        --non-interactive \\
        --agree-tos \\
        --email your_email@example.com \\
        --domains {domain}"""
    
    if run_command(cmd, f"Getting SSL certificate for {domain}"):
        print(f"   ✅ SSL certificate obtained successfully!")
        print(f"   📁 Certificate location: /etc/letsencrypt/live/{domain}/")
        return True
    else:
        print(f"   ❌ Failed to get SSL certificate")
        return False

def copy_certificates():
    """Copy certificates to our webhook directory"""
    domain = "pokemon-arbitrage.duckdns.org"
    webhook_dir = "/home/jthomas4641/pokemon/ssl"
    
    print("📋 Copying certificates to webhook directory...")
    
    commands = [
        (f"sudo mkdir -p {webhook_dir}", "Creating SSL directory"),
        (f"sudo cp /etc/letsencrypt/live/{domain}/fullchain.pem {webhook_dir}/telegram_webhook.crt", "Copying certificate"),
        (f"sudo cp /etc/letsencrypt/live/{domain}/privkey.pem {webhook_dir}/telegram_webhook.key", "Copying private key"),
        (f"sudo chown $(whoami):$(whoami) {webhook_dir}/*", "Changing ownership"),
        (f"sudo chmod 600 {webhook_dir}/telegram_webhook.key", "Setting key permissions"),
        (f"sudo chmod 644 {webhook_dir}/telegram_webhook.crt", "Setting certificate permissions")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    return True

def setup_auto_renewal():
    """Set up automatic certificate renewal"""
    print("🔄 Setting up automatic certificate renewal...")
    
    # Create renewal script
    renewal_script = """#!/bin/bash
# Let's Encrypt auto-renewal script for Pokemon Arbitrage webhook

# Stop the webhook server
sudo pkill -f "python.*direct_webhook.py" || true
sleep 5

# Renew certificates
certbot renew --quiet

# Copy new certificates
cp /etc/letsencrypt/live/pokemon-arbitrage.duckdns.org/fullchain.pem /home/jthomas4641/pokemon/ssl/telegram_webhook.crt
cp /etc/letsencrypt/live/pokemon-arbitrage.duckdns.org/privkey.pem /home/jthomas4641/pokemon/ssl/telegram_webhook.key
chown $(whoami):$(whoami) /home/jthomas4641/pokemon/ssl/*
chmod 600 /home/jthomas4641/pokemon/ssl/telegram_webhook.key
chmod 644 /home/jthomas4641/pokemon/ssl/telegram_webhook.crt

# Restart webhook server
cd /home/jthomas4641/pokemon
sudo python3 direct_webhook.py &
"""
    
    with open("/tmp/renew_certificates.sh", "w") as f:
        f.write(renewal_script)
    
    commands = [
        ("sudo mv /tmp/renew_certificates.sh /usr/local/bin/", "Moving renewal script"),
        ("sudo chmod +x /usr/local/bin/renew_certificates.sh", "Making script executable"),
        ("sudo crontab -l | grep -v 'renew_certificates' | sudo crontab -", "Removing old cron jobs"),
        ("(sudo crontab -l; echo '0 3 * * * /usr/local/bin/renew_certificates.sh') | sudo crontab -", "Adding renewal cron job")
    ]
    
    for cmd, desc in commands:
        run_command(cmd, desc)
    
    return True

def main():
    """Main setup function"""
    print("🚀 Let's Encrypt SSL Setup for eBay Compliance")
    print("=" * 50)
    print("This will set up a trusted SSL certificate using Let's Encrypt")
    print("Your domain: pokemon-arbitrage.duckdns.org")
    print("=" * 50)
    
    steps = [
        ("Installing Certbot", install_certbot),
        ("Stopping webhook server", stop_webhook_server),
        ("Getting Let's Encrypt certificate", get_letsencrypt_certificate),
        ("Copying certificates", copy_certificates),
        ("Setting up auto-renewal", setup_auto_renewal)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        if not step_func():
            print(f"❌ Setup failed at step: {step_name}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Let's Encrypt SSL setup completed successfully!")
    print("=" * 50)
    print("✅ Your webhook now has a trusted SSL certificate")
    print("✅ Auto-renewal is configured")
    print("🔄 Now restart your webhook server:")
    print("   cd /home/jthomas4641/pokemon")
    print("   sudo python3 direct_webhook.py")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    main()
