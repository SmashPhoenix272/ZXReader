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
                 dictionary_type="", is_edit=False):
        super().__init__(parent)
        self.chinese_text = chinese_text
        self.hanviet = hanviet
        self.definition = definition
        self.dictionary_type = dictionary_type
        self.is_edit = is_edit
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Add to Dictionary" if not self.is_edit else "Edit Dictionary Entry")
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
        
        # Case modification options for Names/Names2
        if self.dictionary_type in ["Names", "Names2"]:
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
            
            self.upper_two = QPushButton("First Two")
            self.upper_two.clicked.connect(lambda: self.modify_case("upper", 2))
            upper_layout.addWidget(self.upper_two)
            
            self.upper_three = QPushButton("First Three")
            self.upper_three.clicked.connect(lambda: self.modify_case("upper", 3))
            upper_layout.addWidget(self.upper_three)
            
            self.upper_all = QPushButton("All Letters")
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
            
            self.lower_two = QPushButton("First Two")
            self.lower_two.clicked.connect(lambda: self.modify_case("lower", 2))
            lower_layout.addWidget(self.lower_two)
            
            self.lower_three = QPushButton("First Three")
            self.lower_three.clicked.connect(lambda: self.modify_case("lower", 3))
            lower_layout.addWidget(self.lower_three)
            
            self.lower_all = QPushButton("All Letters")
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
            
            # Apply proper case by default for Names/Names2
            self.apply_proper_case()
        
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
    
    def modify_case(self, case_type: str, num_chars: int):
        """Modify the case of the definition text."""
        text = self.definition_edit.text()
        if not text:
            return
            
        if num_chars == -1:  # All letters
            if case_type == "upper":
                modified = text.upper()
            else:
                modified = text.lower()
        else:
            if case_type == "upper":
                modified = text[:num_chars].upper() + text[num_chars:]
            else:
                modified = text[:num_chars].lower() + text[num_chars:]
        
        self.definition_edit.setText(modified)
    
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
