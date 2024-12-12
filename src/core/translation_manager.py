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
