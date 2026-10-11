"""
Mounter engine for SMB, NFS, and WebDAV on Linux / KDE Plasma.
Coordinates mounting via GIO / FUSE / pkexec, symlink creation, and Dolphin places registration.
"""

import os
import sys
import time
import shutil
import subprocess
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from drivemounter.config import (
    load_mounts, save_mounts, load_settings,
    save_credential, load_credential, remove_credential,
    WINDOWS_DRIVE_LETTERS
)
from drivemounter.backend.dolphin_places import add_place_to_dolphin, remove_place_from_dolphin
from drivemounter.backend.autostart import setup_autostart

class MountError(Exception):
    pass

class AuthRequiredError(MountError):
    pass

def get_gvfs_mount_path(protocol: str, host: str, share: str = "") -> Optional[str]:
    """Finds the local POSIX mount path in /run/user/<uid>/gvfs for a mounted share."""
    uid = os.getuid()
    gvfs_dir = Path(f"/run/user/{uid}/gvfs")
    if not gvfs_dir.exists():
        return None

    host_lower = host.lower()
    share_lower = share.lower()

    for item in gvfs_dir.iterdir():
        name_lower = item.name.lower()
        if protocol == "smb" and "smb-share" in name_lower:
            if f"server={host_lower}" in name_lower and (not share or f"share={share_lower}" in name_lower):
                return str(item)
        elif protocol == "webdav" and ("dav" in name_lower):
            if host_lower in name_lower:
                return str(item)

    # If exact match not found, check if only one entry exists or newly created
    return None

def mount_drive(
    letter: str,
    share_info: Dict[str, Any],
    reconnect: bool = True,
    username: Optional[str] = None,
    password: Optional[str] = None,
    domain: Optional[str] = None,
    remember_creds: bool = False
) -> Dict[str, Any]:
    """
    Mounts a remote share (SMB, NFS, WebDAV) to the specified Windows drive letter.
    """
    letter = letter.upper().rstrip(":")
    settings = load_settings()
    base_dir = Path(settings.get("mount_base_dir", Path.home() / "Network"))
    base_dir.mkdir(parents=True, exist_ok=True)

    mount_link_path = base_dir / letter
    protocol = share_info["protocol"]
    host = share_info["host"]
    share_name = share_info.get("share", "")
    
    # Check if we already have saved credentials for this host if none provided
    if not username and not password:
        saved_creds = load_credential(host)
        if saved_creds:
            username = saved_creds.get("username")
            password = saved_creds.get("password")
            domain = saved_creds.get("domain", "")

    # Clean existing link or directory if it was a dead link
    if mount_link_path.is_symlink() or mount_link_path.exists():
        try:
            if mount_link_path.is_symlink():
                mount_link_path.unlink()
            elif mount_link_path.is_dir() and not os.listdir(mount_link_path):
                mount_link_path.rmdir()
        except Exception:
            pass

    actual_target_path = None
    canonical_uri = share_info.get("canonical_uri", "")

    if protocol == "smb":
        actual_target_path = _mount_smb(
            host, share_name, username, password, domain, canonical_uri
        )
    elif protocol == "webdav":
        actual_target_path = _mount_webdav(
            share_info, username, password
        )
    elif protocol == "nfs":
        actual_target_path = _mount_nfs(
            share_info, mount_link_path
        )
    else:
        raise MountError(f"Nieobsługiwany protokół: {protocol}")

    # Create convenient symlink for the letter: ~/Network/Z -> actual target
    if actual_target_path and os.path.exists(actual_target_path):
        if str(actual_target_path) != str(mount_link_path):
            if mount_link_path.exists() or mount_link_path.is_symlink():
                try:
                    if mount_link_path.is_symlink():
                        mount_link_path.unlink()
                    else:
                        shutil.rmtree(mount_link_path)
                except Exception:
                    pass
            try:
                os.symlink(actual_target_path, mount_link_path)
            except Exception as e:
                print(f"Warning: could not create symlink at {mount_link_path}: {e}")
                mount_link_path = Path(actual_target_path)
    else:
        mount_link_path = Path(actual_target_path) if actual_target_path else mount_link_path

    # Save credentials if requested
    if remember_creds and username and password:
        save_credential(host, username, password, domain or "")

    # Save mount configuration
    display_name = share_info.get("display_name", f"{share_name} on {host}")
    mount_entry = {
        "letter": f"{letter}:",
        "protocol": protocol,
        "host": host,
        "share": share_name,
        "raw_input": share_info.get("raw_input", ""),
        "canonical_uri": canonical_uri,
        "windows_unc": share_info.get("windows_unc", ""),
        "local_path": str(mount_link_path),
        "actual_target": str(actual_target_path) if actual_target_path else str(mount_link_path),
        "display_name": display_name,
        "reconnect": reconnect,
        "mounted_at": time.time(),
        "has_credentials": bool(username)
    }

    mounts = [m for m in load_mounts() if m.get("letter", "").upper() != f"{letter}:"]
    mounts.append(mount_entry)
    save_mounts(mounts)

    # Add to Dolphin Places
    add_place_to_dolphin(letter, str(mount_link_path), display_name)

    # Setup autostart if reconnect requested
    has_any_reconnect = any(m.get("reconnect") for m in mounts)
    setup_autostart(has_any_reconnect)

    # Show native notification
    _send_notification(
        "Dysk sieciowy zmapowany",
        f"Pomyślnie podłączono {letter}: do {share_info.get('windows_unc') or canonical_uri}"
    )

    return mount_entry

def _mount_smb(
    host: str,
    share: str,
    username: Optional[str],
    password: Optional[str],
    domain: Optional[str],
    canonical_uri: str
) -> str:
    """Mounts SMB share via GIO or mount.cifs."""
    auth_str = ""
    if username:
        user_enc = urllib.parse.quote(username, safe="")
        pass_enc = f":{urllib.parse.quote(password, safe='')}" if password else ""
        dom_enc = f"{urllib.parse.quote(domain, safe='')};" if domain else ""
        auth_str = f"{dom_enc}{user_enc}{pass_enc}@"

    target_uri = f"smb://{auth_str}{host}/{share}"

    # Try mounting via gio mount
    cmd = ["gio", "mount", target_uri]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        err = proc.stderr.lower()
        if "już zamontowane" in err or "already mounted" in err:
            # Already mounted, continue to find path
            pass
        elif "uwierzytelnienie" in err or "authentication" in err or "odmowa dostępu" in err or "permission denied" in err:
            raise AuthRequiredError("Wymagane uwierzytelnienie lub niepoprawne hasło.")
        else:
            # If standard gio mount failed, try fallback
            clean_err = proc.stderr.strip() or proc.stdout.strip()
            raise MountError(f"Błąd montowania SMB: {clean_err}")

    # Wait briefly for GVfs to expose POSIX directory
    for _ in range(8):
        gvfs_path = get_gvfs_mount_path("smb", host, share)
        if gvfs_path and os.path.exists(gvfs_path):
            return gvfs_path
        time.sleep(0.25)

    # Fallback: check any matching gvfs folder
    uid = os.getuid()
    gvfs_dir = Path(f"/run/user/{uid}/gvfs")
    if gvfs_dir.exists():
        for p in gvfs_dir.iterdir():
            if "smb-share" in p.name.lower() and host.lower() in p.name.lower():
                return str(p)

    raise MountError(f"Udział SMB został zamontowany, ale nie odnaleziono ścieżki w GVFS.")

def _mount_webdav(
    share_info: Dict[str, Any],
    username: Optional[str],
    password: Optional[str]
) -> str:
    """Mounts WebDAV / Nextcloud share via GIO."""
    host = share_info["host"]
    port = share_info.get("port")
    path = share_info.get("path", "")
    is_ssl = share_info.get("is_ssl", False)
    scheme = "davs" if is_ssl else "dav"

    port_str = f":{port}" if port and port not in (80, 443) else ""
    auth_str = ""
    if username:
        user_enc = urllib.parse.quote(username, safe="")
        pass_enc = f":{urllib.parse.quote(password, safe='')}" if password else ""
        auth_str = f"{user_enc}{pass_enc}@"

    target_uri = f"{scheme}://{auth_str}{host}{port_str}{path}"

    cmd = ["gio", "mount", target_uri]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        err = proc.stderr.lower()
        if "już zamontowane" in err or "already mounted" in err:
            pass
        elif "uwierzytelnienie" in err or "authentication" in err or "odmowa dostępu" in err:
            raise AuthRequiredError("Wymagane uwierzytelnienie WebDAV.")
        else:
            raise MountError(f"Błąd montowania WebDAV: {proc.stderr.strip() or proc.stdout.strip()}")

    for _ in range(8):
        gvfs_path = get_gvfs_mount_path("webdav", host)
        if gvfs_path and os.path.exists(gvfs_path):
            return gvfs_path
        time.sleep(0.25)

    uid = os.getuid()
    gvfs_dir = Path(f"/run/user/{uid}/gvfs")
    if gvfs_dir.exists():
        for p in gvfs_dir.iterdir():
            if "dav" in p.name.lower() and host.lower() in p.name.lower():
                return str(p)

    raise MountError("Zasób WebDAV został zamontowany, ale nie odnaleziono ścieżki w GVFS.")

def _mount_nfs(share_info: Dict[str, Any], mount_dir: Path) -> str:
    """Mounts NFS export directly using pkexec mount or mount."""
    host = share_info["host"]
    export_path = share_info.get("share", "")
    nfs_target = f"{host}:{export_path}"

    mount_dir.mkdir(parents=True, exist_ok=True)

    # Use pkexec for elevated mount if needed
    cmd = ["pkexec", "mount", "-t", "nfs", "-o", "rw,soft,timeo=50", nfs_target, str(mount_dir)]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip()
        # Clean directory if mount failed
        try:
            if mount_dir.is_dir() and not os.listdir(mount_dir):
                mount_dir.rmdir()
        except Exception:
            pass
        raise MountError(f"Błąd montowania NFS ({nfs_target}): {err}")

    return str(mount_dir)

def unmount_drive(letter: str) -> bool:
    """
    Unmounts the specified drive letter, cleans symlinks, and removes from Dolphin places.
    """
    letter = letter.upper().rstrip(":")
    mounts = load_mounts()
    target_mount = None
    for m in mounts:
        if m.get("letter", "").upper().rstrip(":") == letter:
            target_mount = m
            break

    if not target_mount:
        # Check if local symlink exists anyway
        settings = load_settings()
        base_dir = Path(settings.get("mount_base_dir", Path.home() / "Network"))
        link_path = base_dir / letter
        if link_path.is_symlink() or link_path.exists():
            try:
                if link_path.is_symlink():
                    link_path.unlink()
            except Exception:
                pass
        remove_place_from_dolphin(letter)
        return True

    protocol = target_mount.get("protocol")
    local_path = target_mount.get("local_path")
    actual_target = target_mount.get("actual_target")
    canonical_uri = target_mount.get("canonical_uri")

    # Unmount using appropriate backend
    if protocol in ["smb", "webdav"]:
        if canonical_uri:
            subprocess.run(["gio", "mount", "-u", canonical_uri], capture_output=True)
        if actual_target and os.path.exists(actual_target):
            subprocess.run(["gio", "mount", "-u", actual_target], capture_output=True)
    elif protocol == "nfs":
        target_dir = local_path or actual_target
        if target_dir:
            res = subprocess.run(["umount", target_dir], capture_output=True)
            if res.returncode != 0:
                subprocess.run(["pkexec", "umount", target_dir], capture_output=True)

    # Remove symlink
    if local_path:
        p = Path(local_path)
        try:
            if p.is_symlink():
                p.unlink()
            elif p.is_dir() and not os.listdir(p):
                p.rmdir()
        except Exception:
            pass

    # Remove from Dolphin places
    remove_place_from_dolphin(letter)

    # Remove from saved mounts
    updated = [m for m in mounts if m.get("letter", "").upper().rstrip(":") != letter]
    save_mounts(updated)

    # Update autostart if no drives left with reconnect
    setup_autostart(any(m.get("reconnect") for m in updated))

    _send_notification(
        "Dysk sieciowy odłączony",
        f"Pomyślnie odłączono dysk {letter}:"
    )
    return True

def remount_all_drives() -> Tuple[int, int]:
    """
    Called upon login or --remount to reconnect all drives marked for reconnection.
    Returns (success_count, failure_count).
    """
    mounts = load_mounts()
    success = 0
    fail = 0

    for m in mounts:
        if not m.get("reconnect"):
            continue
        try:
            letter = m["letter"]
            share_info = {
                "protocol": m["protocol"],
                "host": m["host"],
                "share": m.get("share", ""),
                "canonical_uri": m.get("canonical_uri", ""),
                "windows_unc": m.get("windows_unc", ""),
                "display_name": m.get("display_name", "")
            }
            mount_drive(letter, share_info, reconnect=True)
            success += 1
        except Exception as e:
            print(f"Failed to remount {m.get('letter')}: {e}")
            fail += 1

    return success, fail

def _send_notification(title: str, text: str):
    """Sends desktop notification via notify-send or kdialog."""
    try:
        subprocess.run(
            ["notify-send", "-a", "DriveMounter", "-i", "drive-network", title, text],
            capture_output=True,
            timeout=2
        )
    except Exception:
        pass
