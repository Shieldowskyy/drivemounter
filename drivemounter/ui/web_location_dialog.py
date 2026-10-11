"""
Windows "Connect to a Web site" (Add Network Location) Dialog for WebDAV/Nextcloud on KDE Plasma.
"""

from PyQt6 import QtWidgets, QtCore, QtGui
from typing import Optional, Dict, Any
from drivemounter.config import WINDOWS_DRIVE_LETTERS, load_mounts
from drivemounter.i18n import t

class WebLocationDialog(QtWidgets.QDialog):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, suggested_letter: str = "Z:"):
        super().__init__(parent)
        self.setWindowTitle(t("WEB_TITLE"))
        self.setWindowIcon(QtGui.QIcon.fromTheme("folder-remote", QtGui.QIcon.fromTheme("drive-network")))
        self.resize(500, 420)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)

        self.suggested_letter = suggested_letter
        self.result_data: Optional[Dict[str, Any]] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        # Header banner
        header_hbox = QtWidgets.QHBoxLayout()
        header_hbox.setSpacing(12)

        icon_lbl = QtWidgets.QLabel()
        icon_lbl.setPixmap(QtGui.QIcon.fromTheme("network-workgroup").pixmap(40, 40))
        header_hbox.addWidget(icon_lbl)

        title_vbox = QtWidgets.QVBoxLayout()
        title_vbox.setSpacing(2)
        title_lbl = QtWidgets.QLabel(t("WEB_HEADER"))
        t_font = title_lbl.font()
        t_font.setPointSize(11)
        t_font.setBold(True)
        title_lbl.setFont(t_font)
        title_vbox.addWidget(title_lbl)

        sub_lbl = QtWidgets.QLabel(t("WEB_SUBHEADER"))
        sub_lbl.setWordWrap(True)
        title_vbox.addWidget(sub_lbl)
        header_hbox.addLayout(title_vbox, 1)

        layout.addLayout(header_hbox)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        sep.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        layout.addWidget(sep)

        # Type selector
        type_hbox = QtWidgets.QHBoxLayout()
        type_hbox.addWidget(QtWidgets.QLabel(t("WEB_SERVICE_TYPE")))
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems([
            "Standardowy WebDAV (https://...)",
            "Nextcloud (np. https://chmura.com/remote.php/dav/files/user/)",
            "ownCloud (np. https://chmura.com/remote.php/webdav/)",
            "Synology / QNAP WebDAV"
        ])
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_hbox.addWidget(self.type_combo, 1)
        layout.addLayout(type_hbox)

        # Form fields
        form = QtWidgets.QFormLayout()
        form.setSpacing(10)

        # Drive letter
        letter_box = QtWidgets.QHBoxLayout()
        self.letter_combo = QtWidgets.QComboBox()
        occupied = {m.get("letter", "").upper() for m in load_mounts()}
        for let in WINDOWS_DRIVE_LETTERS:
            if let in occupied:
                self.letter_combo.addItem(f"{let} (Zajęty)", let)
            else:
                self.letter_combo.addItem(f"{let}", let)
        
        idx = self.letter_combo.findData(self.suggested_letter)
        if idx >= 0:
            self.letter_combo.setCurrentIndex(idx)
        letter_box.addWidget(self.letter_combo)
        letter_box.addStretch(1)
        form.addRow("Dysk:", letter_box)

        # URL
        self.url_edit = QtWidgets.QLineEdit()
        self.url_edit.setPlaceholderText("https://serwer-webdav.pl/dav")
        form.addRow("Adres witryny:", self.url_edit)

        # Username
        self.user_edit = QtWidgets.QLineEdit()
        self.user_edit.setPlaceholderText("Użytkownik (jeśli wymagany)")
        form.addRow("Użytkownik:", self.user_edit)

        # Password
        self.pass_edit = QtWidgets.QLineEdit()
        self.pass_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.pass_edit.setPlaceholderText("Hasło lub hasło aplikacji (App Password)")
        form.addRow("Hasło:", self.pass_edit)

        layout.addLayout(form)

        # Checkboxes
        self.reconnect_cb = QtWidgets.QCheckBox("Połącz ponownie przy logowaniu")
        self.reconnect_cb.setChecked(True)
        layout.addWidget(self.reconnect_cb)

        self.remember_cb = QtWidgets.QCheckBox("Zapamiętaj moje poświadczenia")
        self.remember_cb.setChecked(True)
        layout.addWidget(self.remember_cb)

        layout.addStretch(1)

        # Buttons
        btn_box = QtWidgets.QDialogButtonBox()
        self.ok_btn = btn_box.addButton("Zakończ", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancel_btn = btn_box.addButton("Anuluj", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        self.ok_btn.setDefault(True)

        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _on_type_changed(self, index: int):
        if index == 1: # Nextcloud
            if not self.url_edit.text():
                self.url_edit.setText("https://mojanextcloud.pl/remote.php/dav/files/twoj_login/")
        elif index == 2: # ownCloud
            if not self.url_edit.text():
                self.url_edit.setText("https://mojowncloud.pl/remote.php/webdav/")

    def _on_accept(self):
        url = self.url_edit.text().strip()
        if not url:
            QtWidgets.QMessageBox.warning(self, "Błąd", "Wprowadź adres witryny WebDAV.")
            self.url_edit.setFocus()
            return
        
        if not url.startswith(("http://", "https://", "dav://", "davs://", "webdav://")):
            url = "https://" + url

        letter = self.letter_combo.currentData()
        self.result_data = {
            "url": url,
            "letter": letter,
            "username": self.user_edit.text().strip(),
            "password": self.pass_edit.text(),
            "reconnect": self.reconnect_cb.isChecked(),
            "remember": self.remember_cb.isChecked()
        }
        self.accept()
