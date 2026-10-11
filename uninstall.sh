#!/usr/bin/env bash
# DriveMounter Uninstaller Script
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_TARGET="$HOME/.local/bin/drivemounter"
DESKTOP_TARGET="$HOME/.local/share/applications/drivemounter.desktop"
SERVICE_TARGET="$HOME/.local/share/kio/servicemenus/drivemounter.desktop"
AUTOSTART_TARGET="$HOME/.config/autostart/drivemounter-autostart.desktop"
CONFIG_DIR="$HOME/.config/drivemounter"
VENV_DIR="$PROJECT_DIR/.venv"

echo "=================================================="
echo " Uninstalling DriveMounter (KDE Plasma) "
echo "=================================================="

# 1. Remove launcher symlink
if [ -L "$BIN_TARGET" ] || [ -f "$BIN_TARGET" ]; then
    rm -f "$BIN_TARGET"
    echo "==> Removed launcher: $BIN_TARGET"
fi

# 2. Remove desktop shortcut
if [ -f "$DESKTOP_TARGET" ]; then
    rm -f "$DESKTOP_TARGET"
    echo "==> Removed application shortcut: $DESKTOP_TARGET"
fi

# 3. Remove Dolphin Service Menu
if [ -f "$SERVICE_TARGET" ]; then
    rm -f "$SERVICE_TARGET"
    echo "==> Removed Dolphin Service Menu: $SERVICE_TARGET"
fi

# 4. Remove Autostart entry
if [ -f "$AUTOSTART_TARGET" ]; then
    rm -f "$AUTOSTART_TARGET"
    echo "==> Removed autostart entry: $AUTOSTART_TARGET"
fi

# Refresh desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

# 5. Clean up .venv if requested
read -p "Do you also want to remove the Python virtual environment (.venv)? [y/N]: " REMOVE_VENV
if [[ "$REMOVE_VENV" =~ ^[Yy]$ ]]; then
    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
        echo "==> Removed .venv directory"
    fi
fi

# 6. Clean up user configuration and credentials
read -p "Do you want to purge user settings and saved credentials (~/.config/drivemounter)? [y/N]: " PURGE_CONFIG
if [[ "$PURGE_CONFIG" =~ ^[Yy]$ ]]; then
    if [ -d "$CONFIG_DIR" ]; then
        rm -rf "$CONFIG_DIR"
        echo "==> Purged configuration directory: $CONFIG_DIR"
    fi
fi

echo ""
echo "=================================================="
echo " DriveMounter has been completely uninstalled. "
echo "=================================================="
