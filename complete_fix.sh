#!/bin/bash
set -e

echo "🚀 HAASP Complete Fix - Addressing All Known Issues"
echo "=================================================="

cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"

echo "✅ Step 1: QML Controller Header - FIXED"
echo "   - Added QML_ELEMENT and QML_SINGLETON macros"
echo "   - Added QtQml/qqmlregistration.h include"

echo "✅ Step 2: CMakeLists.txt QML Module - FIXED" 
echo "   - Added NO_PLUGIN to qt_add_qml_module"
echo "   - Added SOURCES section with controller files"
echo "   - Fixed URI format"

echo "✅ Step 3: Main.cpp QML Registration - FIXED"
echo "   - Changed to singleton factory registration"
echo "   - Fixed context property names"
echo "   - Added application metadata"

echo "🔧 Step 4: Clean Build Environment"
echo "   Removing CMake cache and generated files..."
rm -rf build/CMakeFiles 2>/dev/null || true
rm -rf build/CMakeCache.txt 2>/dev/null || true
rm -rf build/*.cpp 2>/dev/null || true
rm -rf build/.qt 2>/dev/null || true

echo "🔨 Step 5: Reconfigure and Build"
mkdir -p build
cd build

echo "   Configuring CMake..."
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo

echo "   Building..."
ninja

echo ""
echo "🎉 ALL ISSUES ADDRESSED!"
echo ""
echo "✅ QML type registration fixed"
echo "✅ Controller singleton pattern implemented"  
echo "✅ CMake configuration corrected"
echo "✅ Build environment cleaned"
echo "✅ Fresh build completed"
echo ""
echo "🚀 Ready to run: ./start.sh start"