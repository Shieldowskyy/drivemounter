"""
Configuration and constants for DriveMounter.
Handles paths, persistent settings, stored mounts, and credentials.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "drivemounter"
MOUNT_BASE_DIR = Path.home() / "Network"
MOUNTS_FILE = CONFIG_DIR / "mounts.json"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "mount_base_dir": str(MOUNT_BASE_DIR),
    "auto_open_dolphin": True,
    "notify_on_mount": True,
    "reconnect_delay_seconds": 2,
    "theme_mode": "native_breeze",
    "language": "auto"  # Automatically follows system language (e.g. Polish on pl_PL)
}

WINDOWS_DRIVE_LETTERS = [
    f"{chr(c)}:" for c in range(ord('Z'), ord('C'), -1)
]  # ['Z:', 'Y:', 'X:', ..., 'D:']

def ensure_config_dirs():
    """Ensure config and mount directories exist with appropriate permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    MOUNT_BASE_DIR.mkdir(parents=True, exist_ok=True)
    # Ensure credentials file will only be readable by user
    if not CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.touch(mode=0o600)
        with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    else:
        try:
            os.chmod(CREDENTIALS_FILE, 0o600)
        except Exception:
            pass

def load_settings() -> Dict[str, Any]:
    ensure_config_dirs()
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                res = DEFAULT_SETTINGS.copy()
                res.update(data)
                return res
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings: Dict[str, Any]):
    ensure_config_dirs()
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

def load_mounts() -> List[Dict[str, Any]]:
    ensure_config_dirs()
    if MOUNTS_FILE.exists():
        try:
            with open(MOUNTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_mounts(mounts: List[Dict[str, Any]]):
    ensure_config_dirs()
    with open(MOUNTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(mounts, f, indent=2, ensure_ascii=False)

def get_mount_for_letter(identifier: str) -> Optional[Dict[str, Any]]:
    clean_id = identifier.strip().rstrip(":")
    for m in load_mounts():
        m_let = m.get('letter', '').strip().rstrip(":")
        m_name = m.get('name', '').strip()
        if clean_id.lower() in (m_let.lower(), m_name.lower()):
            return m
    return None

def save_credential(host: str, username: str, password: str, domain: str = ""):
    ensure_config_dirs()
    data = {}
    if CREDENTIALS_FILE.exists():
        try:
            with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {}
    data[host.lower()] = {
        "username": username,
        "password": password,
        "domain": domain
    }
    with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    os.chmod(CREDENTIALS_FILE, 0o600)

def load_credential(host: str) -> Optional[Dict[str, str]]:
    ensure_config_dirs()
    if CREDENTIALS_FILE.exists():
        try:
            with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get(host.lower())
        except Exception:
            pass
    return None

def remove_credential(host: str):
    ensure_config_dirs()
    if CREDENTIALS_FILE.exists():
        try:
            with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if host.lower() in data:
                del data[host.lower()]
                with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                os.chmod(CREDENTIALS_FILE, 0o600)
        except Exception:
            pass
