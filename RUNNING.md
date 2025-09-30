# HAASP - Quick Start Guide

## 🚀 Running HAASP

### Option 1: Desktop Icon (Easiest)

- **Desktop Icon**: Double-click `HAASP.desktop` on your desktop
- **Applications Menu**: Search for "HAASP" in your applications menu

### Option 2: Command Line

```bash
# From the project directory
./start.sh start
```

### Option 3: Direct Executable

```bash
# Run just the main application (no services)
./build/haasp
```

## 📦 Installation Options

### User Installation (Recommended)

```bash
./install.sh
```

Installs to `~/.local/` for current user only.

### System Installation (Requires sudo)

```bash
sudo ./install.sh --system
```

Installs to `/opt/haasp` system-wide.

## 🔧 What HAASP Does

When you start HAASP, it automatically:

1. **Builds** the C++ application with Qt6/QML interface
2. **Compiles** the Rust analytics webapp
3. **Starts** the Python ML intelligence pipeline
4. **Launches** the main QML application window
5. **Opens** the web dashboard at <https://127.0.0.1:7420>

## 🛑 Stopping HAASP

- Press `Ctrl+C` in the terminal where you started it
- Or close the application window

## 📁 File Locations

- **Executable**: `build/haasp`
- **Desktop Icon**: `HAASP.desktop` (copy to desktop)
- **Icon**: `resources/haasp-icon.svg`
- **Scripts**: `start.sh`, `install.sh`

## ❓ Troubleshooting

If the desktop icon doesn't work:

1. Right-click the `.desktop` file
2. Go to Properties → Permissions
3. Check "Allow executing file as program"

If the application doesn't start:

1. Make sure you have Qt6 installed
2. Check that the build directory exists: `ls build/`
3. Try rebuilding: `./start.sh build`
