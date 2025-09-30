#!/bin/bash
set -e

cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"

echo "🔧 Quick build test..."

# Build C++ components only
echo "   Building C++..."
mkdir -p build && cd build
cmake .. -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
ninja

echo "✅ C++ build successful!"

# Don't build Rust webapp for now to test C++ first
echo "🦀 Skipping Rust webapp for this test..."

echo "✅ Quick build complete! Ready to test C++ app."