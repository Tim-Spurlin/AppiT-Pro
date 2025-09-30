#!/bin/bash
# HAASP Development Environment Startup Script
# 
# This script sets up and starts the complete HAASP development platform:
# - C++ Core with Qt6/QML UI
# - Python ML Intelligence Pipeline  
# - Rust Insights++ WebApp
# - Git Integration and Analytics

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project directories
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$PROJECT_DIR/build"
PYTHON_DIR="$PROJECT_DIR/python"
WEBAPP_DIR="$PROJECT_DIR/webapp"

echo -e "${PURPLE}🚀 HAASP - Hyper-Advanced Associative Application Synthesis Platform${NC}"
echo -e "${CYAN}   Starting development environment...${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check dependencies
check_dependencies() {
    echo -e "${BLUE}🔍 Checking dependencies...${NC}"
    
    # Essential tools
    local deps=("cmake" "ninja" "python3" "rustc" "cargo" "git")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command_exists "$dep"; then
            missing+=("$dep")
        fi
    done
    
    # Qt6 check
    if ! pkg-config --exists Qt6Core Qt6Quick Qt6Qml; then
        missing+=("qt6-base qt6-declarative qt6-quickcontrols2")
    fi
    
    # libgit2 check  
    if ! pkg-config --exists libgit2; then
        missing+=("libgit2")
    fi
    
    if [ ${#missing[@]} -ne 0 ]; then
        echo -e "${RED}❌ Missing dependencies: ${missing[*]}${NC}"
        echo -e "${YELLOW}💡 Install with: sudo pacman -S ${missing[*]}${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All dependencies satisfied${NC}"
}

# Function to setup Python environment
setup_python() {
    echo -e "${BLUE}🐍 Setting up Python environment...${NC}"
    
    cd "$PYTHON_DIR"
    
    # Check if uv is available, otherwise use pip
    if command_exists uv; then
        echo -e "${CYAN}   Using uv for package management${NC}"
        
        # Create virtual environment if it doesn't exist
        if [ ! -d ".venv" ]; then
            uv venv --python 3.11
            echo -e "${GREEN}   Created Python virtual environment${NC}"
        fi
        
        # Activate environment and install packages
        source .venv/bin/activate
        uv pip install -r requirements.txt
        
        # Install additional packages for Jupyter support
        uv pip install ipykernel matplotlib jupyter
        
    else
        echo -e "${YELLOW}   uv not found, using pip${NC}"
        
        # Create virtual environment
        if [ ! -d ".venv" ]; then
            python3 -m venv .venv
            echo -e "${GREEN}   Created Python virtual environment${NC}"
        fi
        
        source .venv/bin/activate
        pip install -r requirements.txt
        pip install ipykernel matplotlib jupyter
    fi
    
    echo -e "${GREEN}✅ Python environment ready${NC}"
    cd "$PROJECT_DIR"
}

# Function to build C++ components
build_cpp() {
    echo -e "${BLUE}⚙️  Building C++ components...${NC}"
    
    # Create build directory
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"
    
    # Configure with optimizations
    echo -e "${CYAN}   Configuring CMake...${NC}"
    cmake .. -G Ninja \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        -DCMAKE_CXX_FLAGS="-march=native -mavx2" \
        -DQML_DISABLE_DISK_CACHE=1
    
    # Build
    echo -e "${CYAN}   Compiling...${NC}"
    ninja -j$(nproc)
    
    echo -e "${GREEN}✅ C++ build complete${NC}"
    cd "$PROJECT_DIR"
}

# Function to setup Rust webapp
setup_rust() {
    echo -e "${BLUE}🦀 Setting up Rust webapp...${NC}"
    
    cd "$WEBAPP_DIR"
    
    # Check Rust version
    echo -e "${CYAN}   Rust version: $(rustc --version)${NC}"
    
    # Build in release mode for performance
    echo -e "${CYAN}   Building webapp...${NC}"
    cargo build --release
    
    # Generate self-signed certificate for HTTPS
    mkdir -p cert
    if [ ! -f "cert/localhost.crt" ]; then
        echo -e "${CYAN}   Generating self-signed certificate...${NC}"
        openssl req -x509 -newkey rsa:4096 -keyout cert/localhost.key \
            -out cert/localhost.crt -days 365 -nodes \
            -subj "/C=US/ST=Local/L=Local/O=HAASP/CN=localhost" 2>/dev/null || {
            echo -e "${YELLOW}   OpenSSL not available, using fallback cert${NC}"
        }
    fi
    
    echo -e "${GREEN}✅ Rust webapp ready${NC}"
    cd "$PROJECT_DIR"
}

# Function to start services in background
start_services() {
    echo -e "${BLUE}🌟 Starting HAASP services...${NC}"
    
    # Kill existing processes
    pkill -f "haasp" 2>/dev/null || true
    pkill -f "git_intelligence.py" 2>/dev/null || true
    pkill -f "haasp-insights" 2>/dev/null || true
    
    sleep 1
    
    # Start Python ML pipeline
    echo -e "${CYAN}   Starting ML Intelligence Pipeline...${NC}"
    cd "$PYTHON_DIR"
    source .venv/bin/activate
    python enrichment_pipeline/git_intelligence.py &
    PYTHON_PID=$!
    cd "$PROJECT_DIR"
    
    # Start Rust webapp
    echo -e "${CYAN}   Starting Insights++ WebApp...${NC}"
    cd "$WEBAPP_DIR"
    RUST_LOG=info ./target/release/haasp-insights &
    WEBAPP_PID=$!
    cd "$PROJECT_DIR"
    
    # Give services time to start
    sleep 2
    
    # Start main HAASP application
    echo -e "${CYAN}   Starting HAASP QML Application...${NC}"
    cd "$BUILD_DIR"
    ./haasp &
    HAASP_PID=$!
    cd "$PROJECT_DIR"
    
    # Store PIDs for cleanup
    echo "$PYTHON_PID" > /tmp/haasp_python.pid
    echo "$WEBAPP_PID" > /tmp/haasp_webapp.pid  
    echo "$HAASP_PID" > /tmp/haasp_main.pid
    
    echo ""
    echo -e "${GREEN}🎉 HAASP is now running!${NC}"
    echo ""
    echo -e "${YELLOW}📱 QML Application:${NC} Main HAASP interface started"
    echo -e "${YELLOW}🌐 Insights++ Dashboard:${NC} https://127.0.0.1:7420"
    echo -e "${YELLOW}🤖 ML Pipeline:${NC} Running in background"
    echo ""
    echo -e "${CYAN}💡 Use Ctrl+C to stop all services${NC}"
}

# Function to cleanup processes
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping HAASP services...${NC}"
    
    # Kill stored PIDs
    if [ -f /tmp/haasp_main.pid ]; then
        kill $(cat /tmp/haasp_main.pid) 2>/dev/null || true
        rm /tmp/haasp_main.pid
    fi
    
    if [ -f /tmp/haasp_webapp.pid ]; then
        kill $(cat /tmp/haasp_webapp.pid) 2>/dev/null || true
        rm /tmp/haasp_webapp.pid
    fi
    
    if [ -f /tmp/haasp_python.pid ]; then
        kill $(cat /tmp/haasp_python.pid) 2>/dev/null || true
        rm /tmp/haasp_python.pid
    fi
    
    # Fallback: kill by name
    pkill -f "haasp" 2>/dev/null || true
    pkill -f "git_intelligence.py" 2>/dev/null || true
    pkill -f "haasp-insights" 2>/dev/null || true
    
    echo -e "${GREEN}✅ All services stopped${NC}"
    echo -e "${PURPLE}👋 Thanks for using HAASP!${NC}"
    exit 0
}

# Function to show help
show_help() {
    echo "HAASP Development Environment"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start     Start all HAASP services (default)"
    echo "  build     Build all components without starting"
    echo "  clean     Clean build artifacts"
    echo "  deps      Check dependencies only"
    echo "  help      Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  HAASP_DEBUG=1    Enable debug output"
    echo "  HAASP_PORT=7420  Change webapp port (default: 7420)"
    echo ""
}

# Trap Ctrl+C for cleanup
trap cleanup SIGINT SIGTERM

# Main execution
case "${1:-start}" in
    "start")
        check_dependencies
        setup_python
        build_cpp
        setup_rust
        start_services
        
        # Wait for user interrupt
        while true; do
            sleep 1
        done
        ;;
    
    "build")
        check_dependencies
        setup_python
        build_cpp
        setup_rust
        echo -e "${GREEN}🎯 Build complete - use './start.sh start' to run${NC}"
        ;;
    
    "clean")
        echo -e "${BLUE}🧹 Cleaning build artifacts...${NC}"
        rm -rf "$BUILD_DIR"
        rm -rf "$PYTHON_DIR/.venv"
        cd "$WEBAPP_DIR" && cargo clean && cd "$PROJECT_DIR"
        echo -e "${GREEN}✅ Clean complete${NC}"
        ;;
    
    "deps")
        check_dependencies
        ;;
    
    "help"|"--help"|"-h")
        show_help
        ;;
    
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        show_help
        exit 1
        ;;
esac