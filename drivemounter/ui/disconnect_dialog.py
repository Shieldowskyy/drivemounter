"""
Windows-style Disconnect Network Drive Dialog for KDE Plasma.
Provides direct management and unmounting of mapped drives.
"""

import subprocess
from pathlib import Path
from PyQt6 import QtWidgets, QtCore, QtGui
from typing import Optional

from drivemounter.config import load_mounts
from drivemounter.backend.mounter import unmount_drive
from drivemounter.i18n import t

class DisconnectDialog(QtWidgets.QDialog):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(t("DISC_TITLE"))
        self.setWindowIcon(QtGui.QIcon.fromTheme("media-eject", QtGui.QIcon.fromTheme("drive-network")))
        self.resize(620, 360)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)

        self._setup_ui()
        self.refresh_list()

    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(10)

        # Header instruction
        header = QtWidgets.QLabel(t("DISC_HEADER"))
        main_layout.addWidget(header)

        # Content layout with Table and Buttons
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setSpacing(12)

        # Table of mapped drives
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            t("COL_DRIVE"),
            t("COL_NETWORK_PATH"),
            t("COL_PROTOCOL"),
            t("COL_LOCAL_POINT")
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        content_layout.addWidget(self.table, 1)

        # Action Buttons on right side (Classic Windows layout)
        btn_vbox = QtWidgets.QVBoxLayout()
        btn_vbox.setSpacing(8)

        self.disconnect_btn = QtWidgets.QPushButton(t("BTN_DISCONNECT_ACT"))
        self.disconnect_btn.setDefault(True)
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.setIcon(QtGui.QIcon.fromTheme("media-eject"))
        self.disconnect_btn.clicked.connect(self._disconnect_selected)
        btn_vbox.addWidget(self.disconnect_btn)

        self.disconnect_all_btn = QtWidgets.QPushButton(t("BTN_DISCONNECT_ALL"))
        self.disconnect_all_btn.setIcon(QtGui.QIcon.fromTheme("edit-delete"))
        self.disconnect_all_btn.clicked.connect(self._disconnect_all)
        btn_vbox.addWidget(self.disconnect_all_btn)

        self.open_dolphin_btn = QtWidgets.QPushButton(t("BTN_OPEN_DOLPHIN"))
        self.open_dolphin_btn.setIcon(QtGui.QIcon.fromTheme("system-file-manager"))
        self.open_dolphin_btn.setEnabled(False)
        self.open_dolphin_btn.clicked.connect(self._open_selected_in_dolphin)
        btn_vbox.addWidget(self.open_dolphin_btn)

        btn_vbox.addStretch(1)

        self.close_btn = QtWidgets.QPushButton(t("BTN_CLOSE"))
        self.close_btn.clicked.connect(self.accept)
        btn_vbox.addWidget(self.close_btn)

        content_layout.addLayout(btn_vbox)
        main_layout.addLayout(content_layout)

    def refresh_list(self):
        mounts = load_mounts()
        self.table.setRowCount(len(mounts))

        for row, m in enumerate(mounts):
            display_id = m.get("name") or m.get("letter", "")
            unc = m.get("windows_unc") or m.get("canonical_uri", "")
            proto = m.get("protocol", "").upper()
            local_path = m.get("local_path", "")

            item_letter = QtWidgets.QTableWidgetItem(display_id)
            item_letter.setIcon(QtGui.QIcon.fromTheme("drive-network", QtGui.QIcon.fromTheme("folder-network")))
            item_letter.setData(QtCore.Qt.ItemDataRole.UserRole, m)

            item_unc = QtWidgets.QTableWidgetItem(unc)
            item_proto = QtWidgets.QTableWidgetItem(proto)
            item_local = QtWidgets.QTableWidgetItem(local_path)

            self.table.setItem(row, 0, item_letter)
            self.table.setItem(row, 1, item_unc)
            self.table.setItem(row, 2, item_proto)
            self.table.setItem(row, 3, item_local)

        self.table.resizeColumnsToContents()
        self.disconnect_all_btn.setEnabled(len(mounts) > 0)
        self._on_selection_changed()

    def _on_selection_changed(self):
        selected_rows = len(self.table.selectionModel().selectedRows())
        self.disconnect_btn.setEnabled(selected_rows > 0)
        self.open_dolphin_btn.setEnabled(selected_rows == 1)

    def _disconnect_selected(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return

        for index in selected:
            row = index.row()
            item = self.table.item(row, 0)
            if item:
                m = item.data(QtCore.Qt.ItemDataRole.UserRole)
                if m:
                    identifier = m.get("name") or m.get("letter", "")
                    unmount_drive(identifier)

        self.refresh_list()

    def _disconnect_all(self):
        mounts = load_mounts()
        if not mounts:
            return

        confirm = QtWidgets.QMessageBox.question(
            self,
            t("DISC_TITLE"),
            t("CONFIRM_DISCONNECT_ALL", count=len(mounts)),
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            for m in mounts:
                identifier = m.get("name") or m.get("letter", "")
                unmount_drive(identifier)
            self.refresh_list()

    def _open_selected_in_dolphin(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        row = selected[0].row()
        item = self.table.item(row, 0)
        if item:
            m = item.data(QtCore.Qt.ItemDataRole.UserRole)
            local_path = m.get("local_path")
            if local_path and Path(local_path).exists():
                try:
                    subprocess.Popen(["dolphin", local_path])
                except Exception:
                    subprocess.Popen(["xdg-open", local_path])
