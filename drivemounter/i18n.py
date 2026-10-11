"""
Internationalization (i18n) module for DriveMounter.
English is the primary and default language, matching the exact Windows phrases.
"""

from typing import Dict
from drivemounter.config import load_settings

STRINGS: Dict[str, Dict[str, str]] = {
    # Main Window
    "MAIN_TITLE": {
        "en": "Map Network Drive",
        "pl": "Mapowanie dysku sieciowego"
    },
    "HEADER_PROMPT": {
        "en": "Specify the drive letter for the connection and the folder that you want to connect to:",
        "pl": "Określ literę dysku dla połączenia i folder, z którym chcesz się połączyć:"
    },
    "LABEL_DRIVE": {
        "en": "D&rive:",
        "pl": "D&ysk:"
    },
    "LABEL_FOLDER": {
        "en": "&Folder:",
        "pl": "&Folder:"
    },
    "PLACEHOLDER_FOLDER": {
        "en": r"\\server\share",
        "pl": r"\\serwer\udział"
    },
    "BTN_BROWSE": {
        "en": "B&rowse...",
        "pl": "P&rzeglądaj..."
    },
    "EXAMPLE_TEXT": {
        "en": r"Example: \\server\share, smb://..., server:/export, https://.../dav",
        "pl": r"Przykład: \\serwer\udział, smb://..., serwer:/eksport, https://.../dav"
    },
    "CB_RECONNECT": {
        "en": "&Reconnect at sign-in",
        "pl": "Połącz &ponownie przy logowaniu"
    },
    "CB_DIFF_CREDS": {
        "en": "Connect using &different credentials",
        "pl": "Połącz przy &użyciu innych poświadczeń"
    },
    "LINK_WEB": {
        "en": '<a href="#web">Connect to a Web site that you can use to store your documents and pictures.</a>',
        "pl": '<a href="#web">Połącz z witryną sieci Web, której możesz używać do przechowywania dokumentów i obrazów.</a>'
    },
    "ACCESS_POINT": {
        "en": "Access point in KDE:",
        "pl": "Punkt dostępu w KDE:"
    },
    "BTN_DISCONNECT": {
        "en": "&Disconnect Drive...",
        "pl": "&Odłącz dysk..."
    },
    "BTN_BACK": {
        "en": "< &Back",
        "pl": "< &Wstecz"
    },
    "BTN_FINISH": {
        "en": "&Finish",
        "pl": "&Zakończ"
    },
    "BTN_CANCEL": {
        "en": "Cancel",
        "pl": "Anuluj"
    },
    "CONNECTING_MSG": {
        "en": "Connecting to {target}...",
        "pl": "Łączenie z {target}..."
    },

    # Credentials Dialog (Windows Security)
    "SEC_TITLE": {
        "en": "KDE Network Security",
        "pl": "Zabezpieczenia sieci KDE"
    },
    "SEC_HEADER": {
        "en": "Enter network credentials",
        "pl": "Wprowadź poświadczenia sieciowe"
    },
    "SEC_SUBHEADER": {
        "en": "Enter your credentials to connect to:<br><b>{host}</b>",
        "pl": "Wprowadź poświadczenia, aby połączyć się z:<br><b>{host}</b>"
    },
    "LABEL_USER": {
        "en": "User name:",
        "pl": "Nazwa użytkownika:"
    },
    "LABEL_PASSWORD": {
        "en": "Password:",
        "pl": "Hasło:"
    },
    "LABEL_DOMAIN": {
        "en": "Domain:",
        "pl": "Domena:"
    },
    "HINT_DOMAIN": {
        "en": "Optional domain or WORKGROUP",
        "pl": "Opcjonalna domena lub WORKGROUP"
    },
    "CB_REMEMBER": {
        "en": "Remember my credentials",
        "pl": "Zapamiętaj moje poświadczenia"
    },

    # Browse Dialog
    "BROWSE_TITLE": {
        "en": "Browse for Folder",
        "pl": "Przeglądanie w poszukiwaniu folderu sieciowego"
    },
    "BROWSE_HEADER": {
        "en": "Select a shared network folder or server to connect to:",
        "pl": "Wybierz udział sieciowy lub serwer, z którym chcesz nawiązać połączenie:"
    },
    "BROWSE_SCAN_BTN": {
        "en": "Scan Server",
        "pl": "Skanuj serwer"
    },
    "BROWSE_IP_PLACEHOLDER": {
        "en": "Enter server IP or hostname (e.g. 192.168.1.50 or my-nas)",
        "pl": "Wpisz IP serwera (np. 192.168.1.50 lub nazwa-nas)"
    },
    "ENTIRE_NETWORK": {
        "en": "Entire Network",
        "pl": "Cała sieć"
    },
    "SCANNING_MSG": {
        "en": "Searching for network resources...",
        "pl": "Wyszukiwanie zasobów sieciowych..."
    },
    "SCAN_DONE_MSG": {
        "en": "Ready.",
        "pl": "Gotowe."
    },
    "SCAN_NO_BROADCAST": {
        "en": "No SMB servers detected via broadcast (you can enter IP above).",
        "pl": "Nie wykryto serwerów SMB przez broadcast (możesz wpisać IP powyżej)."
    },

    # Disconnect Dialog
    "DISC_TITLE": {
        "en": "Disconnect Network Drives",
        "pl": "Odłączanie dysków sieciowych"
    },
    "DISC_HEADER": {
        "en": "Select the network drive(s) you want to disconnect:",
        "pl": "Wybierz dyski sieciowe, które chcesz odłączyć:"
    },
    "COL_DRIVE": {
        "en": "Drive",
        "pl": "Dysk"
    },
    "COL_NETWORK_PATH": {
        "en": "Network Path",
        "pl": "Ścieżka sieciowa"
    },
    "COL_PROTOCOL": {
        "en": "Protocol",
        "pl": "Protokół"
    },
    "COL_LOCAL_POINT": {
        "en": "Local Mount Point",
        "pl": "Punkt w systemie"
    },
    "BTN_DISCONNECT_ACT": {
        "en": "Disconnect",
        "pl": "Odłącz"
    },
    "BTN_DISCONNECT_ALL": {
        "en": "Disconnect All",
        "pl": "Odłącz wszystkie"
    },
    "BTN_OPEN_DOLPHIN": {
        "en": "Open in Dolphin",
        "pl": "Otwórz w Dolphin"
    },
    "BTN_CLOSE": {
        "en": "Close",
        "pl": "Zamknij"
    },
    "CONFIRM_DISCONNECT_ALL": {
        "en": "Are you sure you want to disconnect all ({count}) mapped network drives?",
        "pl": "Czy na pewno chcesz odłączyć wszystkie ({count}) zmapowane dyski sieciowe?"
    },

    # Web Location Dialog
    "WEB_TITLE": {
        "en": "Add Network Location Wizard",
        "pl": "Kreator połączenia z witryną sieci Web"
    },
    "WEB_HEADER": {
        "en": "Connect to a Web site or cloud storage",
        "pl": "Połącz z witryną sieci Web lub magazynem online"
    },
    "WEB_SUBHEADER": {
        "en": "You can connect to a WebDAV server, Nextcloud, ownCloud, or any HTTP(S) server.",
        "pl": "Możesz podłączyć serwer WebDAV, chmurę Nextcloud, ownCloud lub dowolny serwer HTTP(S)."
    },
    "WEB_SERVICE_TYPE": {
        "en": "Service type:",
        "pl": "Typ usługi:"
    },
    "WEB_URL": {
        "en": "Internet address:",
        "pl": "Adres witryny:"
    },

    # Notifications & Alerts
    "NOTIF_MOUNTED_TITLE": {
        "en": "Network Drive Mapped",
        "pl": "Dysk sieciowy zmapowany"
    },
    "NOTIF_MOUNTED_BODY": {
        "en": "Successfully mapped {letter} to {target}",
        "pl": "Pomyślnie podłączono {letter} do {target}"
    },
    "NOTIF_UNMOUNTED_TITLE": {
        "en": "Network Drive Disconnected",
        "pl": "Dysk sieciowy odłączony"
    },
    "NOTIF_UNMOUNTED_BODY": {
        "en": "Successfully disconnected drive {letter}",
        "pl": "Pomyślnie odłączono dysk {letter}"
    },
    "ERR_AUTH_NEEDED": {
        "en": "Authentication required or invalid password.",
        "pl": "Wymagane uwierzytelnienie lub niepoprawne hasło."
    },
    "ERR_CONNECT_TITLE": {
        "en": "Network Drive Connection Error",
        "pl": "Błąd połączenia z dyskiem sieciowym"
    },
    "ERR_CONNECT_BODY": {
        "en": "Unable to connect to the network resource.\n\nError details:\n{error}",
        "pl": "Nie można nawiązać połączenia z zasobem sieciowym.\n\nSzczegóły błędu:\n{error}"
    }
}

def t(key: str, **kwargs) -> str:
    """
    Translates key to target language. Defaults to English ('en').
    """
    settings = load_settings()
    lang = settings.get("language", "en")
    entry = STRINGS.get(key, {})
    text = entry.get(lang) or entry.get("en", key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
