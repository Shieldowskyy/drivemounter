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
    parser.add_argument("--install-desktop", action="store_true", help="Install desktop shortcut and Dolphin service menu")
    parser.add_argument("--uninstall", action="store_true", help="Remove desktop shortcuts, Dolphin service menus, and autostart")
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
        print("Installed desktop entry and Dolphin service menu.")
        sys.exit(0)

    # Handle desktop shortcuts removal
    if args.uninstall:
        uninstall_desktop_files()
        print("Removed desktop shortcuts and Dolphin service menus.")
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
Categories=Qt;KDE;System;Settings;Network;FileTools;
X-KDE-System-Settings-Parent-Category=network
X-KDE-Weight=70
StartupNotify=true
StartupWMClass=drivemounter
Keywords=drive;mount;network;samba;smb;nfs;webdav;share;cifs;knetattach;remote;
"""
    with open(target, "w", encoding="utf-8") as f:
        f.write(content)
    os.chmod(target, 0o755)

    # Install Dolphin Service Menu
    services_dir = Path.home() / ".local" / "share" / "kio" / "servicemenus"
    services_dir.mkdir(parents=True, exist_ok=True)
    service_target = services_dir / "drivemounter.desktop"
    service_content = f"""[Desktop Entry]
Type=Service
MimeType=inode/directory;all/allfiles;
Actions=mapNetworkDrive;disconnectNetworkDrive;
X-KDE-Submenu=Network Drives
X-KDE-Submenu[pl]=Dyski sieciowe
X-KDE-Priority=TopLevel

[Desktop Action mapNetworkDrive]
Name=Map Network Drive...
Name[pl]=Mapuj dysk sieciowy...
Icon=drive-network
Exec={exec_cmd}

[Desktop Action disconnectNetworkDrive]
Name=Disconnect Network Drive...
Name[pl]=Odłącz dysk sieciowy...
Icon=media-eject
Exec={exec_cmd} --disconnect
"""
    with open(service_target, "w", encoding="utf-8") as f:
        f.write(service_content)
    os.chmod(service_target, 0o755)

def uninstall_desktop_files():
    # 1. Desktop application shortcut
    app_desktop = Path.home() / ".local" / "share" / "applications" / "drivemounter.desktop"
    if app_desktop.exists():
        app_desktop.unlink()

    # 2. Dolphin service menu
    service_desktop = Path.home() / ".local" / "share" / "kio" / "servicemenus" / "drivemounter.desktop"
    if service_desktop.exists():
        service_desktop.unlink()

    # 3. Autostart shortcut
    autostart_file = Path.home() / ".config" / "autostart" / "drivemounter-autostart.desktop"
    if autostart_file.exists():
        autostart_file.unlink()

if __name__ == "__main__":
    main()
