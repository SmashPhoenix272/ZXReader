from PyQt5.QtWidgets import QWidget
from typing import Optional
from PyQt5.QtGui import QFont

class StyleManager:
    def __init__(self) -> None:
        self.current_theme = "light"

    def get_style(self) -> str:
        if self.current_theme == "light":
            return """
                QMainWindow {
                    background-color: #f0f0f0;
                }
                QWidget {
                    background-color: #f0f0f0;
                    color: #333;
                }
                QMenuBar {
                    background-color: #e0e0e0;
                    color: #333;
                }
                QMenuBar::item {
                    background-color: #e0e0e0;
                    color: #333;
                }
                QMenuBar::item::selected {
                    background-color: #d0d0d0;
                }
                QMenu {
                    background-color: #e0e0e0;
                    color: #333;
                }
                QMenu::item::selected {
                    background-color: #d0d0d0;
                }
                QLabel {
                    color: #333;
                }
                QTextEdit {
                    background-color: #fff;
                    color: #333;
                }
                QComboBox {
                    background-color: #fff;
                    color: #333;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                }
                QPushButton::hover {
                    background-color: #d0d0d0;
                }
            """
        elif self.current_theme == "dark":
            return """
                QMainWindow {
                    background-color: #333;
                }
                QWidget {
                    background-color: #333;
                    color: #f0f0f0;
                }
                 QMenuBar {
                    background-color: #444;
                    color: #f0f0f0;
                }
                QMenuBar::item {
                    background-color: #444;
                    color: #f0f0f0;
                }
                QMenuBar::item::selected {
                    background-color: #555;
                }
                QMenu {
                    background-color: #444;
                    color: #f0f0f0;
                }
                QMenu::item::selected {
                    background-color: #555;
                }
                QLabel {
                    color: #f0f0f0;
                }
                QTextEdit {
                    background-color: #555;
                    color: #f0f0f0;
                }
                QComboBox {
                    background-color: #555;
                    color: #f0f0f0;
                }
                QPushButton {
                    background-color: #444;
                    color: #f0f0f0;
                }
                QPushButton::hover {
                    background-color: #555;
                }
            """
        elif self.current_theme == "book":
            return """
                QMainWindow {
                    background-color: #f5f0e1;
                }
                QWidget {
                    background-color: #f5f0e1;
                    color: #333;
                }
                QMenuBar {
                    background-color: #e8e0d1;
                    color: #333;
                }
                QMenuBar::item {
                    background-color: #e8e0d1;
                    color: #333;
                }
                QMenuBar::item::selected {
                    background-color: #d0c8b8;
                }
                QMenu {
                    background-color: #e8e0d1;
                    color: #333;
                }
                QMenu::item::selected {
                    background-color: #d0c8b8;
                }
                QLabel {
                    color: #333;
                }
                QTextEdit {
                    background-color: #fff;
                    color: #333;
                }
                QComboBox {
                    background-color: #fff;
                    color: #333;
                }
                QPushButton {
                    background-color: #e8e0d1;
                    color: #333;
                }
                QPushButton::hover {
                    background-color: #d0c8b8;
                }
            """
        elif self.current_theme == "wood":
            return """
                QMainWindow {
                    background-color: #a38b6a;
                }
                QWidget {
                    background-color: #a38b6a;
                    color: #f0f0f0;
                }
                QMenuBar {
                    background-color: #8a7357;
                    color: #f0f0f0;
                }
                QMenuBar::item {
                    background-color: #8a7357;
                    color: #f0f0f0;
                }
                QMenuBar::item::selected {
                    background-color: #715e46;
                }
                QMenu {
                    background-color: #8a7357;
                    color: #f0f0f0;
                }
                QMenu::item::selected {
                    background-color: #715e46;
                }
                QLabel {
                    color: #f0f0f0;
                }
                QTextEdit {
                    background-color: #b9a58a;
                    color: #f0f0f0;
                }
                QComboBox {
                    background-color: #b9a58a;
                    color: #f0f0f0;
                }
                QPushButton {
                    background-color: #8a7357;
                    color: #f0f0f0;
                }
                QPushButton::hover {
                    background-color: #715e46;
                }
            """
        return ""

    def apply_style(self, widget: QWidget) -> None:
        style = self.get_style()
        widget.setStyleSheet(style)

    def load_fonts(self) -> None:
        # Load custom fonts if needed
        pass

    def set_font(self, widget: QWidget, font_name: str = "Arial", size: int = 10) -> None:
        font = QFont(font_name, size)
        widget.setFont(font)

    def set_theme(self, theme: str) -> None:
        self.current_theme = theme
