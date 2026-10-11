"""
URL and Path Parser for SMB, NFS, and WebDAV protocols.
Converts Windows-style paths (\\\\server\\share) and UNIX URIs into structured objects.
"""

import re
from typing import Tuple, Dict, Any, Optional
from urllib.parse import urlparse, unquote

class ShareParseError(Exception):
    pass

def parse_share_input(raw_input: str, forced_protocol: Optional[str] = None) -> Dict[str, Any]:
    """
    Parses user input string and detects the protocol, host, share/path, port, etc.
    Supports:
      - Windows UNC: \\\\server\\share\\path
      - SMB URI: smb://server/share/path
      - NFS: nfs://server/export or server:/export or /export@server
      - WebDAV: http://..., https://..., webdav://..., dav://..., davs://...
    """
    text = raw_input.strip()
    if not text:
        raise ShareParseError("Wprowadź ścieżkę do folderu sieciowego.")

    # 1. Check if Windows UNC format: \\server\share or //server/share
    if text.startswith(r"\\") or text.startswith("//"):
        cleaned = text.replace("/", "\\").lstrip("\\")
        parts = cleaned.split("\\", 1)
        host = parts[0]
        path = parts[1] if len(parts) > 1 else ""
        if not path:
            raise ShareParseError(f"Podaj nazwę udziału dla serwera '{host}' (np. \\\\{host}\\udzial).")
        
        # Standardize share name
        path_clean = path.replace("\\", "/").strip("/")
        return {
            "protocol": "smb",
            "host": host,
            "share": path_clean,
            "raw_input": text,
            "canonical_uri": f"smb://{host}/{path_clean}",
            "windows_unc": f"\\\\{host}\\{path.replace('/', chr(92))}",
            "display_name": f"{path_clean} on {host}"
        }

    # 2. Check if NFS with server:/path syntax (e.g. 192.168.1.50:/volume1/data or nas:/export)
    if ":" in text and not text.startswith(("http://", "https://", "smb://", "nfs://", "dav://", "davs://", "webdav://")):
        match = re.match(r"^([a-zA-Z0-9.\-_]+):(/.*)$", text)
        if match:
            host, path = match.groups()
            return {
                "protocol": "nfs",
                "host": host,
                "share": path,
                "raw_input": text,
                "canonical_uri": f"nfs://{host}{path}",
                "nfs_export": f"{host}:{path}",
                "display_name": f"{path} on {host} (NFS)"
            }

    # 3. Check URI schemes
    parsed = urlparse(text)
    scheme = parsed.scheme.lower() if parsed.scheme else ""

    if forced_protocol:
        forced = forced_protocol.lower()
        if forced in ["smb", "cifs"]:
            scheme = "smb"
        elif forced == "nfs":
            scheme = "nfs"
        elif forced in ["webdav", "dav", "davs"]:
            scheme = "davs" if scheme == "https" or scheme == "davs" else "dav"

    if scheme in ["smb", "cifs"]:
        host = parsed.hostname or ""
        port = parsed.port
        path = parsed.path.strip("/")
        if not host:
            raise ShareParseError("Nieprawidłowy adres serwera SMB.")
        if not path:
            raise ShareParseError(f"Podaj nazwę udziału dla serwera SMB '{host}'.")
        
        port_str = f":{port}" if port else ""
        return {
            "protocol": "smb",
            "host": host,
            "port": port,
            "share": path,
            "raw_input": text,
            "canonical_uri": f"smb://{host}{port_str}/{path}",
            "windows_unc": f"\\\\{host}\\{path.replace('/', chr(92))}",
            "display_name": f"{path} on {host}"
        }

    elif scheme == "nfs":
        host = parsed.hostname or ""
        path = parsed.path
        if not host:
            raise ShareParseError("Nieprawidłowy adres serwera NFS.")
        if not path.startswith("/"):
            path = "/" + path
        return {
            "protocol": "nfs",
            "host": host,
            "share": path,
            "raw_input": text,
            "canonical_uri": f"nfs://{host}{path}",
            "nfs_export": f"{host}:{path}",
            "display_name": f"{path} on {host} (NFS)"
        }

    elif scheme in ["webdav", "dav", "davs", "http", "https"]:
        host = parsed.hostname or ""
        port = parsed.port
        path = parsed.path
        if not host:
            raise ShareParseError("Nieprawidłowy adres serwera WebDAV.")
        
        is_ssl = scheme in ["https", "davs"] or (port == 443)
        dav_scheme = "davs" if is_ssl else "dav"
        http_scheme = "https" if is_ssl else "http"
        port_str = f":{port}" if port and port not in (80, 443) else ""
        
        canonical_uri = f"{dav_scheme}://{host}{port_str}{path}"
        http_url = f"{http_scheme}://{host}{port_str}{path}"

        return {
            "protocol": "webdav",
            "host": host,
            "port": port,
            "path": path,
            "is_ssl": is_ssl,
            "raw_input": text,
            "canonical_uri": canonical_uri,
            "http_url": http_url,
            "display_name": f"WebDAV ({host}{path})"
        }

    # If scheme was not recognized and didn't start with standard prefixes
    # Treat something like 'server/share' as SMB by default (user-friendly)
    if "/" in text and not text.startswith("/"):
        parts = text.split("/", 1)
        host = parts[0]
        share = parts[1].strip("/")
        return {
            "protocol": "smb",
            "host": host,
            "share": share,
            "raw_input": text,
            "canonical_uri": f"smb://{host}/{share}",
            "windows_unc": f"\\\\{host}\\{share.replace('/', chr(92))}",
            "display_name": f"{share} on {host}"
        }

    raise ShareParseError(
        "Nie rozpoznano formatu ścieżki. Użyj formatu:\n"
        "  • SMB: \\\\serwer\\udział lub smb://serwer/udział\n"
        "  • NFS: serwer:/eksport lub nfs://serwer/eksport\n"
        "  • WebDAV: https://serwer/dav lub davs://serwer/dav"
    )
