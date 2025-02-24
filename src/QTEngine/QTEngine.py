import re
import os
import logging
from typing import Dict, List, Tuple, Optional, Any, Callable
from functools import lru_cache

from src.QTEngine.models.trie import Trie
from src.QTEngine.models.chinese_converter import ChineseConverter

# Import the new modularized functions
from src.QTEngine.src.character_utils import LATIN_CHARS, replace_special_chars
from src.QTEngine.src.text_processing import (
    convert_to_sino_vietnamese, 
    rephrase, 
    process_paragraph,
    TranslationMapping
)
from src.QTEngine.src.performance import profile_function
from src.QTEngine.src.data_loader import load_data, DataLoader
from src.QTEngine.src.translation_engine import TranslationEngine

class QTEngine(TranslationEngine):
    """
    A translation engine for converting Chinese text to Sino-Vietnamese.
    
    Attributes:
        names2 (Trie): Trie for Names2 data
        names (Trie): Trie for Names data
        viet_phrase (Trie): Trie for VietPhrase data
        chinese_phien_am (Dict[str, str]): Dictionary of Chinese Phien Am words
        loading_info (Dict[str, Any]): Information about data loading
        chinese_converter (ChineseConverter): Converter for Traditional to Simplified Chinese
    """
    
    def __init__(self, 
                 data_loader: Optional[DataLoader] = None, 
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the QTEngine with optional data loader and configuration.
        
        Args:
            data_loader (Optional[DataLoader]): Custom data loader
            config (Optional[Dict[str, Any]]): Configuration dictionary
        """
        super().__init__(data_loader, config)
        
        # Use provided data loader or create a default one
        self.data_loader = data_loader or DataLoader()
        
        # Load translation data
        self.names2, self.names, self.viet_phrase, self.chinese_phien_am, self.loading_info = self.data_loader.load_data()
        
        # Store configuration
        self.config = config or {}
        
        # Initialize Chinese converter
        self.chinese_converter = ChineseConverter()
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
    
    def translate(self, text: str) -> str:
        """
        Translate Chinese text to Sino-Vietnamese.
        
        Args:
            text (str): Input Chinese text
        
        Returns:
            str: Translated Sino-Vietnamese text
        """
        try:
            translated_text, _ = process_paragraph(
                text, 
                self.names2, 
                self.names, 
                self.viet_phrase, 
                self.chinese_phien_am
            )
            return translated_text
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            raise

    @lru_cache(maxsize=1000)
    def _translate_with_mapping_cached(self, text: str) -> Tuple[str, TranslationMapping]:
        """
        Cached implementation of translation with mapping.
        
        Args:
            text (str): Text to translate
            
        Returns:
            Tuple[str, TranslationMapping]: Translated text and mapping info
        """
        # Convert Traditional to Simplified if necessary
        simplified_text = self.chinese_converter.auto_convert_to_simplified(text)
        if simplified_text is None:
            simplified_text = text
            
        # Process and return translation with mapping
        return process_paragraph(
            simplified_text,
            self.names2,
            self.names,
            self.viet_phrase,
            self.chinese_phien_am
        )
    
    def translate_with_mapping(self, text: str, force_refresh: bool = False) -> Tuple[str, TranslationMapping]:
        """
        Translate Chinese text to Sino-Vietnamese and return mapping information.
        Uses caching for better performance.
        
        Args:
            text (str): Input Chinese text
            force_refresh (bool): Force refresh of translation data
        
        Returns:
            Tuple[str, TranslationMapping]: Translated text and mapping information
        """
        try:
            # Clear cache and refresh data if forcing refresh
            if force_refresh:
                self._translate_with_mapping_cached.cache_clear()
                # Ensure data is reloaded before translation
                self.refresh_data(force_reload=True)
                
                # Convert Traditional to Simplified if necessary
                simplified_text = self.chinese_converter.auto_convert_to_simplified(text)
                if simplified_text is None:
                    simplified_text = text
                
                # Get fresh translation directly without caching
                return process_paragraph(
                    simplified_text,
                    self.names2,
                    self.names,
                    self.viet_phrase,
                    self.chinese_phien_am
                )
            
            # Use cached translation if not forcing refresh
            return self._translate_with_mapping_cached(text)
        except Exception as e:
            self.logger.error(f"Translation with mapping failed: {e}")
            raise
    
    def validate_translation(self, original: str, translated: str) -> bool:
        """
        Validate the quality of translation.
        
        Args:
            original (str): Original Chinese text
            translated (str): Translated Sino-Vietnamese text
        
        Returns:
            bool: Whether the translation meets quality standards
        """
        # Basic validation checks
        if not original or not translated:
            return False
        
        # Check if translation length is reasonable
        length_ratio = len(translated) / len(original)
        if length_ratio < 0.5 or length_ratio > 2.0:
            self.logger.warning("Translation length is significantly different from original")
            return False
        
        return True
    
    def refresh_data(self, specific_file: Optional[str] = None, force_reload: bool = False):
        """
        Refresh translation data using the data loader.
        
        Args:
            specific_file (Optional[str]): If provided, only reload this specific file
            force_reload (bool): Force complete reload of data
        """
        try:
            # Clear both translation caches
            if hasattr(self, '_translate_cached'):
                self._translate_cached.cache_clear()
            if hasattr(self, '_translate_with_mapping_cached'):
                self._translate_with_mapping_cached.cache_clear()
            
            if specific_file:
                # Only reload the specific dictionary and maintain others
                filepath = os.path.join(self.data_loader.data_dir, specific_file)
                if not os.path.exists(filepath):
                    return
                
                # Load with optimized method based on file type
                if specific_file == 'Names2.txt':
                    self.names2 = self._reload_trie(filepath)
                elif specific_file == 'Names.txt':
                    self.names = self._reload_trie(filepath)
                elif specific_file == 'VietPhrase.txt':
                    self.viet_phrase = self._reload_trie(filepath)
                elif specific_file == 'ChinesePhienAmWords.txt':
                    data = self.data_loader.load_dictionary(filepath)
                    self.chinese_phien_am.update(data)
                
                self.logger.info(f"Translation data refreshed successfully for {specific_file}")
            else:
                # Full reload with optimized loading
                loaded_data = self.data_loader.load_data()
                (
                    self.names2,
                    self.names,
                    self.viet_phrase,
                    self.chinese_phien_am,
                    self.loading_info
                ) = loaded_data
                self.logger.info("All translation data refreshed successfully")
            
            # Call parent class's refresh_data method
            super().refresh_data()
        except Exception as e:
            self.logger.error(f"Data refresh failed: {e}")
            raise
                
    def _reload_trie(self, filepath: str) -> Trie:
        """Helper method to efficiently reload a Trie structure."""
        try:
            trie = Trie()
            data = self.data_loader.load_dictionary(filepath)
            # Use batch insert for better performance
            words = [(key, value) for key, value in data.items()]
            trie.batch_insert(words)
            return trie
        except Exception as e:
            self.logger.error(f"Failed to reload trie from {filepath}: {e}")
            raise
    
    def get_translation_metadata(self) -> Dict[str, Any]:
        """
        Retrieve metadata about the translation process.
        
        Returns:
            Dict[str, Any]: Translation metadata
        """
        return {
            'loading_info': self.loading_info,
            'data_sources': {
                'names2_size': len(self.names2.get_all_words()),
                'names_size': len(self.names.get_all_words()),
                'viet_phrase_size': len(self.viet_phrase.get_all_words()),
                'chinese_phien_am_size': len(self.chinese_phien_am)
            }
        }
    
    def rephrase_tokens(self, tokens: List[str]) -> str:
        """
        Rephrase tokens to form a properly formatted sentence.
        
        Args:
            tokens (List[str]): List of tokens to rephrase
        
        Returns:
            str: Rephrased sentence
        """
        return rephrase(tokens)
    
    def process_text(self, text: str, additional_processing: Optional[Callable[[str], str]] = None) -> str:
        """
        Process text with optional additional processing.
        
        Args:
            text (str): Input text
            additional_processing (Optional[Callable]): Optional additional processing function
        
        Returns:
            str: Processed text
        """
        # Translate the text
        translated = self.translate(text)
        
        # Apply additional processing if provided
        if additional_processing:
            translated = additional_processing(translated)
        
        return translated
    
    def translate_paragraph(self, paragraph: str) -> str:
        """
        Backward-compatible method for translating a single paragraph.
        
        Args:
            paragraph (str): The input paragraph in Chinese.
        
        Returns:
            str: The translated paragraph in Sino-Vietnamese.
        """
        # First convert Traditional to Simplified if necessary
        simplified_text = self.chinese_converter.auto_convert_to_simplified(paragraph)
        if simplified_text is None:
            simplified_text = paragraph
            
        translated_text, _ = process_paragraph(
            simplified_text, 
            self.names2, 
            self.names, 
            self.viet_phrase, 
            self.chinese_phien_am
        )
        return translated_text
    
    def get_loading_info(self) -> Dict[str, Any]:
        """
        Backward-compatible method to get loading information.
        
        Returns:
            Dict[str, Any]: Dictionary containing loading information.
        """
        return self.loading_info
