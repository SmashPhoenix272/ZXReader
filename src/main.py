import sys
import os
import time
import logging
from datetime import datetime

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)
from src.gui.main_window import MainWindow
from src.core.translation_manager import TranslationManager
from src.core.dictionary_manager import DictionaryManager
from src.core.chapter_manager import ChapterManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
qt_engine_path = os.path.join(current_dir, 'QTEngine')
sys.path.append(qt_engine_path)
from PyQt5.QtWidgets import QApplication
from src.QTEngine.QTEngine import QTEngine
 

if __name__ == '__main__':
    start_time = time.time()
    logger.info("Starting ZXReader initialization")
    
    # Initialize QApplication
    init_time = time.time()
    app = QApplication(sys.argv)
    logger.info(f"QApplication initialized in {time.time() - init_time:.2f}s")
    
    # Pre-initialize DataLoader singleton
    init_time = time.time()
    from src.QTEngine.src.data_loader import DataLoader
    logger.info("Pre-initializing DataLoader singleton")
    data_loader = DataLoader()
    data_loader.load_data()  # Initial load
    logger.info(f"DataLoader singleton initialized in {time.time() - init_time:.2f}s")
    
    # Initialize QTEngine singleton (will use cached data)
    init_time = time.time()
    qt_engine = QTEngine()
    logger.info(f"QTEngine singleton initialized in {time.time() - init_time:.2f}s")
    
    # Initialize managers, passing QTEngine singleton
    init_time = time.time()
    translation_manager = TranslationManager(qt_engine=qt_engine)
    logger.info(f"TranslationManager initialized with singleton QTEngine in {time.time() - init_time:.2f}s")
    
    init_time = time.time()
    dictionary_manager = DictionaryManager()
    logger.info(f"DictionaryManager initialized in {time.time() - init_time:.2f}s")
    
    init_time = time.time()
    chapter_manager = ChapterManager(qt_engine)
    logger.info(f"ChapterManager initialized in {time.time() - init_time:.2f}s")
    
    # Initialize and show main window
    init_time = time.time()
    main_window = MainWindow(translation_manager, dictionary_manager, chapter_manager)
    logger.info(f"MainWindow created in {time.time() - init_time:.2f}s")
    
    show_time = time.time()
    main_window.show()
    
    # Log total startup time
    total_time = time.time() - start_time
    logger.info(f"Total initialization completed in {total_time:.2f}s")
    logger.info("Starting application event loop")
    
    sys.exit(app.exec_())
