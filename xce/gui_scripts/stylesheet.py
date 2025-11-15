import os

from PyQt5 import QtGui, QtWidgets


def set_stylesheet(xce_object):
    # Use native OS theme for better compatibility with light/dark mode
    # Only apply minimal styling for layout and spacing

    icons_directory = os.path.join((os.getenv("XChemExplorer_DIR")), "xce/icons")

    # Minimal stylesheet that respects OS theme colors
    xce_object.setStyleSheet(
        """
    QPushButton {
    padding: 3px;
    }
    QTabBar::tab {
    padding: 3px;
    }
    QComboBox::down-arrow {
    image: url("""
        + icons_directory
        + """/drop-down.png);
    }
    """
    )

    # Use Fusion style which adapts well to both light and dark themes
    try:
        QtWidgets.QApplication.instance().setStyle("Fusion")
    except:
        # If Fusion not available, use default OS style
        pass
