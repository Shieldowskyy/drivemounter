"""
Network Browse Dialog for DriveMounter.
Reproduces the Windows "Browse for Network Folder" dialog with native KDE Breeze tree view.
"""

from PyQt6 import QtWidgets, QtCore, QtGui
from typing import Optional, List, Dict, Any
from drivemounter.backend.discovery import scan_network_smb, list_server_shares
from drivemounter.i18n import t

class NetworkScanThread(QtCore.QThread):
    scan_finished = QtCore.pyqtSignal(list)

    def run(self):
        results = scan_network_smb(timeout=4)
        self.scan_finished.emit(results)

class ServerShareThread(QtCore.QThread):
    shares_found = QtCore.pyqtSignal(str, list)

    def __init__(self, host: str):
        super().__init__()
        self.host = host

    def run(self):
        shares = list_server_shares(self.host, timeout=3)
        self.shares_found.emit(self.host, shares)

class BrowseNetworkDialog(QtWidgets.QDialog):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, initial_selection: str = ""):
        super().__init__(parent)
        self.setWindowTitle(t("BROWSE_TITLE"))
        self.setWindowIcon(QtGui.QIcon.fromTheme("network-workgroup", QtGui.QIcon.fromTheme("drive-network")))
        self.resize(460, 480)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)

        self.selected_path: Optional[str] = None
        self._setup_ui()
        self._start_scan()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Header description
        info_label = QtWidgets.QLabel(t("BROWSE_HEADER"))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Quick Host / IP finder bar
        host_box = QtWidgets.QHBoxLayout()
        host_box.setSpacing(8)
        self.host_input = QtWidgets.QLineEdit()
        self.host_input.setPlaceholderText(t("BROWSE_IP_PLACEHOLDER"))
        host_box.addWidget(self.host_input, 1)

        find_btn = QtWidgets.QPushButton(t("BROWSE_SCAN_BTN"))
        find_btn.setIcon(QtGui.QIcon.fromTheme("edit-find"))
        find_btn.clicked.connect(self._query_custom_server)
        host_box.addWidget(find_btn)

        self.refresh_btn = QtWidgets.QPushButton()
        self.refresh_btn.setIcon(QtGui.QIcon.fromTheme("view-refresh"))
        self.refresh_btn.setToolTip("Odśwież całą sieć")
        self.refresh_btn.clicked.connect(self._start_scan)
        host_box.addWidget(self.refresh_btn)

        layout.addLayout(host_box)

        # Tree View of Network
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.tree, 1)

        # Status / Progress label
        self.status_label = QtWidgets.QLabel("Skanowanie sieci lokalnej...")
        self.status_label.setStyleSheet("color: palette(placeholder-text);")
        layout.addWidget(self.status_label)

        # Selected path display
        path_box = QtWidgets.QHBoxLayout()
        path_box.addWidget(QtWidgets.QLabel("Folder:"))
        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setPlaceholderText(r"\\serwer\udział")
        self.path_edit.textChanged.connect(self._on_path_edited)
        path_box.addWidget(self.path_edit, 1)
        layout.addLayout(path_box)

        # Button Box
        btn_box = QtWidgets.QDialogButtonBox()
        self.ok_btn = btn_box.addButton("OK", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancel_btn = btn_box.addButton("Anuluj", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        self.ok_btn.setEnabled(False)
        self.ok_btn.setDefault(True)

        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _start_scan(self):
        self.tree.clear()
        self.root_item = QtWidgets.QTreeWidgetItem(self.tree, ["Cała sieć"])
        self.root_item.setIcon(0, QtGui.QIcon.fromTheme("network-workgroup"))
        self.root_item.setExpanded(True)

        self.status_label.setText("Wyszukiwanie zasobów sieciowych...")
        self.refresh_btn.setEnabled(False)

        self.scan_thread = NetworkScanThread()
        self.scan_thread.scan_finished.connect(self._on_scan_finished)
        self.scan_thread.start()

    def _on_scan_finished(self, results: List[Dict[str, Any]]):
        self.refresh_btn.setEnabled(True)
        self.status_label.setText("Gotowe." if results else "Nie wykryto serwerów SMB przez broadcast (możesz wpisać IP powyżej).")

        for wg in results:
            wg_item = QtWidgets.QTreeWidgetItem(self.root_item, [wg["workgroup"]])
            wg_item.setIcon(0, QtGui.QIcon.fromTheme("network-workgroup"))
            wg_item.setExpanded(True)

            for srv in wg.get("servers", []):
                srv_name = srv["name"]
                comment = f" ({srv['comment']})" if srv.get("comment") else ""
                srv_item = QtWidgets.QTreeWidgetItem(wg_item, [f"{srv_name}{comment}"])
                srv_item.setIcon(0, QtGui.QIcon.fromTheme("network-server"))
                srv_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, {"type": "server", "host": srv_name})
                srv_item.setExpanded(True)

                for sh in srv.get("shares", []):
                    sh_item = QtWidgets.QTreeWidgetItem(srv_item, [sh])
                    sh_item.setIcon(0, QtGui.QIcon.fromTheme("folder-remote", QtGui.QIcon.fromTheme("folder")))
                    sh_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, {
                        "type": "share",
                        "host": srv_name,
                        "share": sh,
                        "path": f"\\\\{srv_name}\\{sh}"
                    })

    def _query_custom_server(self):
        host = self.host_input.text().strip().lstrip(r"\\").lstrip("//").split("/")[0].split("\\")[0]
        if not host:
            return
        
        self.status_label.setText(f"Sprawdzanie udziałów na {host}...")
        # Check if already in tree or add custom node
        srv_item = QtWidgets.QTreeWidgetItem(self.root_item, [f"{host} (Własny serwer)"])
        srv_item.setIcon(0, QtGui.QIcon.fromTheme("network-server"))
        srv_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, {"type": "server", "host": host})
        srv_item.setExpanded(True)
        self.tree.setCurrentItem(srv_item)

        self.server_thread = ServerShareThread(host)
        self.server_thread.shares_found.connect(lambda h, shares: self._on_server_shares_found(srv_item, h, shares))
        self.server_thread.start()

    def _on_server_shares_found(self, srv_item: QtWidgets.QTreeWidgetItem, host: str, shares: List[str]):
        if shares:
            for sh in shares:
                sh_item = QtWidgets.QTreeWidgetItem(srv_item, [sh])
                sh_item.setIcon(0, QtGui.QIcon.fromTheme("folder-remote"))
                sh_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, {
                    "type": "share",
                    "host": host,
                    "share": sh,
                    "path": f"\\\\{host}\\{sh}"
                })
            self.status_label.setText(f"Znaleziono {len(shares)} udziałów na {host}.")
        else:
            self.status_label.setText(f"Brak publicznych udziałów na {host} lub wymagane jest logowanie.")
            # Set default path anyway
            self.path_edit.setText(f"\\\\{host}\\")

    def _on_selection_changed(self):
        item = self.tree.currentItem()
        if not item:
            return
        data = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if isinstance(data, dict):
            if data.get("type") == "share":
                path = data.get("path", "")
                self.path_edit.setText(path)
                self.ok_btn.setEnabled(True)
            elif data.get("type") == "server":
                host = data.get("host", "")
                self.path_edit.setText(f"\\\\{host}\\")
                self.ok_btn.setEnabled(False)
        else:
            self.ok_btn.setEnabled(bool(self.path_edit.text().strip()))

    def _on_item_double_clicked(self, item: QtWidgets.QTreeWidgetItem):
        data = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if isinstance(data, dict) and data.get("type") == "share":
            self.accept()

    def _on_path_edited(self, text: str):
        self.ok_btn.setEnabled(bool(text.strip()))

    def get_selected_path(self) -> str:
        return self.path_edit.text().strip()
