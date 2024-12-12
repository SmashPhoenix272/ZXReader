from typing import List, Tuple, Optional
from src.detect_chapters_methods import detect_chapters, CHAPTER_MATCHERS
from src.QTEngine.QTEngine import QTEngine
 
class ChapterManager:
    def __init__(self, qt_engine: QTEngine):
        self.qt_engine = qt_engine
        self.chapters: List[Tuple[int, int]] = []
        self.chapter_titles: List[str] = []
        self.translated_chapter_titles: List[str] = []
        self.current_chapter_index: int = -1
        self.text: str = ""
        self._detection_method: str = list(CHAPTER_MATCHERS.keys())[0]  # Default to first method
 
    def set_text(self, text: str) -> None:
        self.text = text
        self.detect_and_set_chapters()
 
    def detect_and_set_chapters(self) -> None:
        self.chapters = detect_chapters(self.text, self._detection_method)
        self.chapter_titles = self._extract_chapter_titles()
        self._translate_chapter_titles()
        self.current_chapter_index = 0
 
    def _extract_chapter_titles(self) -> List[str]:
        titles = []
        for start, end in self.chapters:
            titles.append(self.text[start:end])
        return titles
 
    def _translate_chapter_titles(self) -> None:
        translated_titles = []
        for title in self.chapter_titles:
            translated_title = self.qt_engine.translate(title)
            translated_titles.append(translated_title)
        self.translated_chapter_titles = translated_titles
 
    def get_chapter_titles(self) -> List[str]:
        return self.translated_chapter_titles
 
    def get_chapters(self) -> List[str]:
        """Get list of chapter titles"""
        return self.translated_chapter_titles
 
    def get_chapter_text(self, index: int) -> str:
        if not self.chapters:
            return ""
        if index == -1:
            return self.text
        if index < 0 or index >= len(self.chapters):
            return ""
        start, end = self.chapters[index]
        
        # Handle edge case where the last chapter goes to the end of the text
        if index == len(self.chapters) - 1:
            return self.text[start:]
        else:
            next_start, _ = self.chapters[index+1]
            return self.text[start:next_start]
 
    def next_chapter(self) -> int:
        if self.current_chapter_index < len(self.chapters) - 1:
            self.current_chapter_index += 1
        return self.current_chapter_index
 
    def prev_chapter(self) -> int:
        if self.current_chapter_index > 0:
            self.current_chapter_index -= 1
        return self.current_chapter_index
 
    def set_current_chapter(self, index: int) -> int:
        if 0 <= index < len(self.chapters):
            self.current_chapter_index = index
        return self.current_chapter_index
    
    def get_current_chapter_index(self) -> int:
        return self.current_chapter_index
 
    @property
    def detection_methods(self) -> List[str]:
        """Get available chapter detection methods"""
        return list(CHAPTER_MATCHERS.keys())
 
    def set_detection_method(self, method: str) -> None:
        """Set the chapter detection method"""
        if method in CHAPTER_MATCHERS:
            self._detection_method = method
            if self.text:  # Re-detect chapters if we have text
                self.detect_and_set_chapters()
