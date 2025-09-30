#!/bin/bash
# HAASP Installer Script
# Installs HAASP as a system application with desktop integration

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/haasp"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons"

echo -e "${BLUE}🚀 HAASP Installer${NC}"
echo -e "${BLUE}=================${NC}"
echo ""

# Check if running as root for system install
if [ "$1" = "--system" ]; then
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}❌ System install requires root privileges${NC}"
        echo "Run: sudo $0 --system"
        exit 1
    fi
    INSTALL_DIR="/opt/haasp"
    DESKTOP_DIR="/usr/share/applications"
    ICON_DIR="/usr/share/icons"
    echo -e "${YELLOW}📦 System-wide installation${NC}"
else
    echo -e "${YELLOW}📦 User installation${NC}"
fi

echo -e "${BLUE}🔧 Setting up directories...${NC}"

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"

# Copy application files
echo -e "${BLUE}📋 Copying application files...${NC}"
cp -r "$PROJECT_DIR"/* "$INSTALL_DIR/"

# Set permissions
chmod +x "$INSTALL_DIR/start.sh"
chmod +x "$INSTALL_DIR/build/haasp"

# Install desktop file
echo -e "${BLUE}🖥️  Installing desktop integration...${NC}"
sed "s|Exec=.*|Exec=\"$INSTALL_DIR/start.sh\" start|" "$INSTALL_DIR/HAASP.desktop" > "$DESKTOP_DIR/haasp.desktop"
chmod +x "$DESKTOP_DIR/haasp.desktop"

# Install icon
cp "$INSTALL_DIR/resources/haasp-icon.svg" "$ICON_DIR/"

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR"
fi

echo ""
echo -e "${GREEN}✅ HAASP installed successfully!${NC}"
echo ""
echo -e "${YELLOW}📍 Installation location:${NC} $INSTALL_DIR"
echo -e "${YELLOW}🖥️  Desktop file:${NC} $DESKTOP_DIR/haasp.desktop"
echo -e "${YELLOW}🎨 Icon:${NC} $ICON_DIR/haasp-icon.svg"
echo ""
echo -e "${BLUE}🚀 To run HAASP:${NC}"
echo "  • Click the HAASP icon in your applications menu"
echo "  • Or run: $INSTALL_DIR/start.sh start"
echo ""
echo -e "${CYAN}💡 The application will build and start all services automatically${NC}"