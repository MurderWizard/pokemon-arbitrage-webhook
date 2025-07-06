#!/bin/bash

# Stop Automation Script
# This script stops all components of the hands-off automation system

set -e

echo "🛑 Stopping Hands-Off Automation System"
echo "========================================"

# Function to stop process by PID file
stop_process() {
    local pid_file=$1
    local process_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🔄 Stopping $process_name (PID: $pid)..."
            kill "$pid"
            sleep 2
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚠️  Force killing $process_name..."
                kill -9 "$pid"
            fi
            
            echo "✅ $process_name stopped"
        else
            echo "ℹ️  $process_name was not running"
        fi
        rm -f "$pid_file"
    else
        echo "ℹ️  No PID file found for $process_name"
    fi
}

# Stop all application components
stop_process ".app.pid" "API Server"
stop_process ".worker.pid" "Background Worker"
stop_process ".scheduler.pid" "Automation Scheduler"
stop_process ".dashboard.pid" "Dashboard"
stop_process ".bot.pid" "Telegram Bot"

# Stop Docker services
echo "🐳 Stopping Docker services..."
docker-compose down

# Kill any remaining Python processes related to the project
echo "🧹 Cleaning up remaining processes..."
pkill -f "app.main" || true
pkill -f "app.workers" || true
pkill -f "app.services.automation_scheduler" || true
pkill -f "app.dashboard" || true
pkill -f "app.telegram.bot" || true

echo ""
echo "✅ Hands-Off Automation System Stopped"
echo "======================================"
echo "All components have been shut down."
echo "To restart, run: ./start_automation.sh"
echo ""
