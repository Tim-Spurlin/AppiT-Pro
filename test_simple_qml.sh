#!/bin/bash
set -e

echo "🎯 Testing Simplified QML Application"
echo "===================================="

cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"

echo "🔨 Rebuild with simplified QML"
cd build
ninja

echo "🚀 Testing application"
echo "   Current directory: $(pwd)"
echo "   Executable: $(ls -la haasp)"
echo ""
echo "Starting HAASP with simplified interface..."
./haasp