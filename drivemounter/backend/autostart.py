"""
Autostart manager for Reconnect at sign-in functionality.
Installs an XDG Autostart entry that runs DriveMounter in remount mode upon user login.
"""

import os
import sys
from pathlib import Path

AUTOSTART_DIR = Path.home() / ".config" / "autostart"
AUTOSTART_FILE = AUTOSTART_DIR / "drivemounter-autostart.desktop"

def get_launcher_cmd() -> str:
    """Returns command line to execute remount."""
    local_bin = Path.home() / ".local" / "bin" / "drivemounter"
    if local_bin.exists():
        return f"{local_bin} --remount"
    
    # Fallback to python execution of module
    module_dir = Path(__file__).resolve().parent.parent.parent
    return f"python3 -m drivemounter.app --remount"

def setup_autostart(enabled: bool = True):
    """Creates or updates the autostart .desktop file."""
    if not enabled:
        if AUTOSTART_FILE.exists():
            try:
                AUTOSTART_FILE.unlink()
            except Exception:
                pass
        return

    AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)
    cmd = get_launcher_cmd()

    content = f"""[Desktop Entry]
Type=Application
Name=DriveMounter Autostart
Comment=Automatyczne podłączanie dysków sieciowych przy logowaniu (KDE Plasma)
Exec={cmd}
Icon=drive-network
Terminal=false
Categories=System;Utility;
X-KDE-autostart-phase=2
StartupNotify=false
"""
    try:
        with open(AUTOSTART_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(AUTOSTART_FILE, 0o755)
    except Exception as e:
        print(f"Error writing autostart file: {e}")

def is_autostart_enabled() -> bool:
    return AUTOSTART_FILE.exists()
