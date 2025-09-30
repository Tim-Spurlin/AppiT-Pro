#!/bin/bash
set -e

echo "🔧 Testing C++ build..."
cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"
mkdir -p build && cd build
cmake .. -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
ninja
echo "✅ C++ build successful!"
cd ..

echo "🦀 Testing Rust webapp build..."
cd webapp
cargo check
echo "✅ Rust build successful!"

echo "🎉 All builds successful! Ready to run with './start.sh start'"