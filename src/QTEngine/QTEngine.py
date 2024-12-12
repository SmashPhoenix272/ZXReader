import re
import logging
from typing import Dict, List, Tuple, Optional, Any, Callable

from models.trie import Trie
from models.chinese_converter import ChineseConverter

# Import the new modularized functions
from src.QTEngine.src.character_utils import LATIN_CHARS, replace_special_chars
from src.QTEngine.src.text_processing import (
    convert_to_sino_vietnamese, 
    rephrase, 
    process_paragraph
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
            return process_paragraph(
                text, 
                self.names2, 
                self.names, 
                self.viet_phrase, 
                self.chinese_phien_am
            )
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
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
    
    def refresh_data(self):
        """
        Refresh translation data using the data loader.
        """
        try:
            (
                self.names2, 
                self.names, 
                self.viet_phrase, 
                self.chinese_phien_am, 
                self.loading_info
            ) = self.data_loader.load_data()
            self.logger.info("Translation data refreshed successfully")
        except Exception as e:
            self.logger.error(f"Data refresh failed: {e}")
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
            
        return process_paragraph(
            simplified_text, 
            self.names2, 
            self.names, 
            self.viet_phrase, 
            self.chinese_phien_am
        )
    
    def get_loading_info(self) -> Dict[str, Any]:
        """
        Backward-compatible method to get loading information.
        
        Returns:
            Dict[str, Any]: Dictionary containing loading information.
        """
        return self.loading_info