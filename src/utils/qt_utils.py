from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QDesktopWidget

# Define constants for easier use
HORIZONTAL = Qt.Orientation.Horizontal
VERTICAL = Qt.Orientation.Vertical
YES = QMessageBox.StandardButton.Yes
NO = QMessageBox.StandardButton.No

def center_window(window):
    """Centers the given window on the screen."""
    screen = QDesktopWidget().screenGeometry()
    size = window.geometry()
    window.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
