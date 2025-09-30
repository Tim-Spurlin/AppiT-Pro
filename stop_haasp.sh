#!/bin/bash

echo "🛑 Stopping HAASP Complete System"
echo "================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Kill services by PID files
echo "   Stopping tracked services..."
for pidfile in /tmp/haasp_*.pid; do
    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")
        service_name=$(basename "$pidfile" .pid | sed 's/haasp_//')
        
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "   Stopping $service_name (PID: $pid)..."
            kill "$pid"
            
            # Wait for graceful shutdown
            for i in {1..5}; do
                if ! kill -0 "$pid" 2>/dev/null; then
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "   Force killing $service_name..."
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
        
        rm -f "$pidfile"
    fi
done

# Fallback: kill by process name
echo "   Cleaning up remaining processes..."
pkill -f "haasp" 2>/dev/null || true
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "haasp-insights" 2>/dev/null || true
pkill -f "voice_service" 2>/dev/null || true

# Clean up temporary files
rm -f /tmp/haasp_*.pid

echo -e "${GREEN}✅ All HAASP services stopped${NC}"
echo -e "${YELLOW}💾 Data preserved in ~/.local/share/haasp/${NC}"
echo -e "${YELLOW}📊 Logs available in ~/.local/state/haasp/logs/${NC}"
echo ""
echo -e "${GREEN}👋 HAASP shutdown complete!${NC}"