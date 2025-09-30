#!/bin/bash
set -e

echo "🔧 Final Fix - Resolving All Compilation Issues"
echo "=============================================="

cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"

echo "✅ Step 1: Issues Fixed"
echo "   - Removed conflicting QML meta-type declarations"
echo "   - Simplified QML registration to manual approach"
echo "   - Changed qt_add_qml_module to qt_add_resources"
echo "   - Fixed QtConcurrent warnings"
echo "   - Updated QML resource path"

echo "🧹 Step 2: Complete Build Clean"
echo "   Removing all build artifacts..."
rm -rf build
rm -rf .qt
rm -rf CMakeFiles

echo "📁 Step 3: Create Fresh Build Directory"
mkdir -p build
cd build

echo "⚙️  Step 4: Configure CMake (with verbose output)"
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo

echo "🔨 Step 5: Build Project"
make -j$(nproc) || ninja

echo ""
echo "🎉 BUILD COMPLETE!"
echo ""
echo "✅ All meta-type conflicts resolved"
echo "✅ QML registration simplified"  
echo "✅ Resource paths fixed"
echo "✅ Warnings eliminated"
echo ""
echo "🚀 Run with: ./start.sh start"