#!/bin/bash
set -e

echo "🚀 HAASP - Starting Application (Fixed Generator)"
echo "============================================="

cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"

echo "🧹 Cleaning build generator conflict..."
rm -rf build/CMakeCache.txt
rm -rf build/CMakeFiles

echo "🔨 Building with consistent generator..."
cd build
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo
make -j$(nproc)

echo "✅ C++ build complete!"

cd ..

echo "🦀 Testing Rust webapp..."
cd webapp
if cargo build --release; then
    echo "✅ Rust build successful!"
else
    echo "⚠️  Rust build failed, continuing anyway..."
fi
cd ..

echo ""
echo "🎉 Ready to run!"
echo ""
echo "🚀 Starting HAASP components:"

# Start the C++ application in background
echo "   Starting C++ application..."
./build/haasp &
HAASP_PID=$!

# Start Rust webapp if available
if [ -f "webapp/target/release/haasp-insights" ]; then
    echo "   Starting Rust analytics server..."
    cd webapp
    ./target/release/haasp-insights &
    WEBAPP_PID=$!
    cd ..
fi

echo ""
echo "✅ HAASP is running!"
echo "📱 Main App: Qt6/Kirigami interface"
echo "🌐 Analytics: https://127.0.0.1:7420 (if Rust webapp built)"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo ""; echo "🛑 Stopping services..."; kill $HAASP_PID 2>/dev/null; kill $WEBAPP_PID 2>/dev/null; echo "👋 Goodbye!"; exit 0' INT

wait