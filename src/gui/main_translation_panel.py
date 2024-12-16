from PyQt5.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QPlainTextEdit
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import (
    QTextCursor, QTextCharFormat, QColor, QTextBlockFormat, 
    QTextDocument, QTextBlockUserData, QTextBlock
)
from typing import Optional, Dict, Tuple, List
from src.core.chapter_manager import ChapterManager
from src.core.translation_manager import TranslationManager
from src.QTEngine.src.text_processing import TranslationMapping, Block
import re

def format_translated_text(text: str) -> str:
    """Format translated text with proper spacing and capitalization."""
    # Add proper spacing between words first
    words = text.split()
    formatted = []
    for i, word in enumerate(words):
        if i > 0 and not word[0] in ',.!?;:"\'])}':
            formatted.append(' ')
        formatted.append(word)
    
    text = ''.join(formatted)
    
    # Apply regex transformations
    text = re.sub(r'([\[\“\‘])\s*(\w)', lambda m: m.group(1) + m.group(2).upper(), text)
    text = re.sub(r'\s+([”\’\]])', r'\1', text)
    text = re.sub(r'([?!⟨:«])\s+(\w)', lambda m: m.group(1) + ' ' + m.group(2).upper(), text)
    text = re.sub(r'\s+([;:?!.])', r'\1', text)
    text = re.sub(r'(?<!\.)\.(?!\.)\s+(\w)', lambda m: '. ' + m.group(2).upper(), text)
    
    return text

def format_original_text(text: str) -> str:
    """Format original Chinese text (no spaces needed)."""
    return ''.join(text.split())  # Remove any existing spaces

class TextSegment:
    """Represents a segment of text with its mapping."""
    def __init__(self, text: str, start_pos: int, is_original: bool, mapping_block: Optional[Block] = None):
        self.text = text
        self.start_pos = start_pos
        self.end_pos = start_pos + len(text)
        self.is_original = is_original
        self.mapping_block = mapping_block

class TranslationTextEdit(QPlainTextEdit):
    """Custom QPlainTextEdit that handles mouse events for dictionary lookup."""
    segment_clicked = pyqtSignal(TextSegment)  # Emits the clicked segment
    selection_lookup = pyqtSignal(str)  # Emits selected text for dictionary lookup

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.segments: List[TextSegment] = []
        
        # Set up text formats
        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(QColor(255, 255, 0, 100))  # Light yellow
        self.original_format = QTextCharFormat()
        self.original_format.setBackground(QColor(240, 240, 255))  # Light blue
        self.translated_format = QTextCharFormat()
        self.translated_format.setBackground(QColor(240, 255, 240))  # Light green
        
        # Mouse selection tracking
        self.is_selecting = False
        self.selection_start_pos = -1
        self.selection_in_original = False
        self.last_clicked_segment = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Get cursor position at click
            cursor = self.cursorForPosition(event.pos())
            pos = cursor.position()
            
            # Start selection tracking
            self.is_selecting = True
            self.selection_start_pos = pos
            
            # Check if selection started in original text
            start_segment = self.find_segment_at_position(pos)
            self.selection_in_original = start_segment and start_segment.is_original
            
            # Store clicked segment for double click handling
            self.last_clicked_segment = start_segment
            
            # Handle single click for dictionary lookup only if not selecting
            if not self.textCursor().hasSelection():
                clicked_segment = self.find_segment_at_position(pos)
                if clicked_segment:
                    self.segment_clicked.emit(clicked_segment)
        
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # If there's a selection, prioritize it over segment click
            cursor = self.textCursor()
            if cursor.hasSelection() and self.selection_in_original:
                selected_text = cursor.selectedText()
                if selected_text.strip():
                    self.selection_lookup.emit(selected_text)
            
            self.is_selecting = False
            self.selection_start_pos = -1
            self.selection_in_original = False
        
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Get cursor position at click
            cursor = self.cursorForPosition(event.pos())
            pos = cursor.position()
            
            # Find segment at click position
            clicked_segment = self.find_segment_at_position(pos)
            if clicked_segment and clicked_segment.mapping_block:
                # Select the entire segment text
                cursor = self.textCursor()
                cursor.setPosition(clicked_segment.start_pos)
                cursor.setPosition(clicked_segment.end_pos, QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
                
                # Emit the selected text for lookup
                if clicked_segment.is_original:
                    self.selection_lookup.emit(clicked_segment.text)
                
                event.accept()
                return
        
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_selecting and self.selection_in_original:
            # Get current cursor position
            cursor = self.cursorForPosition(event.pos())
            current_pos = cursor.position()
            
            # Find segments in the selection range
            start_pos = min(self.selection_start_pos, current_pos)
            end_pos = max(self.selection_start_pos, current_pos)
            
            # Get all segments in the selection range
            selected_segments = []
            current_segment = None
            
            for segment in self.segments:
                # Stop if we reach translated text
                if not segment.is_original:
                    break
                    
                # Check if segment is in selection range
                if segment.start_pos <= end_pos and segment.end_pos >= start_pos:
                    # Calculate the overlapping text
                    seg_start = max(start_pos, segment.start_pos)
                    seg_end = min(end_pos, segment.end_pos)
                    
                    if seg_end > seg_start:
                        selected_text = segment.text[
                            max(0, seg_start - segment.start_pos):
                            seg_end - segment.start_pos
                        ]
                        if selected_text.strip():
                            selected_segments.append(selected_text)
            
            # Emit the combined selected text for dictionary lookup
            if selected_segments:
                self.selection_lookup.emit(''.join(selected_segments))
        
        super().mouseMoveEvent(event)

    def find_segment_at_position(self, pos: int) -> Optional[TextSegment]:
        """Find the segment at the given position."""
        for segment in self.segments:
            if segment.start_pos <= pos < segment.end_pos:
                return segment
        return None

    def clear_segments(self):
        """Clear all segments."""
        self.segments.clear()
        self.clear()

    def add_segment(self, segment: TextSegment):
        """Add a new text segment."""
        self.segments.append(segment)
        
        # Create cursor at segment position
        cursor = QTextCursor(self.document())
        cursor.setPosition(segment.start_pos)
        
        # Set format based on whether it's original or translated
        format = self.original_format if segment.is_original else self.translated_format
        cursor.setCharFormat(format)
        
        # Insert the text
        cursor.insertText(segment.text)

class MainTranslationPanel(QWidget):
    def __init__(self, parent: Optional[QWidget], chapter_manager: ChapterManager,
                 translation_manager: TranslationManager, dictionary_panel):
        super().__init__(parent)
        self.chapter_manager = chapter_manager
        self.translation_manager = translation_manager
        self.dictionary_panel = dictionary_panel
        
        # Create text edit
        self.text_edit = TranslationTextEdit()
        self.text_edit.segment_clicked.connect(self.handle_segment_click)
        self.text_edit.selection_lookup.connect(self.handle_selection_lookup)
        
        # Create toggle button
        self.show_original = False
        self.toggle_button = QPushButton("Show Original Text")
        self.toggle_button.clicked.connect(self.toggle_text_display)
        
        # Layout
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.toggle_button)
        layout.addLayout(button_layout)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def set_chapter_text(self, chapter_index: int):
        """Set the text for a chapter."""
        self.text_edit.clear_segments()
        
        # Get original text and translate
        original_text = self.chapter_manager.get_chapter_text(chapter_index)
        if not original_text:
            return
            
        # Process each paragraph
        current_pos = 0
        paragraphs = original_text.splitlines()
        for i, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue
                
            # Get translation and mapping
            translated_text = self.translation_manager.translate_text(paragraph)
            mapping = self.translation_manager.current_mapping
            
            if self.show_original:
                # For original text, just add blocks directly without spacing
                for block in mapping.blocks:
                    self.text_edit.add_segment(TextSegment(
                        block.original,
                        current_pos,
                        True,
                        block
                    ))
                    current_pos += len(block.original)
                
                # Add newline between original and translation
                self.text_edit.add_segment(TextSegment("\n", current_pos, True))
                current_pos += 1
                
                # Format and combine all translated text
                trans_text = ' '.join(block.translated for block in mapping.blocks)
                trans_text = format_translated_text(trans_text)
                
                # Capitalize first letter of paragraph if it's not already capitalized
                if trans_text and not trans_text[0].isupper() and trans_text[0].isalpha():
                    trans_text = trans_text[0].upper() + trans_text[1:]
                
                # Split back into blocks while preserving spacing
                trans_parts = []
                current_idx = 0
                for block in mapping.blocks:
                    # Find the formatted version of this block in the formatted text
                    block_text = block.translated
                    idx = trans_text.lower().find(block_text.lower(), current_idx)
                    if idx >= 0:
                        # Add any spacing before this block
                        if idx > current_idx:
                            trans_parts.append(TextSegment(
                                trans_text[current_idx:idx],
                                current_pos + current_idx,
                                False
                            ))
                        # Add the block with proper capitalization from the formatted text
                        actual_text = trans_text[idx:idx + len(block_text)]
                        trans_parts.append(TextSegment(
                            actual_text,
                            current_pos + idx,
                            False,
                            block
                        ))
                        current_idx = idx + len(block_text)
                
                # Add any remaining spacing
                if current_idx < len(trans_text):
                    trans_parts.append(TextSegment(
                        trans_text[current_idx:],
                        current_pos + current_idx,
                        False
                    ))
                
                # Add all translated segments
                for segment in trans_parts:
                    self.text_edit.add_segment(segment)
                    current_pos += len(segment.text)
            else:
                # Format and combine all translated text
                trans_text = ' '.join(block.translated for block in mapping.blocks)
                trans_text = format_translated_text(trans_text)
                
                # Capitalize first letter of paragraph if it's not already capitalized
                if trans_text and not trans_text[0].isupper() and trans_text[0].isalpha():
                    trans_text = trans_text[0].upper() + trans_text[1:]
                
                # Split back into blocks while preserving spacing
                trans_parts = []
                current_idx = 0
                for block in mapping.blocks:
                    # Find the formatted version of this block in the formatted text
                    block_text = block.translated
                    idx = trans_text.lower().find(block_text.lower(), current_idx)
                    if idx >= 0:
                        # Add any spacing before this block
                        if idx > current_idx:
                            trans_parts.append(TextSegment(
                                trans_text[current_idx:idx],
                                current_pos + current_idx,
                                False
                            ))
                        # Add the block with proper capitalization from the formatted text
                        actual_text = trans_text[idx:idx + len(block_text)]
                        trans_parts.append(TextSegment(
                            actual_text,
                            current_pos + idx,
                            False,
                            block
                        ))
                        current_idx = idx + len(block_text)
                
                # Add any remaining spacing
                if current_idx < len(trans_text):
                    trans_parts.append(TextSegment(
                        trans_text[current_idx:],
                        current_pos + current_idx,
                        False
                    ))
                
                # Add all translated segments
                for segment in trans_parts:
                    self.text_edit.add_segment(segment)
                    current_pos += len(segment.text)
            
            # Add paragraph break if not last paragraph
            if i < len(paragraphs) - 1:
                self.text_edit.add_segment(TextSegment("\n\n", current_pos, False))
                current_pos += 2

    def handle_segment_click(self, segment: TextSegment):
        """Handle when a text segment is clicked."""
        if not segment.mapping_block:
            return
        
        # Clear any existing highlights
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        
        # Highlight the clicked segment and its corresponding translation/original
        for other_segment in self.text_edit.segments:
            if other_segment.mapping_block == segment.mapping_block:
                cursor = self.text_edit.textCursor()
                cursor.setPosition(other_segment.start_pos)
                cursor.setPosition(other_segment.end_pos, QTextCursor.KeepAnchor)
                cursor.setCharFormat(self.text_edit.highlight_format)
        
        # Look up the word - always use the original text from the mapping block
        self.dictionary_panel.lookup_word(segment.mapping_block.original)

    def handle_selection_lookup(self, text: str):
        """Handle dictionary lookup for selected text."""
        self.dictionary_panel.lookup_word(text)

    def toggle_text_display(self):
        """Toggle between showing original and translated text."""
        self.show_original = not self.show_original
        self.toggle_button.setText("Hide Original Text" if self.show_original else "Show Original Text")
        
        if self.chapter_manager.chapters:
            self.set_chapter_text(0)

    def set_text(self, text: str):
        """Set the entire text content."""
        self.chapter_manager.set_text(text)
        if self.chapter_manager.chapters:
            self.set_chapter_text(0)
