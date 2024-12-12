from typing import Optional
import opencc
import re

class ChineseConverter:
    def __init__(self):
        # Initialize converters
        self.t2s = opencc.OpenCC('t2s')  # Traditional to Simplified
        self.s2t = opencc.OpenCC('s2t')  # Simplified to Traditional
        
        # Common Traditional-only characters
        self.traditional_chars = set('繁體國說壽麗華實現觀點愛爾蘭寫藝術')
    
    def has_chinese(self, text: str) -> bool:
        """Check if the text contains Chinese characters."""
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        return bool(chinese_pattern.search(text))
    
    def is_traditional(self, text: str) -> bool:
        """
        Detect if the Chinese text is Traditional Chinese by checking for
        the presence of Traditional-specific characters.
        """
        if not self.has_chinese(text):
            return False
            
        # Convert text to simplified
        simplified = self.t2s.convert(text)
        
        # If the conversion changes the text, it's likely Traditional
        if simplified != text:
            # Double check by looking for Traditional-specific characters
            for char in text:
                if char in self.traditional_chars:
                    return True
            
            # If no specific Traditional chars found but text changed, still likely Traditional
            return True
            
        return False
    
    def convert_to_simplified(self, text: str) -> str:
        """Convert Chinese text to Simplified Chinese."""
        if not self.has_chinese(text):
            return text
        return self.t2s.convert(text)
    
    def convert_to_traditional(self, text: str) -> str:
        """Convert Chinese text to Traditional Chinese."""
        if not self.has_chinese(text):
            return text
        return self.s2t.convert(text)
    
    def auto_convert_to_simplified(self, text: str) -> Optional[str]:
        """
        Automatically detect if the text is Traditional Chinese and convert to Simplified if it is.
        Returns None if no Chinese characters are found.
        """
        if not self.has_chinese(text):
            return None
            
        # Always convert to simplified to ensure consistency
        simplified = self.convert_to_simplified(text)
        return simplified if simplified != text else text
