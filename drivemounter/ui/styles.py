"""
Styling and theme helpers for DriveMounter on KDE Plasma.
Ensures 100% native KDE Breeze look & feel, correct font scaling, and color harmony.
"""

from PyQt6 import QtWidgets, QtGui, QtCore

def apply_kde_style(app: QtWidgets.QApplication):
    """Configures application with native Breeze style and icons."""
    # Ensure Breeze style is used if available
    available_styles = QtWidgets.QStyleFactory.keys()
    if "Breeze" in available_styles:
        app.setStyle("Breeze")
    elif "Fusion" in available_styles:
        app.setStyle("Fusion")

    # Set application fallback icon
    app_icon = QtGui.QIcon.fromTheme("drive-network")
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

def get_breeze_qss() -> str:
    """
    Subtle CSS enhancements that respect Breeze color palette.
    Keeps native QStyle controls while polishing spacing, headers, and hyperlinks.
    """
    return """
    QDialog, QMainWindow {
        /* Inherits native background from QPalette */
    }
    
    QLabel#headerInstruction {
        font-size: 10.5pt;
        line-height: 1.4;
    }

    QLabel#webStorageLink {
        color: palette(link);
        text-decoration: underline;
    }
    QLabel#webStorageLink:hover {
        color: palette(link-visited);
    }

    QGroupBox {
        font-weight: bold;
        margin-top: 6px;
        padding-top: 10px;
    }

    /* Polish buttons for Windows dialog rhythm */
    QPushButton {
        min-width: 78px;
        min-height: 25px;
        padding: 4px 12px;
    }

    QPushButton:default {
        font-weight: bold;
    }

    QComboBox {
        min-height: 25px;
    }

    QLineEdit {
        min-height: 25px;
    }
    """
