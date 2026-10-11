"""
Main Window: Windows "Map Network Drive" (Mapowanie dysku sieciowego) Clone for KDE Plasma.
1:1 visual fidelity and workflow of the Windows wizard, running natively with Qt6 Breeze.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

from PyQt6 import QtWidgets, QtCore, QtGui

from drivemounter.config import (
    WINDOWS_DRIVE_LETTERS, load_mounts, load_settings, save_settings,
    load_credential
)
from drivemounter.i18n import t
from drivemounter.backend.parser import parse_share_input, ShareParseError
from drivemounter.backend.mounter import mount_drive, MountError, AuthRequiredError
from drivemounter.ui.credentials_dialog import CredentialsDialog
from drivemounter.ui.browse_dialog import BrowseNetworkDialog
from drivemounter.ui.disconnect_dialog import DisconnectDialog
from drivemounter.ui.web_location_dialog import WebLocationDialog
from drivemounter.ui.styles import apply_kde_style, get_breeze_qss

class MountWorkerThread(QtCore.QThread):
    finished_success = QtCore.pyqtSignal(dict)
    failed = QtCore.pyqtSignal(str)
    auth_needed = QtCore.pyqtSignal()

    def __init__(
        self,
        letter: str,
        share_info: Dict[str, Any],
        reconnect: bool,
        username: Optional[str] = None,
        password: Optional[str] = None,
        domain: Optional[str] = None,
        remember: bool = False
    ):
        super().__init__()
        self.letter = letter
        self.share_info = share_info
        self.reconnect = reconnect
        self.username = username
        self.password = password
        self.domain = domain
        self.remember = remember

    def run(self):
        try:
            res = mount_drive(
                letter=self.letter,
                share_info=self.share_info,
                reconnect=self.reconnect,
                username=self.username,
                password=self.password,
                domain=self.domain,
                remember_creds=self.remember
            )
            self.finished_success.emit(res)
        except AuthRequiredError:
            self.auth_needed.emit()
        except MountError as e:
            self.failed.emit(str(e))
        except Exception as e:
            self.failed.emit(f"Wystąpił nieoczekiwany błąd: {e}")

class MapNetworkDriveWindow(QtWidgets.QDialog):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.settings = load_settings()
        self.mount_worker: Optional[MountWorkerThread] = None
        self.cached_credentials: Dict[str, Any] = {}

        self._init_window()
        self._setup_ui()
        self._populate_drives()
        self._update_linux_path_preview()

    def _init_window(self):
        self.setWindowTitle(t("MAIN_TITLE"))
        self.setWindowIcon(QtGui.QIcon.fromTheme("drive-network"))
        self.resize(540, 420)
        self.setMinimumSize(500, 390)
        self.setStyleSheet(get_breeze_qss())
        # Disable context help button in title bar (Windows/KDE style)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)

    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(12)

        # 1. Header instruction (Exact Windows prompt)
        self.header_label = QtWidgets.QLabel(t("HEADER_PROMPT"))
        self.header_label.setObjectName("headerInstruction")
        self.header_label.setWordWrap(True)
        main_layout.addWidget(self.header_label)

        main_layout.addSpacing(4)

        # 2. Main Form Grid (Drive and Folder rows)
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(12)

        # Row 0: Drive letter
        drive_lbl = QtWidgets.QLabel(t("LABEL_DRIVE"))
        drive_lbl.setFixedWidth(50)
        self.drive_combo = QtWidgets.QComboBox()
        self.drive_combo.setMinimumWidth(130)
        self.drive_combo.currentIndexChanged.connect(self._on_drive_changed)
        drive_lbl.setBuddy(self.drive_combo)

        drive_box = QtWidgets.QHBoxLayout()
        drive_box.addWidget(self.drive_combo)
        drive_box.addStretch(1)

        grid.addWidget(drive_lbl, 0, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        grid.addLayout(drive_box, 0, 1)

        # Row 1: Folder
        folder_lbl = QtWidgets.QLabel(t("LABEL_FOLDER"))
        folder_lbl.setFixedWidth(50)
        self.folder_combo = QtWidgets.QComboBox()
        self.folder_combo.setEditable(True)
        self.folder_combo.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.InsertAtTop)
        self.folder_combo.lineEdit().setPlaceholderText(t("PLACEHOLDER_FOLDER"))
        self.folder_combo.lineEdit().textChanged.connect(self._on_folder_text_changed)
        folder_lbl.setBuddy(self.folder_combo)

        # Load recent paths from history
        for path in self.settings.get("recent_paths", []):
            self.folder_combo.addItem(path)
        self.folder_combo.setEditText("")

        self.browse_btn = QtWidgets.QPushButton(t("BTN_BROWSE"))
        self.browse_btn.clicked.connect(self._on_browse_clicked)

        folder_box = QtWidgets.QHBoxLayout()
        folder_box.addWidget(self.folder_combo, 1)
        folder_box.addWidget(self.browse_btn)

        grid.addWidget(folder_lbl, 1, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        grid.addLayout(folder_box, 1, 1)

        main_layout.addLayout(grid)

        # Example helper text & detected protocol badge
        helper_box = QtWidgets.QHBoxLayout()
        helper_box.setContentsMargins(60, 0, 0, 0)
        
        self.example_label = QtWidgets.QLabel(t("EXAMPLE_TEXT"))
        self.example_label.setStyleSheet("color: palette(placeholder-text); font-size: 8.5pt;")
        helper_box.addWidget(self.example_label, 1)

        self.proto_badge = QtWidgets.QLabel("SMB / CIFS")
        self.proto_badge.setStyleSheet(
            "background-color: palette(alternate-base); border-radius: 4px; padding: 2px 6px; font-size: 8pt; font-weight: bold;"
        )
        self.proto_badge.setVisible(False)
        helper_box.addWidget(self.proto_badge)

        main_layout.addLayout(helper_box)

        main_layout.addSpacing(6)

        # 3. Checkboxes (Exact Windows order)
        cb_layout = QtWidgets.QVBoxLayout()
        cb_layout.setContentsMargins(60, 0, 0, 0)
        cb_layout.setSpacing(8)

        self.reconnect_cb = QtWidgets.QCheckBox(t("CB_RECONNECT"))
        self.reconnect_cb.setChecked(True)
        cb_layout.addWidget(self.reconnect_cb)

        self.diff_creds_cb = QtWidgets.QCheckBox(t("CB_DIFF_CREDS"))
        self.diff_creds_cb.setChecked(False)
        cb_layout.addWidget(self.diff_creds_cb)

        main_layout.addLayout(cb_layout)

        main_layout.addSpacing(6)

        # 4. Web storage link (Exact Windows location)
        link_box = QtWidgets.QHBoxLayout()
        link_box.setContentsMargins(60, 0, 0, 0)

        self.web_link = QtWidgets.QLabel(t("LINK_WEB"))
        self.web_link.setObjectName("webStorageLink")
        self.web_link.setWordWrap(True)
        self.web_link.linkActivated.connect(self._on_web_link_clicked)
        link_box.addWidget(self.web_link)
        main_layout.addLayout(link_box)

        # 5. Linux mount path indicator (Clean KDE integration)
        path_box = QtWidgets.QHBoxLayout()
        path_box.setContentsMargins(60, 0, 0, 0)
        self.linux_path_label = QtWidgets.QLabel(t("ACCESS_POINT"))
        self.linux_path_label.setStyleSheet("color: palette(placeholder-text); font-size: 8.5pt;")
        path_box.addWidget(self.linux_path_label)
        path_box.addStretch(1)
        main_layout.addLayout(path_box)

        # Status / Progress indicator
        self.status_msg_label = QtWidgets.QLabel("")
        self.status_msg_label.setStyleSheet("color: palette(highlight); font-weight: bold;")
        self.status_msg_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_msg_label.setVisible(False)
        main_layout.addWidget(self.status_msg_label)

        main_layout.addStretch(1)

        # Separator line
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        sep.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        main_layout.addWidget(sep)

        # 6. Bottom Button Bar (Exact Windows wizard button arrangement)
        btn_bar = QtWidgets.QHBoxLayout()
        btn_bar.setSpacing(8)

        # Left side: Disconnect drives
        self.disconnect_win_btn = QtWidgets.QPushButton(t("BTN_DISCONNECT"))
        self.disconnect_win_btn.setIcon(QtGui.QIcon.fromTheme("media-eject"))
        self.disconnect_win_btn.clicked.connect(self._on_disconnect_clicked)
        btn_bar.addWidget(self.disconnect_win_btn)

        btn_bar.addStretch(1)

        # Right side: Back, Finish, Cancel
        self.back_btn = QtWidgets.QPushButton(t("BTN_BACK"))
        self.back_btn.setEnabled(False)  # Disabled like in Windows on step 1
        btn_bar.addWidget(self.back_btn)

        self.finish_btn = QtWidgets.QPushButton(t("BTN_FINISH"))
        self.finish_btn.setDefault(True)
        self.finish_btn.setEnabled(False)
        self.finish_btn.clicked.connect(self._on_finish_clicked)
        btn_bar.addWidget(self.finish_btn)

        self.cancel_btn = QtWidgets.QPushButton(t("BTN_CANCEL"))
        self.cancel_btn.clicked.connect(self.reject)
        btn_bar.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_bar)

    def _populate_drives(self):
        self.drive_combo.clear()
        mounts = load_mounts()
        mapped_dict = {m.get("letter", "").upper(): m for m in mounts}

        first_free_idx = -1

        for idx, letter in enumerate(WINDOWS_DRIVE_LETTERS):
            if letter in mapped_dict:
                m = mapped_dict[letter]
                dest = m.get("windows_unc") or m.get("canonical_uri", "")
                self.drive_combo.addItem(QtGui.QIcon.fromTheme("drive-network"), f"{letter} ({dest})", letter)
            else:
                self.drive_combo.addItem(f"{letter}", letter)
                if first_free_idx == -1:
                    first_free_idx = idx

        if first_free_idx != -1:
            self.drive_combo.setCurrentIndex(first_free_idx)
        else:
            self.drive_combo.setCurrentIndex(0)

    def _on_drive_changed(self):
        self._update_linux_path_preview()

    def _update_linux_path_preview(self):
        letter = self.drive_combo.currentData() or "Z:"
        letter_clean = letter.rstrip(":")
        base_dir = self.settings.get("mount_base_dir", str(Path.home() / "Network"))
        full_path = os.path.join(base_dir, letter_clean)
        self.linux_path_label.setText(f"{t('ACCESS_POINT')} <b>{full_path}</b>")

    def _on_folder_text_changed(self, text: str):
        text_clean = text.strip()
        self.finish_btn.setEnabled(bool(text_clean))
        
        # Live protocol detection badge
        if text_clean:
            try:
                info = parse_share_input(text_clean)
                proto = info["protocol"].upper()
                if proto == "SMB":
                    self.proto_badge.setText("SMB / CIFS")
                elif proto == "NFS":
                    self.proto_badge.setText("NFS (Linux)")
                elif proto == "WEBDAV":
                    self.proto_badge.setText("WebDAV")
                self.proto_badge.setVisible(True)
            except Exception:
                self.proto_badge.setVisible(False)
        else:
            self.proto_badge.setVisible(False)

    def _on_browse_clicked(self):
        dialog = BrowseNetworkDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            selected = dialog.get_selected_path()
            if selected:
                self.folder_combo.setEditText(selected)
                self.finish_btn.setEnabled(True)

    def _on_web_link_clicked(self):
        letter = self.drive_combo.currentData() or "Z:"
        dialog = WebLocationDialog(self, suggested_letter=letter)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted and dialog.result_data:
            data = dialog.result_data
            self.folder_combo.setEditText(data["url"])
            idx = self.drive_combo.findData(data["letter"])
            if idx >= 0:
                self.drive_combo.setCurrentIndex(idx)
            self.reconnect_cb.setChecked(data["reconnect"])
            if data.get("username"):
                self.cached_credentials = {
                    "username": data["username"],
                    "password": data.get("password", ""),
                    "domain": "",
                    "remember": data.get("remember", True)
                }
            self.finish_btn.setEnabled(True)
            self._on_finish_clicked()

    def _on_disconnect_clicked(self):
        dialog = DisconnectDialog(self)
        dialog.exec()
        self._populate_drives()
        self._update_linux_path_preview()

    def _on_finish_clicked(self):
        folder_text = self.folder_combo.currentText().strip()
        if not folder_text:
            return

        try:
            share_info = parse_share_input(folder_text)
        except ShareParseError as e:
            QtWidgets.QMessageBox.critical(self, "Błąd ścieżki sieciowej", str(e))
            self.folder_combo.setFocus()
            return

        letter = self.drive_combo.currentData() or "Z:"
        reconnect = self.reconnect_cb.isChecked()
        diff_creds = self.diff_creds_cb.isChecked()

        # Save to recent paths
        recent = self.settings.get("recent_paths", [])
        if folder_text in recent:
            recent.remove(folder_text)
        recent.insert(0, folder_text)
        self.settings["recent_paths"] = recent[:10]
        save_settings(self.settings)

        # Check credentials requirement
        username = None
        password = None
        domain = None
        remember = False

        if self.cached_credentials:
            username = self.cached_credentials.get("username")
            password = self.cached_credentials.get("password")
            domain = self.cached_credentials.get("domain")
            remember = self.cached_credentials.get("remember", False)

        elif diff_creds:
            cred_dlg = CredentialsDialog(
                host=share_info["host"],
                parent=self
            )
            if cred_dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                return
            creds = cred_dlg.get_credentials()
            username = creds["username"]
            password = creds["password"]
            domain = creds["domain"]
            remember = creds["remember"]

        self._start_mount(letter, share_info, reconnect, username, password, domain, remember)

    def _start_mount(
        self,
        letter: str,
        share_info: Dict[str, Any],
        reconnect: bool,
        username: Optional[str],
        password: Optional[str],
        domain: Optional[str],
        remember: bool
    ):
        self._set_busy(True, f"Łączenie z {share_info.get('windows_unc') or share_info.get('canonical_uri')}...")

        self.current_mount_args = {
            "letter": letter,
            "share_info": share_info,
            "reconnect": reconnect,
            "remember": remember
        }

        self.mount_worker = MountWorkerThread(
            letter=letter,
            share_info=share_info,
            reconnect=reconnect,
            username=username,
            password=password,
            domain=domain,
            remember=remember
        )
        self.mount_worker.finished_success.connect(self._on_mount_success)
        self.mount_worker.auth_needed.connect(self._on_mount_auth_needed)
        self.mount_worker.failed.connect(self._on_mount_failed)
        self.mount_worker.start()

    def _on_mount_success(self, mount_entry: Dict[str, Any]):
        self._set_busy(False)
        letter = mount_entry.get("letter", "")
        local_path = mount_entry.get("local_path", "")

        # Open Dolphin file manager (just like Windows Explorer opens the drive upon finish)
        if self.settings.get("auto_open_dolphin", True) and local_path and os.path.exists(local_path):
            try:
                subprocess.Popen(["dolphin", local_path])
            except Exception:
                try:
                    subprocess.Popen(["xdg-open", local_path])
                except Exception:
                    pass

        self.accept()

    def _on_mount_auth_needed(self):
        self._set_busy(False)
        share_info = self.current_mount_args["share_info"]
        cred_dlg = CredentialsDialog(
            host=share_info["host"],
            parent=self
        )
        if cred_dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            creds = cred_dlg.get_credentials()
            self._start_mount(
                letter=self.current_mount_args["letter"],
                share_info=share_info,
                reconnect=self.current_mount_args["reconnect"],
                username=creds["username"],
                password=creds["password"],
                domain=creds["domain"],
                remember=creds["remember"]
            )

    def _on_mount_failed(self, error_msg: str):
        self._set_busy(False)
        QtWidgets.QMessageBox.critical(
            self,
            "Błąd połączenia z dyskiem sieciowym",
            f"Nie można nawiązać połączenia z zasobem sieciowym.\n\nSzczegóły błędu:\n{error_msg}"
        )

    def _set_busy(self, busy: bool, message: str = ""):
        self.finish_btn.setEnabled(not busy)
        self.browse_btn.setEnabled(not busy)
        self.folder_combo.setEnabled(not busy)
        self.drive_combo.setEnabled(not busy)
        self.reconnect_cb.setEnabled(not busy)
        self.diff_creds_cb.setEnabled(not busy)
        self.disconnect_win_btn.setEnabled(not busy)

        if busy:
            self.status_msg_label.setText(message)
            self.status_msg_label.setVisible(True)
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        else:
            self.status_msg_label.setVisible(False)
            QtWidgets.QApplication.restoreOverrideCursor()
