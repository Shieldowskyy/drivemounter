# DriveMounter 🌐 (KDE Plasma)

A pixel-perfect 1:1 recreation of the classic Windows **Map Network Drive** wizard, built natively for **KDE Plasma** using **PyQt6** and the native **Breeze** design system.

Seamlessly mount remote network storage on Linux with the familiar Windows workflow: choose a drive letter (`Z:` to `D:`), enter the network path or browse, configure auto-reconnect on sign-in, and provide network credentials.

---

## 🌟 Key Features

- **1:1 Windows Map Network Drive Wizard Workflow:**
  - Exact layout, field order, keyboard shortcuts, and UX matching Windows.
  - Drive letter selector (`Z:` down to `D:`), prioritizing highest available letter.
  - Smart folder input supporting Windows UNC paths (`\\server\share`) as well as standard UNIX URIs.
  - **Browse...** button with live network scanning for SMB workgroups, servers, and shares.
  - **Reconnect at sign-in** checkbox via standard XDG Autostart.
  - **Connect using different credentials** checkbox prompting the exact **Windows Security** style modal.
  - **Connect to a Web site** link launching the WebDAV / Nextcloud / ownCloud connection wizard.
  - **Disconnect Drive...** button for direct management and unmounting of mapped shares.

- **KDE Plasma & Linux Native Integration:**
  - 100% native Qt6 Breeze styling, automatically inheriting active color scheme (Breeze Dark / Breeze Light).
  - Uses native KDE Breeze icons (`drive-network`, `network-server`, `media-eject`, `dialog-password`).
  - **KDE Dolphin Integration:** Mapped drives automatically appear in Dolphin's **Places** sidebar with the network drive icon.
  - **File System Access:** Every drive is mapped to `~/Network/<Letter>` (e.g., `~/Network/Z`), making it instantly accessible to Linux applications, CLI tools, Wine, and Steam Proton.
  - Native desktop notifications on mount/unmount via KDE notification daemon.

- **Full Protocol Support:**
  - **SMB / CIFS:** Windows Shares & Samba (user-space via GIO/GVfs or cifs-utils).
  - **NFS:** Network File System exports (`server:/export` or `nfs://server/export`).
  - **WebDAV:** Nextcloud, ownCloud, NAS WebDAV, or HTTP(S) servers (`https://.../dav`).

- **Multilingual Support (English Priority):**
  - English is the default and prioritized language, matching original Windows phrasing.
  - Polish localization is built-in and switchable via `--lang pl` or settings.

---

## 🚀 Getting Started

### Installation & Launcher Setup

```bash
# Clone or navigate to the repository
cd ~/Dokumenty/drivemounter

# Make launcher executable and link to ~/.local/bin
chmod +x bin/drivemounter
mkdir -p ~/.local/bin
ln -sf "$(pwd)/bin/drivemounter" ~/.local/bin/drivemounter

# Install KDE Application Menu (.desktop) entry
drivemounter --install-desktop
```

### Usage

```bash
# Launch the Map Network Drive wizard
drivemounter

# Open the Disconnect Network Drives dialog directly
drivemounter --disconnect

# Silent background remount (used automatically on user login)
drivemounter --remount

# Force Polish language (English is default)
drivemounter --lang pl
```

---

## 📂 Project Architecture

```
drivemounter/
├── bin/
│   └── drivemounter              # Shell launcher script
├── drivemounter/
│   ├── __init__.py
│   ├── app.py                    # Main application entry point & CLI handler
│   ├── config.py                 # Configuration, paths, stored mounts & settings
│   ├── i18n.py                   # Internationalization (EN primary / PL fallback)
│   ├── backend/
│   │   ├── autostart.py          # XDG Autostart login reconnection manager
│   │   ├── discovery.py          # SMB and network share scanner (smbtree/smbclient)
│   │   ├── dolphin_places.py     # KDE Dolphin places (user-places.xbel) integrator
│   │   ├── mounter.py            # Core mounting engine (SMB, NFS, WebDAV)
│   │   └── parser.py             # URL parser & validator (Windows UNC & URIs)
│   └── ui/
│       ├── browse_dialog.py      # "Browse for Folder" dialog
│       ├── credentials_dialog.py # Windows Security credentials dialog
│       ├── disconnect_dialog.py  # "Disconnect Network Drives" dialog
│       ├── map_drive_window.py   # Main 1:1 Map Network Drive wizard window
│       ├── styles.py             # KDE Breeze style configuration
│       └── web_location_dialog.py# WebDAV / Cloud storage wizard
├── tests/
│   └── test_drivemounter.py      # Automated unit tests
├── drivemounter.desktop          # XDG desktop shortcut
├── setup.py                      # Python packaging setup
└── README.md                     # Documentation
```

---

## 🔒 Security & Credentials

Network credentials are saved locally in `~/.config/drivemounter/credentials.json` with strict user-only permissions (`chmod 0600`). Alternatively, credentials are fed securely during the mount session.

---

## 🧪 Running Tests

```bash
python3 -m unittest discover -s tests -v
```

---

## 📄 License

MIT License. Free for personal and commercial use.
