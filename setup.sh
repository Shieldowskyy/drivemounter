#!/usr/bin/env bash
# DriveMounter Setup Script (Automated Virtual Environment & Launcher Setup)
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
BIN_TARGET="$HOME/.local/bin"
DESKTOP_TARGET="$HOME/.local/share/applications"

echo "=================================================="
echo " Setting up DriveMounter (KDE Plasma) with venv "
echo "=================================================="

# 1. Create Python virtual environment (.venv)
if [ ! -d "$VENV_DIR" ]; then
    echo "==> Creating virtual environment in .venv..."
    python3 -m venv "$VENV_DIR"
else
    echo "==> Virtual environment already exists at $VENV_DIR"
fi

# 2. Upgrade pip and install package in editable mode
echo "==> Installing dependencies in venv..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -e "$PROJECT_DIR" --quiet

# 3. Ensure bin/drivemounter is executable
chmod +x "$PROJECT_DIR/bin/drivemounter"

# 4. Link launcher into ~/.local/bin
mkdir -p "$BIN_TARGET"
ln -sf "$PROJECT_DIR/bin/drivemounter" "$BIN_TARGET/drivemounter"
echo "==> Linked launcher to $BIN_TARGET/drivemounter"

# 5. Install Desktop entry (Application Menu & KDE System Settings)
mkdir -p "$DESKTOP_TARGET"
sed -e "s|^Exec=drivemounter|Exec=$BIN_TARGET/drivemounter|" "$PROJECT_DIR/drivemounter.desktop" > "$DESKTOP_TARGET/drivemounter.desktop"
chmod +x "$DESKTOP_TARGET/drivemounter.desktop"
echo "==> Installed desktop entry to $DESKTOP_TARGET/drivemounter.desktop"

# 6. Install KDE Dolphin Service Menu (Right-click context menu in Dolphin)
SERVICE_TARGET="$HOME/.local/share/kio/servicemenus"
mkdir -p "$SERVICE_TARGET"
sed -e "s|Exec=drivemounter|Exec=$BIN_TARGET/drivemounter|g" "$PROJECT_DIR/drivemounter-service.desktop" > "$SERVICE_TARGET/drivemounter.desktop"
chmod +x "$SERVICE_TARGET/drivemounter.desktop"
echo "==> Installed Dolphin Service Menu to $SERVICE_TARGET/drivemounter.desktop"

# Refresh desktop database if available
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_TARGET" 2>/dev/null || true
fi

echo ""
echo "=================================================="
echo " DriveMounter installed successfully! "
echo " You can now launch it via:"
echo "   - Application menu (Map Network Drive)"
echo "   - Terminal command: drivemounter"
echo "=================================================="
