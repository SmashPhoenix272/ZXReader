from PyQt5.QtWidgets import QMenuBar, QAction, QMenu
from PyQt5.QtCore import pyqtSignal

class MenuBar(QMenuBar):
    file_opened = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_menus()

    def init_menus(self):
        """Initializes the menus and actions."""
        file_menu = self.addMenu('File')
        chapter_menu = self.addMenu('Chapter')
        dictionary_menu = self.addMenu('Dictionary')

        # File Menu Actions
        self.open_file_action = QAction('Open', self)
        self.open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(self.open_file_action)

        # Chapter Menu Actions
        self.detect_chapters_action = QAction('Detect Chapters', self)
        self.detect_chapters_action.triggered.connect(self.main_window.chapter_manager.detect_chapters)
        chapter_menu.addAction(self.detect_chapters_action)

        # Dictionary Menu Actions
        self.sync_dictionaries_action = QAction('Sync Custom Names', self)
        self.sync_dictionaries_action.triggered.connect(lambda: self.main_window.dictionary_manager.sync_custom_names())
        dictionary_menu.addAction(self.sync_dictionaries_action)

    def open_file(self):
        file_path = self.main_window.file_handler.open_file_dialog()
        if file_path:
            self.file_opened.emit(file_path)
