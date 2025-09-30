#!/bin/bash
set -e

echo "🔧 Universal HAASP Build & Run"
echo "=============================="

cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"

echo "🛑 Kill any running processes"
pkill -f haasp 2>/dev/null || true
pkill -f git_intelligence 2>/dev/null || true

echo "📂 Check build directory status"
if [ -d "build" ]; then
    echo "   Build directory exists"
    ls -la build/ | head -5
else
    echo "   Creating build directory"
    mkdir -p build
fi

cd build

echo "🔨 Configure CMake"
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo

echo "📋 Check what build system was generated"
if [ -f "build.ninja" ]; then
    echo "   ✅ Using Ninja build system"
    BUILD_CMD="ninja"
elif [ -f "Makefile" ]; then
    echo "   ✅ Using Make build system"
    BUILD_CMD="make -j$(nproc)"
else
    echo "   ❌ No build system found!"
    ls -la
    exit 1
fi

echo "🔨 Building with: $BUILD_CMD"
$BUILD_CMD

echo "🔍 Check if executable was created"
if [ -f "haasp" ]; then
    echo "✅ haasp executable found!"
    ls -la haasp
    echo ""
    echo "🚀 Starting HAASP QML Application..."
    echo "   (This should open the Qt6 window)"
    ./haasp
else
    echo "❌ haasp executable not found"
    echo "📋 Contents of build directory:"
    ls -la
    exit 1
fi