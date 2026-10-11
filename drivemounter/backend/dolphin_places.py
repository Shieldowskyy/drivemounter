"""
Integration with KDE Dolphin Places (user-places.xbel).
Adds and removes mapped network drives to Dolphin's Places sidebar with native network drive icons.
"""

import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

XBEL_PATH = Path.home() / ".local" / "share" / "user-places.xbel"

def add_place_to_dolphin(letter: str, mount_path: str, display_name: str, icon_name: str = "drive-network") -> bool:
    """
    Adds a mapped network drive to KDE Dolphin's Places list.
    """
    letter = letter.upper().rstrip(":")
    tag_id = f"drivemounter-{letter}"
    href_url = f"file://{os.path.abspath(mount_path)}"
    title_text = f"{letter}: [{display_name}]"

    try:
        if not XBEL_PATH.exists():
            # Create basic structure if missing
            root = ET.Element("xbel", {
                "xmlns:bookmark": "http://www.freedesktop.org/standards/desktop-bookmarks",
                "xmlns:kdepriv": "http://www.kde.org/kdepriv",
                "xmlns:mime": "http://www.freedesktop.org/standards/shared-mime-info"
            })
            tree = ET.ElementTree(root)
        else:
            tree = ET.parse(XBEL_PATH)
            root = tree.getroot()

        # Check if item with this ID or href already exists, if so update it
        existing_bm = None
        for bm in root.findall("bookmark"):
            info = bm.find("info")
            if info is not None:
                for meta in info.findall("metadata"):
                    if meta.get("owner") == "http://www.kde.org":
                        id_elem = meta.find("ID")
                        if id_elem is not None and id_elem.text == tag_id:
                            existing_bm = bm
                            break
            if existing_bm:
                break

        if existing_bm is not None:
            # Update title and href
            existing_bm.set("href", href_url)
            t_elem = existing_bm.find("title")
            if t_elem is not None:
                t_elem.text = title_text
        else:
            # Create new bookmark element
            bm = ET.SubElement(root, "bookmark", {"href": href_url})
            t_elem = ET.SubElement(bm, "title")
            t_elem.text = title_text

            info = ET.SubElement(bm, "info")
            meta_fd = ET.SubElement(info, "metadata", {"owner": "http://freedesktop.org"})
            # Namespace bookmark:icon
            ET.SubElement(meta_fd, "{http://www.freedesktop.org/standards/desktop-bookmarks}icon", {"name": icon_name})

            meta_kde = ET.SubElement(info, "metadata", {"owner": "http://www.kde.org"})
            id_elem = ET.SubElement(meta_kde, "ID")
            id_elem.text = tag_id
            sys_elem = ET.SubElement(meta_kde, "isSystemItem")
            sys_elem.text = "false"

        ET.indent(tree, space=" ", level=0)
        tree.write(XBEL_PATH, encoding="UTF-8", xml_declaration=True)

        # Notify Dolphin / KIO via DBus if available
        notify_places_changed()
        return True

    except Exception as e:
        print(f"Error updating Dolphin places: {e}")
        return False

def remove_place_from_dolphin(letter: str) -> bool:
    """
    Removes a mapped network drive from KDE Dolphin's Places list.
    """
    letter = letter.upper().rstrip(":")
    tag_id = f"drivemounter-{letter}"

    if not XBEL_PATH.exists():
        return False

    try:
        tree = ET.parse(XBEL_PATH)
        root = tree.getroot()
        removed = False

        for bm in list(root.findall("bookmark")):
            info = bm.find("info")
            if info is not None:
                for meta in info.findall("metadata"):
                    if meta.get("owner") == "http://www.kde.org":
                        id_elem = meta.find("ID")
                        if id_elem is not None and id_elem.text == tag_id:
                            root.remove(bm)
                            removed = True
                            break

        if removed:
            ET.indent(tree, space=" ", level=0)
            tree.write(XBEL_PATH, encoding="UTF-8", xml_declaration=True)
            notify_places_changed()
            return True

    except Exception as e:
        print(f"Error removing from Dolphin places: {e}")
        return False

    return False

def notify_places_changed():
    """Trigger DBus notification to reload Places in running Dolphin instances."""
    try:
        subprocess.run(
            ["qdbus", "org.kde.dolphin", "/Places", "org.kde.KIO.Places.placesChanged"],
            capture_output=True,
            timeout=1
        )
    except Exception:
        pass
