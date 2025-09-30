# HAASP Project AI Coding Instructions

## Project Overview
HAASP is a hybrid Qt6/QML visual application builder with Git integration, ML-powered enrichment, and Rust analytics. The architecture follows a three-tier model: C++/Qt6 core (GUI/editing), Python ML pipeline (Git intelligence), and Rust webapp (analytics dashboard).

## Build & Run Commands

### Quick Start (from project root `/home/tim-spurlin/Desktop/Developer Hub/Projects/2025/September/AppiT-Pro`):
```bash
./start.sh start  # Builds and starts all components
```

### Manual Build (from project root):
```bash
mkdir -p build && cd build
cmake .. -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
ninja
./haasp  # Run main application
```

## Key Architecture Patterns

### Component Communication
- **C++ ↔ QML**: Use `Q_PROPERTY` and `Q_INVOKABLE` in headers (see `src/core/`)
- **C++ ↔ Python**: gRPC services via protobuf (definitions in `proto/`)
- **C++ ↔ Rust**: REST API on port 7420 (see `webapp/src/main.rs`)
- **Git Operations**: libgit2 integration in `src/git/` - always use `GitManager` singleton

### File Organization
```
src/
├── core/         # Application state, QML engine setup
├── git/          # Git repository management (libgit2)
├── models/       # QAbstractItemModel implementations
├── qml/          # QML components - MUST follow Kirigami patterns
└── widgets/      # Custom Qt widgets

python/           # ML pipeline - sklearn/transformers
webapp/           # Rust analytics server - actix-web/tokio
```

## Critical Conventions

### QML Development
- **Always** use Kirigami components as base (import `org.kde.kirigami` 2.20)
- Register C++ types in `src/core/QmlEngine.cpp` using `qmlRegisterType`
- QML files in `resources/qml/` are auto-loaded via `qml.qrc`

### Git Integration
- Never directly use libgit2 - always go through `GitManager` class
- Repository operations are async - use signals: `repositoryOpened`, `commitCreated`
- Git portal state persists in `~/.config/HAASP/git_repos.json`

### Python ML Pipeline
- Enrichment models live in `python/enrichment_pipeline/`
- Communication via gRPC on port 50051
- Models auto-download on first run to `python/models/`

### Rust Analytics
- WebSocket updates on `/ws` endpoint
- GitHub-style activity visualization
- Metrics stored in-memory (no persistence by default)

## Testing & Debugging

### Enable QML Debugging (from `build/` directory):
```bash
export QML_DEBUG=1
export QSG_RENDER_TIMING=1
./haasp
```

### Test Python Pipeline (from `python/` directory):
```bash
source .venv/bin/activate
python -m pytest tests/
```

### Rust Server Dev Mode (from `webapp/` directory):
```bash
RUST_LOG=debug cargo run
```

## Common Pitfalls

1. **Missing QML module**: Ensure Qt6 declarative modules installed (`qt6-declarative-dev`)
2. **Git operations fail**: Check libgit2 version ≥1.9.1 required
3. **Python import errors**: Run `pip install -r python/requirements.txt` in venv
4. **Rust build fails**: Requires Rust 1.70+ with `cargo-watch` for dev

## Integration Points

- **Protobuf Changes**: Regenerate with `./scripts/generate_proto.sh`
- **New QML Component**: Register in `QmlEngine.cpp` AND add to `qml.qrc`
- **Database Schema**: Migrations in `sql/migrations/` - run sequentially
- **Config Files**: User settings in `~/.config/HAASP/`, system in `/etc/haasp/`

## Performance Considerations

- QML Inspector creates overhead - disable in production builds
- Python models cached for 24h (see `ModelCache` in `git_intelligence.py`)
- Rust server uses connection pooling - max 100 concurrent WebSockets
- Git operations batched - max 1000 commits per analysis cycle