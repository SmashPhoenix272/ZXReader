from PyQt5.QtWidgets import (
    QTextEdit, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, 
    QPlainTextEdit, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from src.gui.dictionary_edit_dialog import DictionaryEditDialog
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
        # Keep a space before the word unless it starts with certain punctuation
        if i > 0 and not word[0] in ',.!?;:"\'])}':
            formatted.append(' ')
        formatted.append(word)
    
    text = ''.join(formatted)
    
    # Apply regex transformations in specific order
    # 1. Handle quotes and brackets
    text = re.sub(r'([\[\“\‘])\s*(\w)', lambda m: m.group(1) + m.group(2).upper(), text)
    text = re.sub(r'\s+([”\’\]])', r'\1', text)
    
    # 2. Handle special punctuation that needs space after
    text = re.sub(r'([?!⟨:«])\s+(\w)', lambda m: m.group(1) + ' ' + m.group(2).upper(), text)
    
    # 3. Handle periods separately to maintain mapping
    text = re.sub(r'\s*\.\s*(?=\w)', '. ', text)  # Ensure exactly one space after period
    text = re.sub(r'(?<=\.)\s+(\w)', lambda m: ' ' + m.group(1).upper(), text)
    
    # 4. Handle other punctuation
    text = re.sub(r'\s+([;:?!])', r'\1', text)
    
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
    dictionary_updated = pyqtSignal(str)  # Emits when dictionary is updated, includes filename

    def __init__(self, dictionary_manager=None):
        super().__init__()
        self.setReadOnly(True)
        self.segments: List[TextSegment] = []
        self.dictionary_manager = dictionary_manager
        
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

    def contextMenuEvent(self, event):
        """Handle right-click context menu."""
        menu = QMenu(self)
        
        # Check for selected text first
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            if selected_text.strip():
                # Get the segment to check if selection is in original text
                pos = cursor.selectionStart()
                segment = self.find_segment_at_position(pos)
                if segment:
                    if segment.is_original:
                        chinese_text = selected_text
                        hanviet = self.dictionary_manager.convert_to_hanviet(chinese_text)
                        
                        # Add dictionary actions for selected text
                        for dict_name in ["Names", "Names2", "VietPhrase"]:
                            existing_def = self.dictionary_manager.get_definition(dict_name, chinese_text)
                            action_text = f"Edit {dict_name}" if existing_def else f"Add to {dict_name}"
                            action = QAction(action_text, self)
                            action.triggered.connect(
                                lambda checked, d=dict_name, c=chinese_text, h=hanviet, e=existing_def:
                                self.show_dictionary_dialog(d, c, h, e)
                            )
                            menu.addAction(action)
                        
                        menu.exec_(event.globalPos())
                        return
                    elif segment.mapping_block:
                        # For translated text, try to find the corresponding Chinese text
                        # by looking up the mapping block
                        chinese_text = segment.mapping_block.original
                        hanviet = self.dictionary_manager.convert_to_hanviet(chinese_text)
                        
                        # Add dictionary actions for the original Chinese text
                        for dict_name in ["Names", "Names2", "VietPhrase"]:
                            existing_def = self.dictionary_manager.get_definition(dict_name, chinese_text)
                            action_text = f"Edit {dict_name}" if existing_def else f"Add to {dict_name}"
                            action = QAction(action_text, self)
                            action.triggered.connect(
                                lambda checked, d=dict_name, c=chinese_text, h=hanviet, e=existing_def:
                                self.show_dictionary_dialog(d, c, h, e)
                            )
                            menu.addAction(action)
                        
                        menu.exec_(event.globalPos())
                        return
        
        # Fall back to highlighted block if no text is selected
        cursor = self.cursorForPosition(event.pos())
        pos = cursor.position()
        segment = self.find_segment_at_position(pos)
        
        if segment and segment.mapping_block:
            chinese_text = segment.mapping_block.original
            hanviet = self.dictionary_manager.convert_to_hanviet(chinese_text)
            
            # Add dictionary actions for highlighted block
            for dict_name in ["Names", "Names2", "VietPhrase"]:
                existing_def = self.dictionary_manager.get_definition(dict_name, chinese_text)
                action_text = f"Edit {dict_name}" if existing_def else f"Add to {dict_name}"
                action = QAction(action_text, self)
                action.triggered.connect(
                    lambda checked, d=dict_name, c=chinese_text, h=hanviet, e=existing_def:
                    self.show_dictionary_dialog(d, c, h, e)
                )
                menu.addAction(action)
            
            menu.exec_(event.globalPos())
        
    def show_dictionary_dialog(self, dictionary_name: str, chinese_text: str, 
                             hanviet: str, existing_def: Optional[str]):
        """Show dialog for adding/editing dictionary entry."""
        dialog = DictionaryEditDialog(
            self,
            chinese_text=chinese_text,
            hanviet=hanviet,
            definition=existing_def or hanviet,  # Use hanviet as default definition
            dictionary_type=dictionary_name,
            is_edit=existing_def is not None
        )
        
        # Connect the dialog's dictionary_updated signal to our signal
        dialog.dictionary_updated.connect(self.dictionary_updated.emit)
        
        if dialog.exec_():
            values = dialog.get_values()
            if self.dictionary_manager.add_to_dictionary(
                dictionary_name, 
                values["chinese_text"], 
                values["definition"]
            ):
                # Signal will be emitted by the dialog
                pass

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
            cursor = self.textCursor()
            if cursor.hasSelection():
                selected_text = cursor.selectedText()
                if selected_text.strip():
                    # Get the segment to check if selection is in original text
                    start_pos = cursor.selectionStart()
                    end_pos = cursor.selectionEnd()
                    
                    # Find all segments in the selection range
                    selected_segments = []
                    for segment in self.segments:
                        # Check if segment overlaps with selection
                        if (segment.start_pos <= end_pos and segment.end_pos >= start_pos):
                            # Calculate the overlapping text
                            seg_start = max(start_pos, segment.start_pos)
                            seg_end = min(end_pos, segment.end_pos)
                            
                            if seg_end > seg_start:
                                selected_text = segment.text[
                                    max(0, seg_start - segment.start_pos):
                                    seg_end - segment.start_pos
                                ]
                                if selected_text.strip():
                                    selected_segments.append((selected_text, segment))
                    
                    if selected_segments:
                        # For original text
                        if self.selection_in_original:
                            combined_text = ''.join(text for text, _ in selected_segments)
                            self.selection_lookup.emit(combined_text)
                        # For translated text
                        else:
                            # Get the selected Vietnamese text
                            viet_text = ' '.join(text for text, _ in selected_segments)
                            viet_text = viet_text.strip()
                            
                            # Try to find a matching block for the exact Vietnamese text
                            for segment in self.segments:
                                if not segment.is_original and segment.mapping_block:
                                    if viet_text == segment.text.strip():
                                        self.selection_lookup.emit(segment.mapping_block.original)
                                        break
                                    # Also check if it's part of a compound word
                                    elif ' ' in segment.text:
                                        parts = segment.text.split()
                                        if viet_text in parts:
                                            # Find the corresponding Chinese text
                                            chinese_parts = segment.mapping_block.original
                                            if len(parts) == len(chinese_parts):
                                                idx = parts.index(viet_text)
                                                self.selection_lookup.emit(chinese_parts[idx])
                                                break
            
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
                else:
                    # For translated text, use the original Chinese text
                    self.selection_lookup.emit(clicked_segment.mapping_block.original)
                
                event.accept()
                return
        
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_selecting:
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
                # For original text, only collect original segments
                if self.selection_in_original:
                    if not segment.is_original:
                        break
                # For translated text, only collect translated segments
                elif segment.is_original:
                    continue
                    
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
                            if self.selection_in_original:
                                selected_segments.append(selected_text)
                            else:
                                # For translated text, use the original Chinese text
                                if segment.mapping_block:
                                    selected_segments.append(segment.mapping_block.original)
            
            # Emit the combined selected text for dictionary lookup
            if selected_segments:
                self.selection_lookup.emit(''.join(selected_segments))
        
        super().mouseMoveEvent(event)

    def find_segment_at_position(self, pos: int) -> Optional[TextSegment]:
        """Find the segment at the given position."""
        # First find the direct segment
        direct_segment = None
        for segment in self.segments:
            if segment.start_pos <= pos < segment.end_pos:
                direct_segment = segment
                break
                
        if not direct_segment:
            return None
            
        # If it's original text, return as is
        if direct_segment.is_original:
            return direct_segment
            
        # For translated text, try to find compound words
        if not direct_segment.is_original and direct_segment.mapping_block:
            # Get the full text and position within it
            text = direct_segment.text
            rel_pos = pos - direct_segment.start_pos
            
            # Find word boundaries
            start = rel_pos
            end = rel_pos
            
            # Expand selection to word boundaries
            while start > 0 and (text[start-1].isalpha() or text[start-1] == ' '):
                start -= 1
            while end < len(text) and (text[end].isalpha() or text[end] == ' '):
                end += 1
                
            # Trim spaces from edges
            while start < end and text[start] == ' ':
                start += 1
            while end > start and text[end-1] == ' ':
                end -= 1
                
            # If we found a word boundary different from the original segment
            if start != 0 or end != len(text):
                # Create a new segment for the compound word
                new_segment = TextSegment(
                    text[start:end],
                    direct_segment.start_pos + start,
                    False,
                    direct_segment.mapping_block
                )
                return new_segment
                
        return direct_segment

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
        self.current_chapter_index = 0  # Track current chapter
        
        # Create text edit with dictionary manager from dictionary panel
        self.text_edit = TranslationTextEdit(self.dictionary_panel.dictionary_manager)
        self.text_edit.segment_clicked.connect(self.handle_segment_click)
        self.text_edit.selection_lookup.connect(self.handle_selection_lookup)
        self.text_edit.dictionary_updated.connect(self.handle_dictionary_update)
        
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
        self.current_chapter_index = chapter_index  # Update current chapter index
        
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
                    block_text = block.translated.strip()
                    # Handle empty translations specially
                    if not block_text:
                        # For empty translations, just keep the mapping
                        trans_parts.append(TextSegment(
                            "",
                            current_pos + current_idx,
                            False,
                            block
                        ))
                        continue
                    
                    # Look for the block text, considering potential punctuation
                    search_idx = current_idx
                    while True:
                        idx = trans_text.lower().find(block_text.lower(), search_idx)
                        if idx < 0:
                            break
                            
                        # Check if this is the correct occurrence (not part of another word)
                        is_word_boundary = True
                        if idx > 0 and trans_text[idx-1].isalnum():
                            is_word_boundary = False
                        if idx + len(block_text) < len(trans_text) and trans_text[idx + len(block_text)].isalnum():
                            is_word_boundary = False
                            
                        if is_word_boundary:
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
                            break
                            
                        search_idx = idx + 1
                
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
                    block_text = block.translated.strip()
                    # Handle empty translations specially
                    if not block_text:
                        # For empty translations, just keep the mapping
                        trans_parts.append(TextSegment(
                            "",
                            current_pos + current_idx,
                            False,
                            block
                        ))
                        continue
                    
                    # Look for the block text, considering potential punctuation
                    search_idx = current_idx
                    while True:
                        idx = trans_text.lower().find(block_text.lower(), search_idx)
                        if idx < 0:
                            break
                            
                        # Check if this is the correct occurrence (not part of another word)
                        is_word_boundary = True
                        if idx > 0 and trans_text[idx-1].isalnum():
                            is_word_boundary = False
                        if idx + len(block_text) < len(trans_text) and trans_text[idx + len(block_text)].isalnum():
                            is_word_boundary = False
                            
                        if is_word_boundary:
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
                            break
                            
                        search_idx = idx + 1
                
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
            self.set_chapter_text(self.current_chapter_index)  # Use current chapter index

    def set_text(self, text: str):
        """Set the entire text content."""
        self.chapter_manager.set_text(text)
        if self.chapter_manager.chapters:
            self.set_chapter_text(0)
            self.current_chapter_index = 0  # Reset chapter index when loading new text
            
    def handle_dictionary_update(self, specific_file: Optional[str] = None):
        """
        Handle dictionary update by refreshing the current text.
        
        Args:
            specific_file (Optional[str]): If provided, only reload this specific dictionary
        """
        # Get the current text before refreshing
        current_text = None
        if self.chapter_manager.chapters:
            current_text = self.chapter_manager.get_chapter_text(self.current_chapter_index)
        
        # Reload only the specific dictionary if provided
        self.dictionary_panel.dictionary_manager.load_dictionaries(specific_file=specific_file)
        
        # Force refresh translation with current text
        if current_text:
            # Get translation and mapping with force_refresh
            translated_text = self.translation_manager.translate_text(current_text, force_refresh=True)
            
            # Update the display
            self.set_chapter_text(self.current_chapter_index)
