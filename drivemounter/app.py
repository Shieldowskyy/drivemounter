"""
DriveMounter Main Application Entry Point.
A pixel-perfect Windows 'Map Network Drive' clone tailored natively for KDE Plasma.
"""

import sys
import os
import argparse
from pathlib import Path

from PyQt6 import QtWidgets, QtCore, QtGui

from drivemounter.ui.styles import apply_kde_style
from drivemounter.ui.map_drive_window import MapNetworkDriveWindow
from drivemounter.ui.disconnect_dialog import DisconnectDialog
from drivemounter.backend.mounter import remount_all_drives
from drivemounter.config import ensure_config_dirs

def main():
    parser = argparse.ArgumentParser(
        description="DriveMounter - Narzędzie do montowania dysków sieciowych (SMB, NFS, WebDAV) dla KDE Plasma"
    )
    parser.add_argument("--remount", action="store_true", help="Silent remount on login (autostart)")
    parser.add_argument("--disconnect", action="store_true", help="Open disconnect network drives window")
    parser.add_argument("--install-desktop", action="store_true", help="Install desktop shortcut into KDE application menu")
    parser.add_argument("--lang", choices=["en", "pl"], default=None, help="Force UI language (en=English, pl=Polish)")

    args = parser.parse_args()

    ensure_config_dirs()
    if args.lang:
        from drivemounter.config import load_settings, save_settings
        st = load_settings()
        st["language"] = args.lang
        save_settings(st)

    # Handle silent login remount
    if args.remount:
        success, fail = remount_all_drives()
        print(f"DriveMounter remount: {success} sukcesów, {fail} błędów.")
        sys.exit(0)

    # Handle desktop shortcut installation
    if args.install_desktop:
        install_desktop_file()
        print("Zainstalowano skrót w menu aplikacji KDE.")
        sys.exit(0)

    # Start GUI Application
    # Set desktop application properties for Wayland/X11 and KDE taskbar grouping
    QtCore.QCoreApplication.setApplicationName("drivemounter")
    QtCore.QCoreApplication.setApplicationVersion("1.0.0")
    QtCore.QCoreApplication.setOrganizationName("KDE")
    QtCore.QCoreApplication.setOrganizationDomain("kde.org")

    app = QtWidgets.QApplication(sys.argv)
    apply_kde_style(app)

    if args.disconnect:
        dlg = DisconnectDialog()
        dlg.show()
        sys.exit(app.exec())
    else:
        win = MapNetworkDriveWindow()
        win.show()
        sys.exit(app.exec())

def install_desktop_file():
    apps_dir = Path.home() / ".local" / "share" / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    target = apps_dir / "drivemounter.desktop"

    bin_path = Path.home() / ".local" / "bin" / "drivemounter"
    exec_cmd = str(bin_path) if bin_path.exists() else f"python3 {Path(__file__).resolve()}"

    content = f"""[Desktop Entry]
Type=Application
Name=Map Network Drive
Name[pl]=Mapuj dysk sieciowy
GenericName=Network Drive Mounter
GenericName[pl]=Narzędzie do mapowania dysków sieciowych
Comment=Mount SMB, NFS, and WebDAV network shares with a Windows-like wizard
Comment[pl]=Mapuj udziały sieciowe SMB, NFS oraz WebDAV za pomocą kreatora w stylu Windows
Exec={exec_cmd}
Icon=drive-network
Terminal=false
Categories=Qt;KDE;System;Network;FileTools;
StartupNotify=true
StartupWMClass=drivemounter
Keywords=drive;mount;network;samba;smb;nfs;webdav;share;cifs;
"""
    with open(target, "w", encoding="utf-8") as f:
        f.write(content)
    os.chmod(target, 0o755)

if __name__ == "__main__":
    main()
