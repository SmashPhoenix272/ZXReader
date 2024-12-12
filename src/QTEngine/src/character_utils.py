from typing import Set, Dict
from src.QTEngine.src.ReplaceChar import SPECIAL_CHARS

# Comprehensive set of Latin characters including various language variants
LATIN_CHARS: Set[str] = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                  'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'  # Vietnamese
                  'ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ'
                  'áéíóúýàèìòùâêîôûãõñäëïöüÿçß'  # French, German, Spanish, Portuguese
                  'ÁÉÍÓÚÝÀÈÌÒÙÂÊÎÔÛÃÕÑÄËÏÖÜŸÇSS')  # Uppercase variants

def replace_special_chars(text: str) -> str:
    """
    Replace special characters in the text with their Vietnamese equivalents.

    Args:
        text (str): The input text containing special characters.

    Returns:
        str: The text with special characters replaced.
    """
    for han, viet in SPECIAL_CHARS.items():
        text = text.replace(han, viet)
    return text
