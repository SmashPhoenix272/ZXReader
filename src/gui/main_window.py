from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal
from src.gui.file_info_panel import FileInfoPanel
from src.gui.chapter_panel import ChapterPanel
from src.gui.dictionary_panel import DictionaryPanel
from src.gui.main_translation_panel import MainTranslationPanel
from src.gui.menu_bar import MenuBar
from src.core.file_handler import FileHandler
#from src.utils.qt_utils import create_font

class MainWindow(QMainWindow):
    def __init__(self, translation_manager, dictionary_manager, chapter_manager):
        super().__init__()
        self.translation_manager = translation_manager
        self.dictionary_manager = dictionary_manager
        self.chapter_manager = chapter_manager
        self.file_handler = FileHandler()  # Initialize FileHandler
        
        self.setWindowTitle("ZXReader")
        self.setGeometry(100, 100, 1200, 800)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        self.main_content_layout = QHBoxLayout()
        self.main_layout.addLayout(self.main_content_layout)
        
        self.left_panel_layout = QVBoxLayout()
        self.main_content_layout.addLayout(self.left_panel_layout)
        
        self.right_panel_layout = QVBoxLayout()
        self.main_content_layout.addLayout(self.right_panel_layout)

        # Initialize panels with proper parent and managers
        self.file_info_panel = FileInfoPanel(self, self.translation_manager)
        self.left_panel_layout.addWidget(self.file_info_panel)
        
        self.chapter_panel = ChapterPanel(self, self.chapter_manager, self.translation_manager)
        self.left_panel_layout.addWidget(self.chapter_panel)
        
        self.dictionary_panel = DictionaryPanel(self.dictionary_manager)
        self.left_panel_layout.addWidget(self.dictionary_panel)
        
        self.main_translation_panel = MainTranslationPanel(self, self.chapter_manager, self.translation_manager, self.dictionary_panel)
        self.right_panel_layout.addWidget(self.main_translation_panel)

        # Connect signals with correct signal names
        self.menu_bar.file_opened.connect(self.set_file_info)
        self.chapter_panel.chapter_selected.connect(self.set_chapter_text)
        self.chapter_panel.chapter_changed.connect(self.set_chapter_list)
    
    def open_file_dialog(self):
        file_path = self.file_handler.open_file_dialog()
        if file_path:
            self.set_file_info(file_path)
            text = self.file_handler.read_file(file_path)
            if text is not None:
                self.main_translation_panel.set_text(text)
    
    def set_file_info(self, file_path):
        self.file_info_panel.set_file_info(file_path)

    def set_chapter_text(self, chapter_text):
         self.main_translation_panel.set_chapter_text(chapter_text)

    def set_chapter_list(self, chapter_list):
        self.main_translation_panel.set_chapter_list(chapter_list)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    from src.core.translation_manager import TranslationManager
    from src.core.dictionary_manager import DictionaryManager
    from src.core.chapter_manager import ChapterManager
    from src.QTEngine.QTEngine import QTEngine
    import sys
    
    app = QApplication(sys.argv)
    qt_engine = QTEngine()
    translation_manager = TranslationManager(qt_engine)
    dictionary_manager = DictionaryManager(qt_engine)
    chapter_manager = ChapterManager(qt_engine)
    main_window = MainWindow(translation_manager, dictionary_manager, chapter_manager)
    main_window.show()
    sys.exit(app.exec_())
