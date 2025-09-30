#!/bin/bash
set -e

echo "🎯 Testing QML Application Only"
echo "=============================="

cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"

echo "🛑 Kill any running processes"
pkill -f haasp 2>/dev/null || true
pkill -f git_intelligence 2>/dev/null || true

echo "📍 Current directory: $(pwd)"
echo "📁 Checking build directory..."
ls -la build/ || echo "Build directory not found"

echo "🔍 Looking for executable..."
if [ -f "build/haasp" ]; then
    echo "✅ Found haasp executable"
    echo "🚀 Starting QML application..."
    cd build
    ./haasp
else
    echo "❌ haasp executable not found"
    echo "📋 Contents of build directory:"
    ls -la build/ 2>/dev/null || echo "Build directory doesn't exist"
    
    echo "🔨 Need to build first..."
    mkdir -p build
    cd build
    echo "   Configuring..."
    cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo
    echo "   Building..."
    make -j$(nproc)
    echo "✅ Build complete"
    echo "🚀 Starting application..."
    ./haasp
fi