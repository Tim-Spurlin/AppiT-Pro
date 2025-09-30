#!/bin/bash
set -e

echo "🔧 Final HAASP Fix - QML Resources & Dependencies"
echo "=============================================="

cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"

echo "✅ Fixed Issues:"
echo "   - Created traditional .qrc file for QML resources"
echo "   - Fixed askama dependency version conflict"
echo "   - Updated CMakeLists.txt to use .qrc file"

echo "🧹 Clean rebuild..."
rm -rf build
mkdir -p build
cd build

echo "🔨 Building C++ with fixed resources..."
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo
make -j$(nproc)

echo "✅ C++ build complete!"

cd ..

echo "🦀 Building Rust webapp with fixed dependencies..."
cd webapp
cargo build --release
echo "✅ Rust build complete!"

cd ..

echo ""
echo "🚀 Starting HAASP Application..."

# Start C++ app in background
echo "   Starting QML application..."
./build/haasp &
HAASP_PID=$!

# Start Rust webapp
echo "   Starting analytics server..."
cd webapp
./target/release/haasp-insights &
WEBAPP_PID=$!
cd ..

echo ""
echo "🎉 HAASP IS RUNNING!"
echo ""
echo "📱 Main Application: Qt6/Kirigami interface should be visible"
echo "🌐 Analytics Dashboard: https://127.0.0.1:7420"
echo ""
echo "Press Ctrl+C to stop all services"

# Setup cleanup trap
trap 'echo ""; echo "🛑 Stopping services..."; kill $HAASP_PID 2>/dev/null || true; kill $WEBAPP_PID 2>/dev/null || true; echo "👋 Goodbye!"; exit 0' INT

# Wait for user interrupt
wait