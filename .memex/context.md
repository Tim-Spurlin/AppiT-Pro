## HAASP Project Context and Conventions

### Project Overview
HAASP (Hyper-Advanced Associative Application Synthesis Platform) is a sophisticated QML-first application builder with integrated Git analytics and development intelligence. The system uses a hybrid architecture combining:
- **C++ Core**: High-performance nucleus with Git Service (libgit2) and Associative Nexus
- **QML UI**: Qt6-based visual interface with live preview and per-element editing  
- **Python ML**: Code intelligence and quality prediction agents (optional, Kafka-dependent)
- **Rust WebApp**: GitHub-like Insights++ analytics dashboard (local TLS server)

### Build System Patterns

#### CMake Configuration Requirements
The project uses CMake with specific patterns that must be followed:
- **Default Generator**: CMake generates Ninja build files (`build.ninja`) by default
- **Build Command**: Always use `ninja` not `make` unless explicitly configured for Makefiles
- **Generator Conflicts**: Must clean `CMakeCache.txt` when switching between generators
- **Resource System**: Use traditional `.qrc` files instead of `qt_add_resources` for reliability

#### Critical Build Dependencies
```bash
# Required system packages on Arch Linux:
- qt6-base, qt6-declarative, qt6-tools
- libgit2 (>=1.9.1)
- protobuf, grpc (via pkg-config)
- rust (>=1.70), cargo
- python (>=3.11) with venv support
```

#### Build Process Troubleshooting
- **"No targets specified"**: Indicates CMake generated Ninja but script uses `make`
- **QML Module Warnings**: Kirigami plugins missing is normal, doesn't block compilation
- **Meta-type Redefinition**: Remove conflicting `QML_DECLARE_TYPE` and `Q_DECLARE_METATYPE`
- **QtConcurrent Warnings**: Capture return values with `auto future = QtConcurrent::run(...); Q_UNUSED(future);`

### QML Architecture Patterns

#### Module Import Strategy
The project has evolved to use simplified Qt imports due to Kirigami dependency issues:
- **Avoid**: `org.kde.kirigami` imports (causes module not installed errors)
- **Use**: Standard Qt Quick components (`QtQuick.Controls 2.15`, `QtQuick.Layouts 1.15`)
- **Fallback Pattern**: Create simplified QML versions when complex modules fail
- **Resource Loading**: Multiple path fallback strategy (direct file → working dir → resources)

#### QML Resource Management
```qml
// Preferred resource structure:
<!DOCTYPE RCC>
<RCC version="1.0">
    <qresource prefix="/">
        <file alias="qml/Main.qml">src/ui/qml/Main.qml</file>
        <!-- Use alias for clear resource paths -->
    </qresource>
</RCC>
```

#### QML Registration Patterns
- **Avoid**: Automatic `QML_ELEMENT` registration (causes conflicts)
- **Use**: Manual singleton registration in main.cpp:
```cpp
qmlRegisterSingletonType<haasp::ui::Controller>(
    "org.haasp.ui", 1, 0, "Controller",
    [](QQmlEngine *, QJSEngine *) -> QObject * {
        return new haasp::ui::Controller();
    });
```

### Service Architecture Patterns

#### Optional Service Dependencies
The system is designed to gracefully handle missing external services:
- **Kafka**: Python ML pipeline has fallback standalone mode when Kafka unavailable
- **External APIs**: All integrations should have offline/local-only alternatives
- **Database Services**: Local-first approach with optional cloud sync

#### Service Startup Sequence
1. **C++ Core**: Always starts first, most reliable component
2. **Rust Analytics**: Stable, starts on port 7420 with TLS
3. **Python ML**: Optional, may fail with Kafka connection errors (graceful degradation)

### Development Workflow Patterns

#### Testing Strategy
- **C++ Components**: Build first, most reliable indicator of system health
- **QML Interface**: Test with simplified versions before complex Kirigami integration
- **Resource System**: Always test direct file loading before embedded resources
- **Service Integration**: Test components individually before full system integration

#### Debugging Approach
- **QML Loading Issues**: Use multiple path fallback with debug output
- **Build System Issues**: Check for generator mismatches (Ninja vs Make)
- **Module Dependencies**: Create simplified versions without external imports
- **Resource Problems**: Verify file paths and resource embedding separately

#### Error Recovery Patterns
- **CMake Issues**: Clean cache and regenerate when switching configurations
- **QML Module Errors**: Fall back to standard Qt components
- **Service Failures**: Continue with available components, log missing services
- **Resource Loading**: Always provide file-based fallbacks for embedded resources

### Code Organization

#### Hybrid Language Integration
- **C++ (Performance Core)**: State management, Git operations, threading with QtConcurrent
- **QML (UI Layer)**: Simplified Qt Quick components, avoid complex module dependencies
- **Python (ML Enhancement)**: Optional enrichment with graceful degradation when services unavailable
- **Rust (Analytics)**: Self-contained web service with local TLS, most stable component

#### File Structure Conventions
```
src/
├── nucleus/           # C++ core (always builds successfully)
├── ui/qml/           # QML files (use simplified versions for testing)
│   ├── Main.qml      # Complex version with Kirigami
│   └── SimpleMain.qml # Fallback version with standard Qt
└── main.cpp          # Multi-path QML loading with fallbacks

webapp/               # Rust analytics (builds reliably)
python/               # Optional ML pipeline (Kafka-dependent)
resources.qrc         # Traditional resource file (more reliable than qt_add_resources)
```

### Platform-Specific Considerations

#### Arch Linux with KDE/Qt6
- **Kirigami Installation**: May not be properly linked even when installed
- **Qt6 Version**: Using 6.9.2 with specific plugin warnings (normal)
- **Build Tools**: Ninja is default, preferred over Make for Qt6 projects
- **Missing Packages**: Vulkan headers not required for basic functionality

#### Development Environment (VS Code)
- **IDE**: Development is done in VS Code, NOT Qt Creator
- **Terminal Integration**: VS Code integrated terminal used for all builds and testing
- **CMake Integration**: Uses VS Code CMake extension and terminal commands
- **QML Development**: No Qt Creator designer - pure text editing in VS Code
- **Debugging**: Uses VS Code terminal output and console.log() in QML
- **Process Management**: Background services managed via VS Code terminal
- **Resource Paths**: Relative paths vary between development and build environments
- **Build Commands**: All executed through VS Code terminal, not IDE build system

This project represents a complex multi-language application with sophisticated fallback mechanisms designed to handle missing dependencies gracefully while maintaining core functionality.