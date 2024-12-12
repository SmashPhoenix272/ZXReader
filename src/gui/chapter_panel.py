from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QListWidget,
    QPushButton,
    QHBoxLayout,
    QMessageBox
)
from PyQt5.QtCore import pyqtSignal
from typing import Optional
from src.core.chapter_manager import ChapterManager
from src.core.translation_manager import TranslationManager

class ChapterPanel(QWidget):
    chapter_selected = pyqtSignal(int)  # Signal when a chapter is selected
    chapter_changed = pyqtSignal(int)   # Signal when chapter content changes

    def __init__(self, parent: Optional[QWidget], chapter_manager: ChapterManager, translation_manager: TranslationManager):
        super().__init__(parent)
        self.chapter_manager = chapter_manager
        self.translation_manager = translation_manager
        self.initUI()
        self.update_detection_methods()

    def initUI(self):
        layout = QVBoxLayout()

        self.method_dropdown = QComboBox()
        self.method_dropdown.currentIndexChanged.connect(self.update_chapter_list)  # type: ignore
        layout.addWidget(self.method_dropdown)

        self.chapter_list = QListWidget()
        self.chapter_list.itemClicked.connect(self.on_chapter_selected)  # type: ignore
        layout.addWidget(self.chapter_list)

        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_chapter)  # type: ignore
        nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_chapter)  # type: ignore
        nav_layout.addWidget(self.next_button)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def update_detection_methods(self):
        self.method_dropdown.clear()
        self.method_dropdown.addItems(self.chapter_manager.detection_methods)
        self.method_dropdown.addItem("Hiển thị toàn bộ")

    def update_chapter_list(self):
        selected_method = self.method_dropdown.currentText()
        try:
            self.chapter_manager.set_detection_method(selected_method)
            chapters = self.chapter_manager.get_chapters()
            self.chapter_list.clear()
            if selected_method == "Hiển thị toàn bộ":
                self.chapter_list.addItem("Toàn bộ")
            else:
                for i, chapter in enumerate(chapters):
                    self.chapter_list.addItem(chapter)
                if chapters:
                    self.chapter_list.setCurrentRow(0)
                    self.chapter_selected.emit(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not detect chapters: {e}")

    def on_chapter_selected(self, item):
        selected_method = self.method_dropdown.currentText()
        if selected_method == "Hiển thị toàn bộ":
            self.chapter_selected.emit(-1)
        else:
            self.chapter_selected.emit(self.chapter_list.row(item))
        self.chapter_list.setCurrentItem(item)

    def prev_chapter(self):
        current_row = self.chapter_list.currentRow()
        if current_row > 0:
            self.chapter_list.setCurrentRow(current_row - 1)
            self.chapter_selected.emit(current_row - 1)

    def next_chapter(self):
        current_row = self.chapter_list.currentRow()
        if current_row < self.chapter_list.count() - 1:
            self.chapter_list.setCurrentRow(current_row + 1)
            self.chapter_selected.emit(current_row + 1)
    
    def set_chapter_list(self) -> None:
        chapters = self.chapter_manager.get_chapters()
        if chapters:
            self.chapter_list.clear()
            self.chapter_list.addItems(chapters)
