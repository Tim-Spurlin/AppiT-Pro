#!/bin/bash
set -e

echo "🚀 HAASP Complete System Startup"
echo "==============================="
echo "Starting all advanced features and services..."

cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Step 1: Verify and Install Dependencies${NC}"

# Check for required system packages
check_package() {
    if pacman -Qi "$1" &> /dev/null; then
        echo -e "  ✅ $1"
    else
        echo -e "  ❌ $1 - installing..."
        sudo pacman -S --noconfirm "$1"
    fi
}

echo "   Checking system packages..."
check_package "qt6-base"
check_package "qt6-declarative" 
check_package "qt6-tools"
check_package "libgit2"
check_package "python-pip"
check_package "rustup"
check_package "cmake"
check_package "ninja"

# Audio packages for voice activation
check_package "pipewire"
check_package "pipewire-pulse"
check_package "python-sounddevice" || pip install --user sounddevice

echo -e "${GREEN}✅ System dependencies verified${NC}"

echo -e "${BLUE}🔧 Step 2: Setup Python Retrieval Service${NC}"

# Create and setup retrieval service environment
if [ ! -d "retrieval_service/.venv" ]; then
    echo "   Creating Python virtual environment..."
    cd retrieval_service
    python -m venv .venv
    cd ..
fi

echo "   Installing Python dependencies for retrieval service..."
cd retrieval_service
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Additional packages for advanced features
pip install python-Levenshtein networkx soundfile

echo -e "   ✅ Retrieval service environment ready"
cd ..

echo -e "${BLUE}🔧 Step 3: Build C++ Core Engine${NC}"

echo "   Configuring CMake..."
mkdir -p build
cd build

# Configure with all features enabled
cmake .. -G Ninja \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DCMAKE_CXX_FLAGS="-O2 -march=native" \
    -DHAASP_ENABLE_VOICE=ON \
    -DHAASP_ENABLE_GRAPH=ON

echo "   Building C++ engine..."
ninja -j$(nproc)

if [ ! -f "haasp" ]; then
    echo -e "${RED}❌ C++ build failed - executable not found${NC}"
    exit 1
fi

echo -e "   ✅ C++ engine built successfully"
cd ..

echo -e "${BLUE}🔧 Step 4: Build Rust Analytics WebApp${NC}"

cd webapp
echo "   Building Rust analytics server..."
cargo build --release

if [ ! -f "target/release/haasp-insights" ]; then
    echo -e "${YELLOW}⚠️  Rust webapp build failed - continuing without analytics${NC}"
else
    echo -e "   ✅ Rust analytics server ready"
fi
cd ..

echo -e "${BLUE}🔧 Step 5: Initialize Advanced Features${NC}"

# Create necessary directories
mkdir -p ~/.local/share/haasp/{models,certs,logs}
mkdir -p ~/.local/state/haasp/logs

# Generate TLS certificates for local services
if [ ! -f ~/.local/share/haasp/certs/cert.pem ]; then
    echo "   Generating TLS certificates..."
    openssl req -x509 -newkey rsa:4096 -keyout ~/.local/share/haasp/certs/key.pem \
        -out ~/.local/share/haasp/certs/cert.pem -days 365 -nodes \
        -subj "/C=US/ST=Local/L=Local/O=HAASP/CN=localhost" 2>/dev/null
    chmod 600 ~/.local/share/haasp/certs/key.pem
    echo -e "   ✅ TLS certificates generated"
fi

# Initialize vector databases
echo "   Initializing vector storage..."
cd retrieval_service
source .venv/bin/activate

python3 -c "
import logging
logging.basicConfig(level=logging.INFO)

from faiss_manager import HybridVectorManager
from fts_manager import FuzzySearchManager
from graph_memory import NeuralGraphMemory

print('Initializing retrieval systems...')
vector_mgr = HybridVectorManager()
vector_mgr.build_main_index()
vector_mgr.save_index()

fuzzy_mgr = FuzzySearchManager()
graph_mgr = NeuralGraphMemory()
graph_mgr.save_graph()

print('✅ Vector systems initialized')
"

cd ..
echo -e "   ✅ Advanced features initialized"

echo -e "${BLUE}🚀 Step 6: Start All Services${NC}"

# Function to start service in background and track PID
start_service() {
    local name="$1"
    local command="$2"
    local pidfile="/tmp/haasp_${name}.pid"
    
    echo "   Starting $name..."
    
    # Kill existing process if running
    if [ -f "$pidfile" ]; then
        kill $(cat "$pidfile") 2>/dev/null || true
        rm -f "$pidfile"
    fi
    
    # Start new process
    bash -c "$command" &
    echo $! > "$pidfile"
    
    sleep 1
    if kill -0 $(cat "$pidfile") 2>/dev/null; then
        echo -e "   ✅ $name started (PID: $(cat $pidfile))"
    else
        echo -e "   ❌ $name failed to start"
        rm -f "$pidfile"
    fi
}

# Start retrieval service
start_service "retrieval_service" "
    cd retrieval_service
    source .venv/bin/activate
    export PYTHONPATH=\$PWD:\$PYTHONPATH
    python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
"

# Start voice service
start_service "voice_service" "
    cd retrieval_service  # Voice service is part of retrieval for now
    source .venv/bin/activate
    export PYTHONPATH=\$PWD:\$PYTHONPATH
    python -c 'import asyncio; from voice_service.vad import VoiceServiceAPI; from rag_orchestrator import RAGOrchestrator; asyncio.run(VoiceServiceAPI(RAGOrchestrator()).start_voice_service())'
"

# Start Rust analytics webapp (if available)
if [ -f "webapp/target/release/haasp-insights" ]; then
    start_service "webapp" "
        cd webapp
        ./target/release/haasp-insights
    "
fi

# Wait for services to be ready
echo "   Waiting for services to initialize..."
sleep 3

# Test service endpoints
echo "   Testing service connectivity..."

# Test retrieval service
if curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo -e "   ✅ Retrieval service: http://127.0.0.1:8000"
else
    echo -e "   ⚠️  Retrieval service not responding"
fi

# Test analytics webapp
if curl -s -k https://127.0.0.1:7420/ > /dev/null; then
    echo -e "   ✅ Analytics webapp: https://127.0.0.1:7420"
else
    echo -e "   ⚠️  Analytics webapp not responding"
fi

echo -e "${BLUE}🚀 Step 7: Launch HAASP Main Interface${NC}"

# Set Qt/Wayland environment
export QT_QPA_PLATFORM=wayland
export QML_DISABLE_DISK_CACHE=1
export QSG_RENDER_LOOP=threaded

echo "   Starting HAASP QML interface..."

# Start main application
start_service "haasp_main" "
    cd build
    export QT_QPA_PLATFORM=wayland
    export QML_DISABLE_DISK_CACHE=1
    ./haasp
"

echo ""
echo -e "${GREEN}🎉 HAASP COMPLETE SYSTEM IS NOW RUNNING!${NC}"
echo ""
echo -e "${CYAN}📱 Main Interface:${NC} HAASP Qt6/QML Application"
echo -e "${CYAN}🔍 Retrieval Service:${NC} http://127.0.0.1:8000"
echo -e "${CYAN}📊 Analytics Dashboard:${NC} https://127.0.0.1:7420"  
echo -e "${CYAN}🎤 Voice Activation:${NC} Available (requires calibration)"
echo ""
echo -e "${YELLOW}💡 Features Available:${NC}"
echo -e "   🧠 Hybrid retrieval (Vector + Fuzzy + Graph)"
echo -e "   🎯 RAG with Grok API integration"
echo -e "   🤖 AI Pilots (Sentinel, Doc Architect, Remediator, Codewright)"
echo -e "   🎨 Infinite canvas for pilot orchestration"
echo -e "   📊 Advanced Git analytics (GitHub++ features)"
echo -e "   🎤 Voice-activated commands"
echo -e "   💾 Conversation memory and context awareness"
echo -e "   🔍 Semantic search across all data"
echo ""
echo -e "${PURPLE}🛠️  How to Use:${NC}"
echo -e "   1. The QML interface should be visible with advanced features"
echo -e "   2. Use the infinite canvas to create and connect pilots"
echo -e "   3. Enable voice activation in settings (requires microphone calibration)"
echo -e "   4. Open a repository to enable Git analytics"
echo -e "   5. Use intelligent search for context-aware assistance"
echo ""
echo -e "${CYAN}🛑 To Stop All Services:${NC} Press Ctrl+C or run: ./stop_haasp.sh"

# Setup signal handling for graceful shutdown
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down HAASP services...${NC}"
    
    # Kill all services
    for pidfile in /tmp/haasp_*.pid; do
        if [ -f "$pidfile" ]; then
            kill $(cat "$pidfile") 2>/dev/null || true
            rm -f "$pidfile"
        fi
    done
    
    # Fallback process cleanup
    pkill -f "haasp" 2>/dev/null || true
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "haasp-insights" 2>/dev/null || true
    
    echo -e "${GREEN}✅ All services stopped${NC}"
    echo -e "${PURPLE}👋 Thanks for using HAASP!${NC}"
    exit 0
}

# Register signal handlers
trap cleanup SIGINT SIGTERM

# Keep script running to manage services
echo -e "${CYAN}🔄 HAASP is running... Press Ctrl+C to stop all services${NC}"

# Monitor services and restart if needed
while true do
    sleep 10
    
    # Check if main application is still running
    if [ -f "/tmp/haasp_haasp_main.pid" ]; then
        if ! kill -0 $(cat /tmp/haasp_haasp_main.pid) 2>/dev/null; then
            echo -e "${YELLOW}⚠️  Main application stopped, restarting...${NC}"
            start_service "haasp_main" "
                cd build
                export QT_QPA_PLATFORM=wayland
                ./haasp
            "
        fi
    fi
    
    # Check retrieval service
    if ! curl -s http://127.0.0.1:8000/ > /dev/null; then
        echo -e "${YELLOW}⚠️  Retrieval service down, restarting...${NC}"
        start_service "retrieval_service" "
            cd retrieval_service
            source .venv/bin/activate
            python -m uvicorn main:app --host 127.0.0.1 --port 8000
        "
    fi
done