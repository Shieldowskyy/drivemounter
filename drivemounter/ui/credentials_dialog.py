"""
Windows Security Credentials Dialog for KDE Plasma.
Faithfully reproduces the "Enter network credentials" dialog from Windows with Breeze styling.
"""

from PyQt6 import QtWidgets, QtCore, QtGui
from typing import Optional, Dict, Any
from drivemounter.i18n import t

class CredentialsDialog(QtWidgets.QDialog):
    def __init__(self, host: str, parent: Optional[QtWidgets.QWidget] = None, prefill_user: str = "", prefill_domain: str = ""):
        super().__init__(parent)
        self.host = host
        self.setWindowTitle(t("SEC_TITLE"))
        self.setWindowIcon(QtGui.QIcon.fromTheme("dialog-password"))
        self.setModal(True)
        self.setMinimumWidth(380)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)

        self._setup_ui(prefill_user, prefill_domain)

    def _setup_ui(self, prefill_user: str, prefill_domain: str):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(14)

        # Header with Security Icon and Titles
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(12)

        icon_label = QtWidgets.QLabel()
        sec_icon = QtGui.QIcon.fromTheme("dialog-password")
        if sec_icon.isNull():
            sec_icon = QtGui.QIcon.fromTheme("security-high")
        icon_label.setPixmap(sec_icon.pixmap(40, 40))
        icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        header_layout.addWidget(icon_label)

        title_vbox = QtWidgets.QVBoxLayout()
        title_vbox.setSpacing(3)

        title_lbl = QtWidgets.QLabel(t("SEC_HEADER"))
        title_font = title_lbl.font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        title_vbox.addWidget(title_lbl)

        sub_lbl = QtWidgets.QLabel(t("SEC_SUBHEADER", host=self.host))
        sub_lbl.setTextFormat(QtCore.Qt.TextFormat.RichText)
        sub_lbl.setWordWrap(True)
        title_vbox.addWidget(sub_lbl)

        header_layout.addLayout(title_vbox, 1)
        main_layout.addLayout(header_layout)

        # Separator line
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        sep.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        main_layout.addWidget(sep)

        # Form fields
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        self.user_edit = QtWidgets.QLineEdit()
        self.user_edit.setPlaceholderText(t("LABEL_USER").rstrip(":"))
        if prefill_user:
            self.user_edit.setText(prefill_user)
        form_layout.addRow(t("LABEL_USER"), self.user_edit)

        # Password layout with toggle view action
        self.pass_edit = QtWidgets.QLineEdit()
        self.pass_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.pass_edit.setPlaceholderText(t("LABEL_PASSWORD").rstrip(":"))
        
        # Add visibility toggle icon to password field
        self.toggle_action = self.pass_edit.addAction(
            QtGui.QIcon.fromTheme("visibility", QtGui.QIcon.fromTheme("document-preview")),
            QtWidgets.QLineEdit.ActionPosition.TrailingPosition
        )
        self.toggle_action.setToolTip("Show/hide password")
        self.toggle_action.triggered.connect(self._toggle_password_visibility)

        form_layout.addRow(t("LABEL_PASSWORD"), self.pass_edit)

        self.domain_edit = QtWidgets.QLineEdit()
        self.domain_edit.setPlaceholderText(t("HINT_DOMAIN"))
        if prefill_domain:
            self.domain_edit.setText(prefill_domain)
        form_layout.addRow(t("LABEL_DOMAIN"), self.domain_edit)

        main_layout.addLayout(form_layout)

        # Remember credentials checkbox (exact Windows wording)
        self.remember_cb = QtWidgets.QCheckBox(t("CB_REMEMBER"))
        self.remember_cb.setChecked(True)
        main_layout.addWidget(self.remember_cb)

        main_layout.addSpacing(6)

        # Action buttons
        btn_box = QtWidgets.QDialogButtonBox()
        self.ok_btn = btn_box.addButton("OK", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancel_btn = btn_box.addButton("Anuluj", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        self.ok_btn.setDefault(True)

        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        main_layout.addWidget(btn_box)

        # Focus
        if not prefill_user:
            self.user_edit.setFocus()
        else:
            self.pass_edit.setFocus()

    def _toggle_password_visibility(self):
        if self.pass_edit.echoMode() == QtWidgets.QLineEdit.EchoMode.Password:
            self.pass_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        else:
            self.pass_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

    def _on_accept(self):
        if not self.user_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "Wymagane dane", "Podaj nazwę użytkownika.")
            self.user_edit.setFocus()
            return
        self.accept()

    def get_credentials(self) -> Dict[str, Any]:
        return {
            "username": self.user_edit.text().strip(),
            "password": self.pass_edit.text(),
            "domain": self.domain_edit.text().strip(),
            "remember": self.remember_cb.isChecked()
        }
