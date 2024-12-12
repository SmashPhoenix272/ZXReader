import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)
from src.gui.main_window import MainWindow
from src.core.translation_manager import TranslationManager
from src.core.dictionary_manager import DictionaryManager
from src.core.chapter_manager import ChapterManager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
qt_engine_path = os.path.join(current_dir, 'QTEngine')
sys.path.append(qt_engine_path)
from PyQt5.QtWidgets import QApplication
from src.QTEngine.QTEngine import QTEngine
 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    qt_engine = QTEngine()
    translation_manager = TranslationManager()
    dictionary_manager = DictionaryManager()
    chapter_manager = ChapterManager(qt_engine)
    main_window = MainWindow(translation_manager, dictionary_manager, chapter_manager)
    main_window.show()
    sys.exit(app.exec_())
