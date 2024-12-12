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

class ChapterPanel(QWidget):
    chapter_selected = pyqtSignal(int)

    def __init__(self, chapter_manager, translation_manager):
        super().__init__()
        self.chapter_manager = chapter_manager
        self.translation_manager = translation_manager
        self.detection_methods = ["regex1", "regex2", "regex3"]
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.method_dropdown = QComboBox()
        self.method_dropdown.addItems(self.detection_methods)
        self.method_dropdown.currentIndexChanged.connect(self.update_chapter_list)
        layout.addWidget(self.method_dropdown)

        self.chapter_list = QListWidget()
        self.chapter_list.itemClicked.connect(self.on_chapter_selected)
        layout.addWidget(self.chapter_list)

        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_chapter)
        nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_chapter)
        nav_layout.addWidget(self.next_button)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def update_chapter_list(self):
        selected_method = self.method_dropdown.currentText()
        try:
            chapters = self.chapter_manager.detect_chapters(selected_method)
            self.chapter_list.clear()
            for i, chapter in enumerate(chapters):
                translated_title = self.translation_manager.translate_text(chapter.title)
                self.chapter_list.addItem(f"{i+1}. {translated_title}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not detect chapters: {e}")

    def on_chapter_selected(self, item):
        self.chapter_selected.emit(self.chapter_list.row(item))

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
