from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Tuple
import logging
import os

from src.QTEngine.src.data_loader import DataLoader
from src.QTEngine.src.data_watcher import DataFileWatcher, create_data_watcher

logger = logging.getLogger(__name__)

class TranslationEngine(ABC):
    """
    Abstract base class for translation engines with dynamic data watching.
    Defines the core interface for translation functionality.
    """
    
    def __init__(self, 
                 data_loader: Optional[DataLoader] = None, 
                 config: Optional[Dict[str, Any]] = None,
                 data_dir: Optional[str] = None,
                 auto_watch: bool = True):
        """
        Initialize the translation engine with optional data watching.
        
        Args:
            data_loader: Optional custom data loader
            config: Optional configuration dictionary
            data_dir: Optional directory for data files
            auto_watch: Whether to automatically start file watching
        """
        self.config = config or {}
        self.data_loader = data_loader or DataLoader(data_dir=data_dir)
        self.data_dir = data_dir or self.data_loader.data_dir
        
        # Initial data load
        self.data = self.data_loader.load_data()
        
        # Setup file watcher
        self.data_watcher = None
        if auto_watch:
            self.start_data_watching()
    
    def start_data_watching(self):
        """
        Start watching data files for changes.
        """
        try:
            self.data_watcher = create_data_watcher(
                data_dir=self.data_dir, 
                reload_callback=self._on_data_reload
            )
            logger.info(f"Started watching data files in {self.data_dir}")
        except Exception as e:
            logger.error(f"Failed to start data watching: {e}")
    
    def _on_data_reload(self, new_data: Tuple):
        """
        Internal method to handle data reloading.
        
        Args:
            new_data: Newly loaded data tuple
        """
        try:
            logger.info("Reloading translation data")
            self.data = new_data
            self.refresh_data()
        except Exception as e:
            logger.error(f"Error during data reload: {e}")
    
    @abstractmethod
    def translate(self, text: str) -> str:
        """
        Translate the input text.
        
        Args:
            text (str): Input text to translate
        
        Returns:
            str: Translated text
        """
        raise NotImplementedError("Subclasses must implement translation method")
    
    @abstractmethod
    def validate_translation(self, original: str, translated: str) -> bool:
        """
        Validate the quality of translation.
        
        Args:
            original (str): Original text
            translated (str): Translated text
        
        Returns:
            bool: Whether the translation meets quality standards
        """
        raise NotImplementedError("Subclasses must implement translation validation")
    
    def refresh_data(self):
        """
        Optional method to refresh translation data.
        Can be overridden by subclasses to perform custom actions on data reload.
        """
        pass
    
    def get_translation_metadata(self) -> Dict[str, Any]:
        """
        Retrieve metadata about the translation process.
        
        Returns:
            Dict[str, Any]: Translation metadata
        """
        return {
            'data_dir': self.data_dir,
            'watching_enabled': self.data_watcher is not None
        }
    
    def stop_data_watching(self):
        """
        Stop watching data files.
        """
        if self.data_watcher:
            self.data_watcher.stop()
            logger.info("Stopped data file watching")
