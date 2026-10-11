"""
Network discovery helper for SMB and local servers.
Finds network computers and shares using smbtree, smbclient, and network tools.
"""

import subprocess
import re
from typing import List, Dict, Any, Optional

def scan_network_smb(timeout: int = 4) -> List[Dict[str, Any]]:
    """
    Scans the local network for SMB workgroups, servers, and shares using smbtree.
    Returns a tree structure:
    [
      {
        "workgroup": "WORKGROUP",
        "servers": [
          {
            "name": "NAS-SERVER",
            "comment": "Synology NAS",
            "shares": ["dane", "multimedia", "kopie"]
          }
        ]
      }
    ]
    """
    results: List[Dict[str, Any]] = []
    current_wg: Optional[Dict[str, Any]] = None
    current_server: Optional[Dict[str, Any]] = None

    try:
        proc = subprocess.run(
            ["smbtree", "-N"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = proc.stdout
    except Exception:
        output = ""

    if not output:
        return results

    # Parse smbtree hierarchical output:
    # WORKGROUP
    #     \\SERVER               Server description
    #         \\SERVER\IPC$          IPC Service
    #         \\SERVER\public        Public folder
    for line in output.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            continue

        indent = len(line) - len(line.lstrip())

        if indent == 0 and not line_stripped.startswith(r"\\"):
            # Workgroup name
            current_wg = {"workgroup": line_stripped, "servers": []}
            results.append(current_wg)
            current_server = None

        elif line_stripped.startswith(r"\\") and indent <= 6:
            # Server line: \\SERVER    description
            parts = line_stripped.split(None, 1)
            srv_raw = parts[0].lstrip(r"\\")
            srv_comment = parts[1] if len(parts) > 1 else ""
            
            if current_wg is None:
                current_wg = {"workgroup": "WORKGROUP", "servers": []}
                results.append(current_wg)

            current_server = {
                "name": srv_raw,
                "comment": srv_comment,
                "shares": []
            }
            current_wg["servers"].append(current_server)

        elif line_stripped.startswith(r"\\") and current_server is not None:
            # Share line: \\SERVER\share
            parts = line_stripped.split(None, 1)
            full_share = parts[0].lstrip(r"\\")
            if "\\" in full_share:
                _, share_name = full_share.split("\\", 1)
                # Ignore hidden admin shares like IPC$, ADMIN$, C$ by default, or keep them
                current_server["shares"].append(share_name)

    return results

def list_server_shares(host: str, username: Optional[str] = None, password: Optional[str] = None, timeout: int = 4) -> List[str]:
    """
    Queries a specific server for available SMB shares using smbclient -L.
    """
    shares: List[str] = []
    cmd = ["smbclient", "-L", host]
    
    if username and password:
        cmd.extend(["-U", f"{username}%{password}"])
    elif username:
        cmd.extend(["-U", username, "-N"])
    else:
        cmd.append("-N")

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = proc.stdout
    except Exception:
        return []

    # Parse Sharename Type Comment table from smbclient
    # Sharename       Type      Comment
    # ---------       ----      -------
    # public          Disk      Public Share
    in_shares = False
    for line in output.splitlines():
        if "Sharename" in line and "Type" in line:
            in_shares = True
            continue
        if in_shares:
            if line.startswith("---------") or not line.strip():
                if line.startswith("---------"):
                    continue
                else:
                    break
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1].lower() == "disk":
                shares.append(parts[0])

    return shares
