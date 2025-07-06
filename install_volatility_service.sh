#!/bin/bash

# Make scripts executable
chmod +x auto_volatility_monitor.py
chmod +x price_volatility_tracker.py
chmod +x daily_price_updater.py

# Copy service file to systemd
sudo cp pokemon-volatility.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable pokemon-volatility
sudo systemctl start pokemon-volatility

echo "Volatility monitoring service installed and started!"
echo "Check status with: sudo systemctl status pokemon-volatility"
