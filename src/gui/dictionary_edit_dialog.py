"""
FILE OVERVIEW:
Purpose: Dialog for adding/editing dictionary entries
Key Concepts: Dictionary editing, text case modification
Module Type: GUI
@ai_context: Handles dictionary entry editing with text case options
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QGridLayout, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Optional

class DictionaryEditDialog(QDialog):
    dictionary_updated = pyqtSignal(str)  # Signal when dictionary is updated, includes filename
    
    def __init__(self, parent=None, chinese_text="", hanviet="", definition="", 
                 dictionary_type="", is_edit=False, context_text=""):
        super().__init__(parent)
        self.chinese_text = chinese_text
        self.hanviet = hanviet
        self.definition = definition
        self.dictionary_type = dictionary_type
        self.is_edit = is_edit
        
        # Context and selection settings
        self.context_text_full = context_text
        self.context_window_size = 15  # Characters to show on each side
        self.selection_start = -1
        self.selection_end = -1
        
        # Find initial selection position
        if self.chinese_text and self.context_text_full:
            pos = self.context_text_full.find(self.chinese_text)
            if pos != -1:
                self.selection_start = pos
                self.selection_end = pos + len(self.chinese_text)
        
        self.setup_ui()
        
    def update_selection(self, new_start: int, new_end: int):
        """Update the selection and refresh the UI accordingly."""
        if new_start < 0 or new_end > len(self.context_text_full) or new_start >= new_end:
            return
            
        # Update selection
        self.selection_start = new_start
        self.selection_end = new_end
        
        # Get the new selected text
        new_text = self.context_text_full[self.selection_start:self.selection_end]
        
        # Store previous state
        old_text = self.chinese_edit.text()
        
        # Update the text fields
        self.chinese_edit.setText(new_text)
        new_hanviet = self.parent().dictionary_manager.convert_to_hanviet(new_text)
        self.hanviet_edit.setText(new_hanviet)
        
        if old_text != new_text:
            # Check if this is a new entry or editing existing one
            existing_def = None
            
            # First try the current dictionary type
            if self.dictionary_type:
                existing_def = self.parent().dictionary_manager.get_definition(
                    self.dictionary_type, new_text)
                    
            # If not found in current dictionary, check others
            if not existing_def:
                for dict_name in ["Names", "Names2", "VietPhrase"]:
                    if dict_name != self.dictionary_type:
                        definition = self.parent().dictionary_manager.get_definition(
                            dict_name, new_text)
                        if definition:
                            existing_def = definition
                            self.dictionary_type = dict_name
                            break
            
            # Update window title, definition, and mode
            self.is_edit = existing_def is not None
            title = f"Edit {self.dictionary_type}" if self.is_edit else f"Add to {self.dictionary_type}"
            self.setWindowTitle(title)
            
            # Set definition and apply proper case for new entries
            if existing_def:
                self.definition_edit.setText(existing_def)
            else:
                self.definition_edit.setText(new_hanviet)
                if self.dictionary_type in ["Names", "Names2"]:
                    self.apply_proper_case()
        
        # Update the preview
        self.context_text.setText(self.get_context_preview())
        self.update_nav_buttons()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        title = f"Edit {self.dictionary_type}" if self.is_edit else f"Add to {self.dictionary_type}"
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Chinese text
        chinese_layout = QHBoxLayout()
        chinese_label = QLabel("Chinese Text:")
        self.chinese_edit = QLineEdit(self.chinese_text)
        self.chinese_edit.setReadOnly(True)
        chinese_layout.addWidget(chinese_label)
        chinese_layout.addWidget(self.chinese_edit)
        layout.addLayout(chinese_layout)
        
        # Hán Việt
        hanviet_layout = QHBoxLayout()
        hanviet_label = QLabel("Hán Việt:")
        self.hanviet_edit = QLineEdit(self.hanviet)
        self.hanviet_edit.setReadOnly(True)
        hanviet_layout.addWidget(hanviet_label)
        hanviet_layout.addWidget(self.hanviet_edit)
        layout.addLayout(hanviet_layout)
        
        # Definition
        definition_layout = QHBoxLayout()
        definition_label = QLabel("Definition:")
        self.definition_edit = QLineEdit(self.definition)
        definition_layout.addWidget(definition_label)
        definition_layout.addWidget(self.definition_edit)
        layout.addLayout(definition_layout)
        
        # Case modification options
        case_layout = QGridLayout()
        
        # Upper case options
        upper_widget = QWidget()
        upper_layout = QVBoxLayout(upper_widget)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_label = QLabel("Uppercase:")
        upper_layout.addWidget(upper_label)
        
        self.upper_first = QPushButton("First Letter")
        self.upper_first.clicked.connect(lambda: self.modify_case("upper", 1))
        upper_layout.addWidget(self.upper_first)
        
        self.upper_two = QPushButton("First Two Letters")
        self.upper_two.clicked.connect(lambda: self.modify_case("upper", 2))
        upper_layout.addWidget(self.upper_two)
        
        self.upper_three = QPushButton("First Three Letters")
        self.upper_three.clicked.connect(lambda: self.modify_case("upper", 3))
        upper_layout.addWidget(self.upper_three)
        
        self.upper_all = QPushButton("All First Letters")
        self.upper_all.clicked.connect(lambda: self.modify_case("upper", -1))
        upper_layout.addWidget(self.upper_all)
        
        case_layout.addWidget(upper_widget, 0, 0)
        
        # Lower case options
        lower_widget = QWidget()
        lower_layout = QVBoxLayout(lower_widget)
        lower_layout.setContentsMargins(0, 0, 0, 0)
        lower_label = QLabel("Lowercase:")
        lower_layout.addWidget(lower_label)
        
        self.lower_first = QPushButton("First Letter")
        self.lower_first.clicked.connect(lambda: self.modify_case("lower", 1))
        lower_layout.addWidget(self.lower_first)
        
        self.lower_two = QPushButton("First Two Letters")
        self.lower_two.clicked.connect(lambda: self.modify_case("lower", 2))
        lower_layout.addWidget(self.lower_two)
        
        self.lower_three = QPushButton("First Three Letters")
        self.lower_three.clicked.connect(lambda: self.modify_case("lower", 3))
        lower_layout.addWidget(self.lower_three)
        
        self.lower_all = QPushButton("All First Letters")
        self.lower_all.clicked.connect(lambda: self.modify_case("lower", -1))
        lower_layout.addWidget(self.lower_all)
        
        case_layout.addWidget(lower_widget, 0, 1)
        
        # Proper case button
        proper_widget = QWidget()
        proper_layout = QVBoxLayout(proper_widget)
        proper_layout.setContentsMargins(0, 0, 0, 0)
        proper_label = QLabel("Other:")
        proper_layout.addWidget(proper_label)
        
        self.proper_case = QPushButton("Proper Case")
        self.proper_case.clicked.connect(self.apply_proper_case)
        proper_layout.addWidget(self.proper_case)
        
        case_layout.addWidget(proper_widget, 0, 2)
        
        layout.addLayout(case_layout)
            
        # Apply proper case by default only for new entries
        if not self.is_edit and self.dictionary_type in ["Names", "Names2"]:
            self.apply_proper_case()
            
        # Chinese text preview
        preview_layout = QHBoxLayout()
        preview_label = QLabel("Context:")
        self.context_widget = QWidget()
        context_layout = QHBoxLayout(self.context_widget)
        context_layout.setContentsMargins(0, 0, 0, 0)
        context_layout.setSpacing(5)
        
        self.prev_btn = QPushButton("<")
        self.prev_btn.setFixedWidth(30)
        self.prev_btn.setEnabled(False)  # Initially disabled
        self.prev_btn.clicked.connect(self.show_prev_context)
        
        # Ensure minimum width for better readability
        self.context_text = QLabel()
        self.context_text.setMinimumWidth(300)
        self.context_text.setWordWrap(True)
        self.context_text.setText(self.get_context_preview())
        self.context_text.setTextFormat(Qt.RichText)
        self.context_text.setStyleSheet("""
            QLabel {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #f8f9fa;
                font-size: 14px;
                min-height: 40px;
            }
        """)
        
        self.next_btn = QPushButton(">")
        self.next_btn.setFixedWidth(30)
        self.next_btn.setEnabled(False)  # Initially disabled
        self.next_btn.clicked.connect(self.show_next_context)
        
        context_layout.addWidget(self.prev_btn)
        context_layout.addWidget(self.context_text)
        context_layout.addWidget(self.next_btn)
        
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.context_widget)
        layout.addLayout(preview_layout)
        
        # Enable navigation buttons if we have context
        if self.context_text_full:
            self.update_nav_buttons()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def modify_case(self, case_type: str, num_words: int):
        """Modify the case of the first letter of specified words."""
        text = self.definition_edit.text()
        if not text:
            return
            
        words = text.split()
        if not words:
            return
            
        if num_words == -1:  # All words
            # Only modify first letter of each word
            for i in range(len(words)):
                if words[i]:
                    if case_type == "upper":
                        words[i] = words[i][0].upper() + words[i][1:]
                    else:
                        words[i] = words[i][0].lower() + words[i][1:]
        else:
            # Modify first letter of specified number of words
            for i in range(min(num_words, len(words))):
                if words[i]:
                    if case_type == "upper":
                        words[i] = words[i][0].upper() + words[i][1:]
                    else:
                        words[i] = words[i][0].lower() + words[i][1:]
        
        self.definition_edit.setText(" ".join(words))
    
    def apply_proper_case(self):
        """Apply proper case to the definition text."""
        text = self.definition_edit.text()
        if not text:
            return
            
        # Split on spaces and handle each word
        words = text.split()
        proper_words = []
        for word in words:
            if word:
                proper_words.append(word[0].upper() + word[1:].lower())
        
        self.definition_edit.setText(" ".join(proper_words))
    
    def get_context_preview(self) -> str:
        """Get the context preview with highlighting."""
        if not self.context_text_full or self.selection_start < 0:
            return "<html><body><i>No context available</i></body></html>"
            
        # Calculate window start and end positions
        window_start = max(0, self.selection_start - self.context_window_size)
        window_end = min(len(self.context_text_full), 
                        self.selection_end + self.context_window_size)
        
        # Get the visible portion of text
        visible_text = self.context_text_full[window_start:window_end]
        
        # Create the highlighted version
        highlight_start = self.selection_start - window_start
        highlight_end = self.selection_end - window_start
        text = visible_text[:highlight_start]
        text += f'<span style="background-color: #ffd700;">'
        text += visible_text[highlight_start:highlight_end]
        text += '</span>'
        text += visible_text[highlight_end:]
        
        # Add navigation indicators if there's more text
        if window_start > 0:
            text = "..." + text
        if window_end < len(self.context_text_full):
            text = text + "..."
            
        return f'<html><body>{text}</body></html>'
        
    def update_nav_buttons(self):
        """Update navigation button states."""
        self.prev_btn.setEnabled(self.selection_start > 0)
        self.next_btn.setEnabled(self.selection_end < len(self.context_text_full))
        
    def show_prev_context(self):
        """Expand selection to include previous character."""
        if self.selection_start > 0:
            self.update_selection(self.selection_start - 1, self.selection_end)
            
    def show_next_context(self):
        """Expand selection to include next character."""
        if self.selection_end < len(self.context_text_full):
            self.update_selection(self.selection_start, self.selection_end + 1)
    
    def get_values(self):
        """Get the dialog values."""
        return {
            "chinese_text": self.chinese_edit.text(),
            "hanviet": self.hanviet_edit.text(),
            "definition": self.definition_edit.text()
        }
    
    def accept(self):
        """Handle dialog acceptance."""
        # Emit signal with the dictionary filename
        filename = f"{self.dictionary_type}.txt"
        self.dictionary_updated.emit(filename)
        super().accept()
