# HAASP - Hyper-Advanced Associative Application Synthesis Platform

A QML-first application builder with integrated Git analytics and development intelligence.

## Architecture

HAASP combines:
- **C++ Core**: High-performance nucleus with Git Service (libgit2) and Associative Nexus  
- **QML UI**: Kirigami-based visual interface with live preview and editing
- **Python ML**: Code intelligence and quality prediction agents
- **Rust WebApp**: GitHub-like Insights++ analytics dashboard (local TLS)

## Key Features

- **Live QML Development**: Real-time preview and per-element editing
- **Git-Native Workflow**: Integrated repository management and analytics
- **Code Intelligence**: ML-driven quality prediction and change impact analysis  
- **Local-First**: No cloud dependencies, secure token storage via KWallet
- **Performance Optimized**: Hybrid C++/QML/Python with advanced threading

## Quick Start

```bash
# Clone repository
git clone <repo-url> haasp
cd haasp

# Build dependencies (Arch Linux)
sudo pacman -S qt6-base qt6-declarative qt6-quickcontrols2 libgit2 cmake ninja

# Build project
mkdir build && cd build
cmake .. -G Ninja
ninja

# Run HAASP
./bin/haasp
```

## Development

Built on Arch Linux with Zen kernel, KDE Plasma 6, Wayland.
See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions.

## License

MIT License - See LICENSE file