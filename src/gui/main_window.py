import sys
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QHBoxLayout,
    QWidget,
    QMessageBox
)
from .file_info_panel import FileInfoPanel
from .chapter_panel import ChapterPanel
from .main_translation_panel import MainTranslationPanel
from .dictionary_panel import DictionaryPanel
from src.core.file_handler import FileHandler
from src.core.translation_manager import TranslationManager
from src.core.chapter_manager import ChapterManager
from src.core.dictionary_manager import DictionaryManager
from .menu_bar import MenuBar
from .style_manager import StyleManager

class MainWindow(QMainWindow):
    def __init__(self, translation_manager):
        super().__init__()
        self.setWindowTitle("ZXReader")
        self.setGeometry(100, 100, 1200, 800)

        self.style_manager = StyleManager()
        self.file_handler = FileHandler()
        self.translation_manager = translation_manager
        self.dictionary_manager = DictionaryManager()
        self.chapter_manager = ChapterManager(self.translation_manager)

        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.file_info_panel = FileInfoPanel(self.file_handler, self.translation_manager)
        self.chapter_panel = ChapterPanel(self.chapter_manager, self.translation_manager)
        self.main_translation_panel = MainTranslationPanel()
        self.dictionary_panel = DictionaryPanel(self.dictionary_manager)

        main_layout.addWidget(self.file_info_panel, 20)
        main_layout.addWidget(self.chapter_panel, 20)
        main_layout.addWidget(self.main_translation_panel, 60)
        main_layout.addWidget(self.dictionary_panel, 20)

        self.menu_bar.file_opened.connect(self.handle_file_opened)
        self.chapter_panel.chapter_selected.connect(self.handle_chapter_selected)

    def handle_file_opened(self, file_path, translated_file_path):
        self.file_info_panel.set_file_info(file_path, translated_file_path)
        file_content = self.file_handler.read_file(file_path)
        self.chapter_manager.set_file_content(file_content)
        self.chapter_panel.update_chapter_list()

    def handle_chapter_selected(self, chapter_index):
        chapter_text = self.chapter_manager.get_chapter_text(chapter_index)
        self.main_translation_panel.set_text(chapter_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    translation_manager = TranslationManager()
    main_window = MainWindow(translation_manager)
    main_window.show()
    sys.exit(app.exec_())
