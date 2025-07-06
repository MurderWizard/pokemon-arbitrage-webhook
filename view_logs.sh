#!/bin/bash

# View Logs Script
# This script shows live logs from all automation components

echo "📋 Hands-Off Automation System Logs"
echo "==================================="
echo "Press Ctrl+C to exit"
echo ""

# Function to show logs with color coding
show_logs() {
    local log_file=$1
    local component=$2
    local color=$3
    
    if [ -f "$log_file" ]; then
        echo -e "\033[${color}m=== $component ===\033[0m"
        tail -n 10 "$log_file"
        echo ""
    fi
}

# Show recent logs from all components
show_logs "logs/app.log" "API Server" "32"      # Green
show_logs "logs/worker.log" "Background Worker" "34"  # Blue
show_logs "logs/scheduler.log" "Automation Scheduler" "35"  # Magenta
show_logs "logs/dashboard.log" "Dashboard" "36"  # Cyan
show_logs "logs/bot.log" "Telegram Bot" "33"    # Yellow

# Follow logs in real-time
echo "🔄 Following logs in real-time..."
echo "================================="

# Create logs directory if it doesn't exist
mkdir -p logs

# Follow multiple log files
if command -v multitail &> /dev/null; then
    # Use multitail if available for better display
    multitail -i logs/app.log -i logs/worker.log -i logs/scheduler.log -i logs/dashboard.log -i logs/bot.log
else
    # Fall back to tail -f
    tail -f logs/*.log 2>/dev/null || echo "No log files found. Start the system first with ./start_automation.sh"
fi
