import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)
from src.gui.main_window import MainWindow
from src.core.translation_manager import TranslationManager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
qt_engine_path = os.path.join(current_dir, 'QTEngine')
sys.path.append(qt_engine_path)
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    translation_manager = TranslationManager()
    main_window = MainWindow(translation_manager)
    main_window.show()
