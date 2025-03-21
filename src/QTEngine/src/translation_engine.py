from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Tuple, List
from functools import lru_cache
from datetime import datetime, timedelta
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
    
    # Class-level watcher to prevent duplicates
    _shared_watcher = None
    
    def __init__(self,
                 data_loader: Optional[DataLoader] = None,
                 config: Optional[Dict[str, Any]] = None,
                 data_dir: Optional[str] = None,
                 auto_watch: bool = True):
        """
        Initialize the translation engine with optional data watching.
        Uses a shared file watcher to prevent duplicate notifications.
        
        Args:
            data_loader: Optional custom data loader
            config: Optional configuration dictionary
            data_dir: Optional directory for data files
            auto_watch: Whether to automatically start file watching
        """
        self.config = config or {}
        
        # Get or reuse DataLoader singleton instance
        self.data_loader = data_loader or DataLoader(data_dir=data_dir)
        self.data_dir = data_dir or self.data_loader.data_dir
        
        # Use cached data from singleton instance if available
        self.data = self.data_loader.loaded_data or self.data_loader.load_data()
        logger.info("TranslationEngine using DataLoader singleton instance")
        
        # Setup shared file watcher
        if auto_watch and not TranslationEngine._shared_watcher:
            TranslationEngine._shared_watcher = self.start_data_watching()
        self.data_watcher = TranslationEngine._shared_watcher
    
    def start_data_watching(self):
        """
        Start watching data files for changes.
        
        Returns:
            DataFileWatcher: The created file watcher instance
        """
        try:
            watcher = create_data_watcher(
                data_dir=self.data_dir,
                reload_callback=self._on_data_reload
            )
            logger.info(f"Started watching data files in {self.data_dir}")
            return watcher
        except Exception as e:
            logger.error(f"Failed to start data watching: {e}")
            return None
    
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
    
    def refresh_data(self, force_reload: bool = False, specific_file: Optional[str] = None):
        """
        Optional method to refresh translation data.
        Can be overridden by subclasses to perform custom actions on data reload.
        
        Args:
            force_reload (bool): Whether to force a complete reload of all data
        
        Note: This clears all translation caches to ensure fresh results.
        """
        # Clear both translation caches
        if hasattr(self, '_translate_cached'):
            self._translate_cached.cache_clear()
        if hasattr(self, '_translate_with_mapping_cached'):
            self._translate_with_mapping_cached.cache_clear()
            
        # If forcing reload, trigger data loader refresh
        if force_reload and self.data_loader:
            if specific_file:
                self.data = self.data_loader.load_data(specific_file=specific_file)
            else:
                self.data = self.data_loader.load_data()
            
        logger.info("Translation data and caches refreshed successfully")
        
    @lru_cache(maxsize=1000)
    def _translate_cached(self, text: str) -> str:
        """
        Cached translation helper to improve performance.
        
        Args:
            text (str): Text to translate
            
        Returns:
            str: Translated text
        """
        return self.translate(text)

    @lru_cache(maxsize=1000)
    def _translate_with_mapping_cached(self, text: str) -> Tuple[str, Any]:
        """
        Cached translation with mapping helper.
        
        Args:
            text (str): Text to translate
            
        Returns:
            Tuple[str, Any]: Tuple of translated text and mapping
        """
        raise NotImplementedError("Subclasses must implement _translate_with_mapping_cached")
    
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
