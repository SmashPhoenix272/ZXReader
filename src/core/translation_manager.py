import os
import sys

# Assuming QTEngine is in the parent directory of 'core'
current_dir = os.path.dirname(__file__)
qt_engine_path = os.path.abspath(os.path.join(current_dir, '..', 'QTEngine'))
sys.path.append(qt_engine_path)
os.chdir(qt_engine_path)

from QTEngine import QTEngine

class TranslationManager:
    def __init__(self):
        """Initializes the Translation Manager and QTEngine."""
        self.qt_engine = QTEngine()

    def translate_text(self, text):
        """
        Translates the given text using QTEngine.

        Args:
            text (str): The text to be translated.

        Returns:
            str: The translated text.
        """
        if not text:
            return ""
        
        translated_text = self.qt_engine.translate(text)
        return translated_text
    
    def get_translated_file_path(self, file_path):
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
