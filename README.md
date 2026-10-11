# DriveMounter 🌐 – Native Windows "Map Network Drive" Wizard for Linux (KDE Plasma)

<p align="center">
  <a href="https://github.com/Shieldowskyy/drivemounter/actions/workflows/tests.yml"><img src="https://github.com/Shieldowskyy/drivemounter/actions/workflows/tests.yml/badge.svg" alt="Tests" /></a>
  <a href="https://github.com/Shieldowskyy/drivemounter/actions/workflows/package.yml"><img src="https://img.shields.io/badge/Packages-.deb%20%7C%20.rpm-blue" alt="Packages: .deb and .rpm" /></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.9+-3776AB.svg?logo=python&logoColor=white" alt="Python 3.9+" /></a>
  <a href="https://kde.org/"><img src="https://img.shields.io/badge/KDE-Plasma%206%20%2F%205-1D99F3.svg?logo=kde&logoColor=white" alt="KDE Plasma" /></a>
</p>

<p align="center">
  <strong>The easiest way to mount SMB, Samba, NFS, and WebDAV shares on Linux.</strong><br>
  A pixel-perfect, 1:1 recreation of the classic Windows <strong>Map Network Drive</strong> wizard, natively built for <strong>KDE Plasma</strong> with full <strong>Dolphin file manager</strong> and <strong>Breeze</strong> desktop integration.
</p>

---

## 📸 Screenshots

<p align="center">
  <img src="screenshot_main.png" alt="DriveMounter - Native Windows Map Network Drive GUI wizard on Linux KDE Plasma" width="540" />
</p>

<p align="center">
  <img src="screenshot_credentials.png" alt="Windows Security credentials prompt for Samba SMB share on KDE Plasma" width="380" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="screenshot_disconnect.png" alt="Disconnect network drives manager on KDE Dolphin Linux" width="460" />
</p>

---

## 🎯 Why DriveMounter?

Migrating from Windows to Linux or setting up a modern KDE Plasma workstation? 

* ❌ **No more editing `/etc/fstab`** or risking boot hangs on missing network connections.
* ❌ **No more cryptic terminal commands** (`sudo mount -t cifs -o username=...`).
* ❌ **No more broken path references in Wine / Proton**: Get predictable virtual drive letters (`Z:`, `Y:`, `X:`, down to `D:`) mapped directly to `~/Network/<Letter>`.
* ✅ **Familiar 1:1 Windows Workflow**: Enter `\\server\share`, pick your drive letter, check "Reconnect at sign-in", enter your credentials, and you're done.

---

## ⚖️ How DriveMounter Compares

| Feature | DriveMounter 🌐 | Standard KDE KNetAttach | `/etc/fstab` / Terminal | GIO / GVfs |
| :--- | :---: | :---: | :---: | :---: |
| **Familiar Windows 1:1 Wizard UX** | ✅ **Yes** | ❌ No | ❌ No | ❌ No |
| **Windows UNC Support (`\\server\share`)** | ✅ **Yes** | ❌ No | ❌ No | ⚠️ Partial |
| **Drive Letter Concept (`Z:` to `D:`)** | ✅ **Yes** | ❌ No | ❌ No | ❌ No |
| **Wine & Steam Proton Compatibility** | ✅ **Instant (`~/Network/Z`)** | ❌ Complex | ⚠️ Manual | ⚠️ Virtual URI |
| **Dolphin Places & Context Menu Integration** | ✅ **Native** | ⚠️ Places only | ❌ No | ⚠️ Places only |
| **Live SMB Server & Share Scanner** | ✅ **Built-in** | ❌ No | ❌ No | ⚠️ Basic |
| **KDE System Settings Registration** | ✅ **Native** | ❌ No | ❌ No | ❌ No |
| **Non-Root / User-Space Mounting** | ✅ **Yes** | ⚠️ Partial | ❌ Requires sudo | ✅ Yes |

---

## 🌟 Key Features

### 🪟 1:1 Windows Map Network Drive Wizard Workflow
- **Exact Layout & UX**: Replicates the original Windows wizard field order, keyboard shortcuts, and button behavior.
- **Drive Letter Assignment**: Select letters from `Z:` down to `D:` with intelligent allocation of the highest available letter.
- **Smart Path Recognition**: Accepts Windows UNC paths (`\\server\share\folder`) as well as standard UNIX URIs (`smb://...`, `nfs://...`, `https://.../dav`).
- **Live Network Discovery**: Click **Browse...** to automatically scan local SMB workgroups, servers, and published shares.
- **Auto-Reconnect on Sign-in**: Transparent login reconnection via standard XDG Autostart.
- **Windows Security Modal**: Authentic credentials dialog supporting usernames, passwords, and domains/workgroups.
- **Web Storage Location Wizard**: Built-in wizard for WebDAV, Nextcloud, and ownCloud connections.
- **Disconnect Drive Manager**: Manage, browse, and unmount mapped resources with a dedicated management window.

### 🐧 Deep KDE Plasma & Linux Desktop Integration
- **Breeze Design System**: 100% native Qt6/Qt5 Breeze styling that automatically adapts to **Breeze Dark**, **Breeze Light**, and custom color schemes.
- **KDE Dolphin Places Sidebar**: Mapped shares automatically appear in Dolphin's **Places** panel with native network drive icons (`drive-network`).
- **Dolphin Right-Click Context Menu**: Service menu integration allowing you to right-click anywhere in Dolphin to map or disconnect drives.
- **KDE System Settings**: Registered under the **Network** module in KDE System Settings and discoverable via **KRunner**.
- **Wine & Steam Proton Friendly**: Drives mount to `~/Network/<Letter>` (e.g., `~/Network/Z`), providing an accessible UNIX path for Windows games and software running under Wine.
- **Native Notifications**: Desktop feedback via the KDE notification daemon (`notify-send` / `kdialog`).

### 🌐 Comprehensive Protocol Support
- **SMB / CIFS**: Windows Shares, Samba, TrueNAS, Synology, QNAP, and Unraid servers.
- **NFS**: Network File System exports (`server:/export` or `nfs://server/export`).
- **WebDAV**: Nextcloud, ownCloud, NAS WebDAV, and secure HTTP(S) file servers.

### 🌍 Multilingual
- **English**: Default and prioritized, matching exact Windows terminology.
- **Polish (Polski)**: Built-in translation switchable via `drivemounter --lang pl`.

---

## 📦 System Dependencies

Ensure the required network utilities are installed on your distribution:

### Ubuntu / Debian / Linux Mint / Kubuntu
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip cifs-utils nfs-common davfs2 smbclient libnotify-bin
```

### Fedora / RHEL / AlmaLinux
```bash
sudo dnf install python3 python3-pip cifs-utils nfs-utils davfs2 samba-client libnotify
```

### Arch Linux / Manjaro / EndeavourOS
```bash
sudo pacman -S python python-pip cifs-utils nfs-utils davfs2 samba libnotify
```

---

## 🚀 Installation

### Option 1: Native Package Installation (Recommended)

#### Debian / Ubuntu / Kubuntu (`.deb`)
```bash
# Build locally or download from GitHub Releases:
./packaging/build_deb.sh
sudo apt install ./dist/drivemounter_1.0.0_all.deb
```

#### Fedora / RHEL (`.rpm`)
```bash
# Download the .rpm from GitHub Releases or install:
sudo dnf install ./dist/drivemounter-1.0.0-1.noarch.rpm
```

---

### Option 2: Automated Quick Install (with Python `venv`)

DriveMounter includes an automated `setup.sh` script that provisions an isolated virtual environment (`.venv`), installs dependencies, registers the desktop shortcut, and links the launcher:

```bash
# Clone the repository
git clone https://github.com/Shieldowskyy/drivemounter.git
cd drivemounter

# Run the automated setup
./setup.sh
```

---

### Option 3: Manual Installation

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies & package
pip install --upgrade pip
pip install -e .

# 3. Link launcher to ~/.local/bin
mkdir -p ~/.local/bin
ln -sf "$(pwd)/bin/drivemounter" ~/.local/bin/drivemounter

# 4. Install desktop shortcuts & Dolphin service menu
drivemounter --install-desktop
```

---

## 💡 Usage

```bash
# Launch the Map Network Drive wizard
drivemounter

# Open the Disconnect Network Drives manager directly
drivemounter --disconnect

# Silent background remount (used automatically on user login)
drivemounter --remount

# Switch UI language
drivemounter --lang en   # English (default)
drivemounter --lang pl   # Polish

# Remove desktop integrations
drivemounter --uninstall
```

### 🗑️ Uninstallation

To completely remove DriveMounter and all system shortcuts:

```bash
./uninstall.sh
```

---

## ❓ Frequently Asked Questions (FAQ)

### How does DriveMounter assign drive letters on Linux?
Linux uses a unified hierarchical file tree (`/`). DriveMounter maps your chosen letter (e.g., `Z:`) to a standardized, accessible local directory: `~/Network/Z`. This directory behaves identically to a mounted drive, making it instantly browsable in Dolphin, terminal, and file dialogs.

### Can I use mapped drives in Wine or Steam Proton?
Yes! Since the shares are mapped to fixed directories like `~/Network/Z`, you can effortlessly configure Wine (`winecfg`) to link the virtual Windows drive `Z:` to `~/Network/Z`. This is ideal for playing games or running Windows productivity apps with remote assets.

### Are my network passwords stored securely?
Yes. Stored network credentials are saved locally in `~/.config/drivemounter/credentials.json` with strict user-only permissions (`chmod 0600`), inaccessible to other users. You can also mount drives without saving credentials.

### Does DriveMounter reconnect on system reboot or login?
Yes. When the **"Reconnect at sign-in"** checkbox is selected, DriveMounter registers a background remount job via the standard XDG Autostart specification (`~/.config/autostart`), automatically mounting your shares upon login.

---

## 📂 Project Architecture

```
drivemounter/
├── bin/
│   └── drivemounter              # Smart shell launcher (auto-detects .venv)
├── drivemounter/
│   ├── __init__.py
│   ├── app.py                    # Application entry point & CLI handler
│   ├── config.py                 # Persistent settings & paths
│   ├── i18n.py                   # Internationalization (EN primary / PL fallback)
│   ├── backend/
│   │   ├── autostart.py          # XDG Autostart login reconnection manager
│   │   ├── discovery.py          # SMB network share scanner
│   │   ├── dolphin_places.py     # KDE Dolphin places (user-places.xbel) integrator
│   │   ├── mounter.py            # Mounting engine (SMB, NFS, WebDAV)
│   │   └── parser.py             # URL parser & validator (Windows UNC & URIs)
│   └── ui/
│       ├── browse_dialog.py      # "Browse for Folder" dialog
│       ├── credentials_dialog.py # Windows Security credentials dialog
│       ├── disconnect_dialog.py  # "Disconnect Network Drives" dialog
│       ├── map_drive_window.py   # Main 1:1 Map Network Drive wizard window
│       ├── styles.py             # KDE Breeze style configuration
│       └── web_location_dialog.py# WebDAV / Cloud storage wizard
├── packaging/
│   ├── build_deb.sh              # Debian / Ubuntu .deb package builder
│   └── drivemounter.spec         # Fedora / RHEL RPM package specification
├── tests/
│   └── test_drivemounter.py      # Automated unit tests
├── drivemounter.desktop          # XDG desktop shortcut (KDE Menu & System Settings)
├── drivemounter-service.desktop  # KDE Dolphin Service Menu (right-click actions)
├── setup.sh                      # Automated installer with .venv default
├── uninstall.sh                  # Interactive uninstaller script
├── setup.py                      # Python packaging script
├── pyproject.toml                # PEP 517/621 package configuration
├── requirements.txt              # Python requirements
├── LICENSE                       # MIT License
└── README.md                     # Documentation
```

---

## 🧪 Running Tests

```bash
python3 -m unittest discover -s tests -v
```

---

## ⭐ Support & Community

If you find DriveMounter helpful for migrating from Windows or managing network shares on Linux, **please give this repository a star on GitHub!** It helps other Linux and KDE users discover the project.

---

## 👤 Author

**Krzysztof (Shieldziak) Tarczyński**  
- GitHub: [@Shieldowskyy](https://github.com/Shieldowskyy)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
