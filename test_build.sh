#!/bin/bash
set -e

echo "🚀 Testing HAASP Build..."
cd "/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro"

echo "🦀 Testing Rust webapp..."
cd webapp
echo "   Running cargo check..."
if cargo check; then
    echo "✅ Rust check passed!"
    echo "   Running cargo build..."
    if cargo build --release; then
        echo "✅ Rust build successful!"
    else
        echo "❌ Rust build failed"
        exit 1
    fi
else
    echo "❌ Rust check failed"
    exit 1
fi

echo "🎉 Build test complete! Try running with './start.sh start'"