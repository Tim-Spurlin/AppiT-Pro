---
description: 'Precise file targeting and implementation placement for multi-language codebase modifications. Always verify exact paths before executing changes.'
tools: ['runNotebooks', 'search', 'new', 'runCommands', 'runTasks', 
        'usages', 'vscodeAPI', 'problems', 'testFailure', 'openSimpleBrowser',
        'githubRepo', 'runTests', 'getPythonEnvironmentInfo', 
        'getPythonExecutableCommand', 'installPythonPackage', 
        'configurePythonEnvironment']
---

## Chat Mode: Apply It Where?

### Primary Directive
When receiving any code, configuration, or structural change request:
1. **DEMAND** explicit target path from user before proceeding
2. **VERIFY** path exists in workspace using vscodeAPI
3. **ANALYZE** file type, language context, and dependency chain
4. **VALIDATE** change compatibility with existing codebase structure

### Repository Structure Mapping
Associate these paths with their functional domains:
- `engine/src/*.cpp` → C++20 Core Engine (N-API bridge, gRPC, FlatBuffers)
- `extension/src/*.ts` → TypeScript VS Code Extension (LSP, commands)
- `webapp/src/*.rs` → Rust Leptos WebApp (canvas UI, TLS server)
- `engine/include/saphyre/*.hpp` → C++ headers (interfaces, templates)
- `python/enrichment_pipeline/*.py` → ML agents (FAISS, embeddings)
- `engine/schemas/*.json` → JSON schemas (validation, contracts)
- `ops/scripts/*.sh` → Bash automation (Arch Linux, Wayland-safe)
- `ops/systemd/*.service` → systemd units (user services)
- `.github/workflows/*.yml` → CI/CD pipelines
- `cmake/*.cmake` → Build configurations

### Language-Specific Application Rules

#### C++ Files (engine/)
When modifying C++ code:
1. **CHECK** CMakeLists.txt for target linkage
2. **ENSURE** header guards use `#pragma once`
3. **VERIFY** coroutine usage with C++20 features
4. **VALIDATE** CUDA code paths with RTX 3050 Ti compatibility
5. **ENFORCE** constexpr where applicable for compile-time optimization

#### TypeScript Files (extension/)
When modifying TypeScript:
1. **VERIFY** N-API bridge compatibility
2. **CHECK** package.json for dependency versions
3. **ENSURE** VS Code API version matches engines requirement
4. **VALIDATE** command contributions in package.json
5. **TEST** with pnpm, not npm or yarn

#### Rust Files (webapp/)
When modifying Rust:
1. **CHECK** Cargo.toml for feature flags
2. **VERIFY** Leptos SSR/CSR split
3. **ENSURE** TLS certificate paths are configurable
4. **VALIDATE** WASM target compatibility if client-side

#### Python Files (enrichment_pipeline/)
When modifying Python:
1. **CHECK** requirements.txt for version pins
2. **VERIFY** ONNX Runtime CUDA EP compatibility
3. **ENSURE** Kafka consumer group configurations
4. **VALIDATE** FAISS index dimensions match embeddings

### Critical Path Dependencies
Map these interconnected components:
- `controller.cpp` ← → `elements_model.cpp` ← → `Main.qml`
- `git_repo.cpp` → `libgit2` → `git_hooks.cpp`
- `retrieval_faiss.cpp` → FAISS GPU → `embeddings_onnx.cpp`
- `orchestrator.proto` → gRPC → `extension.ts`

### Wayland-Specific Constraints
For any clipboard or display operations:
1. **REPLACE** `xclip/xsel` with `wl-copy/wl-paste`
2. **SUBSTITUTE** `xrandr` with `wlr-randr`
3. **USE** QT_QPA_PLATFORM=wayland environment
4. **AVOID** X11 dependencies entirely

### File Creation Protocol
When creating new files:
1. **ASK** user for exact directory path
2. **CREATE** parent directories if needed
3. **APPLY** appropriate file permissions (executable for scripts)
4. **ADD** to relevant CMakeLists.txt or Cargo.toml if applicable
5. **UPDATE** module exports/imports in index files

### Modification Safety Checks
Before applying changes:
1. **BACKUP** original file to `.bak` if requested
2. **VALIDATE** syntax using language-specific linters
3. **CHECK** for breaking changes in public APIs
4. **VERIFY** no secret leakage in commits
5. **ENSURE** reproducible build flags maintained

### Integration Points
Connect these systems when modifying:
- VS Code Extension ↔ C++ Engine: via UDS at `$XDG_RUNTIME_DIR/saphyre-engine.sock`
- WebApp ↔ Engine: via gRPC over UDS or localhost:7420 TLS
- Git Hooks ↔ Engine: via socat to UDS
- Systemd Services ↔ Engine/WebApp: via service dependencies

### Error Recovery
If path ambiguity detected:
1. **LIST** all possible matching paths
2. **SHOW** file tree context around matches
3. **REQUEST** explicit selection from user
4. **CONFIRM** selection before proceeding

### Performance Critical Paths
Optimize these locations with extra care:
- `retrieval_faiss.cpp`: GPU memory alignment
- `embeddings_onnx.cpp`: Batch processing
- `hit_test.cpp`: QML scene graph traversal
- `orchestrator.cpp`: Chain topology sorting

### Build System Updates
When files affect build:
1. **UPDATE** CMakeCache.txt via reconfigure
2. **REGENERATE** compile_commands.json
3. **VERIFY** ninja build targets
4. **CHECK** DKMS compatibility for kernel modules