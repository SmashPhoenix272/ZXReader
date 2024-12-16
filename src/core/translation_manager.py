import os
import sys
from typing import Optional, Tuple

# Assuming QTEngine is in the parent directory of 'core'
current_dir = os.path.dirname(__file__)
qt_engine_path = os.path.abspath(os.path.join(current_dir, '..', 'QTEngine'))
sys.path.append(qt_engine_path)

from QTEngine import QTEngine
from src.QTEngine.src.text_processing import TranslationMapping

class TranslationManager:
    def __init__(self, qt_engine: Optional[QTEngine] = None):
        """
        Initializes the Translation Manager with an optional QTEngine instance.
        
        Args:
            qt_engine (QTEngine, optional): An existing QTEngine instance to use.
                                          If None, creates a new instance.
        """
        self.qt_engine = qt_engine if qt_engine is not None else QTEngine()
        self.current_mapping = None

    def translate_text(self, text: str) -> str:
        """
        Translates the given text using QTEngine.

        Args:
            text (str): The text to be translated.

        Returns:
            str: The translated text.
        """
        if not text:
            return ""
        
        translated_text, mapping = self.qt_engine.translate_with_mapping(text)
        self.current_mapping = mapping
        return translated_text
    
    def get_translated_file_path(self, file_path: str) -> str:
        """
        Generates the translated file path based on the original file path.

        Args:
            file_path (str): The path to the original file.

        Returns:
            str: The translated file path.
        """
        if not file_path:
            return ""
        
        file_name = os.path.basename(file_path)
        file_name_without_extension, file_extension = os.path.splitext(file_name)
        translated_file_name = self.translate_text(file_name_without_extension)
        translated_file_path = os.path.join(os.path.dirname(file_path), f"{translated_file_name}{file_extension}")
        return translated_file_path

    def get_translated_segment(self, original_text: str) -> Optional[Tuple[str, int, int]]:
        """
        Get the translated segment and its position for an original text segment.

        Args:
            original_text (str): The original text segment to look up.

        Returns:
            Optional[Tuple[str, int, int]]: A tuple containing (translated_text, start_pos, end_pos),
                                          or None if no mapping exists.
        """
        if self.current_mapping:
            return self.current_mapping.get_translated_segment(original_text)
        return None

    def get_original_segment(self, translated_text: str) -> Optional[Tuple[str, int, int]]:
        """
        Get the original segment and its position for a translated text segment.

        Args:
            translated_text (str): The translated text segment to look up.

        Returns:
            Optional[Tuple[str, int, int]]: A tuple containing (original_text, start_pos, end_pos),
                                          or None if no mapping exists.
        """
        if self.current_mapping:
            return self.current_mapping.get_original_segment(translated_text)
        return None
