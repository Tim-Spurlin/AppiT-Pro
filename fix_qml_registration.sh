#!/bin/bash
set -e

cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"

echo "🔧 Fixing QML Type Registration Issues..."

echo "   Step 1: Clean CMake cache and generated files..."
rm -rf build/CMakeFiles/haasp_autogen 2>/dev/null || true
rm -rf build/haasp_qmltyperegistrations.cpp 2>/dev/null || true
rm -rf build/.qt 2>/dev/null || true
rm -rf build/meta_types 2>/dev/null || true
rm -rf build/CMakeCache.txt 2>/dev/null || true

echo "   Step 2: Reconfigure CMake..."
cd build
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_VERBOSE_MAKEFILE=ON

echo "   Step 3: Clean build..."
ninja clean 2>/dev/null || make clean 2>/dev/null || true

echo "   Step 4: Rebuild..."
ninja || make

echo "✅ QML Registration fix complete!"
echo "🚀 You can now run: ./start.sh start"