from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QScrollArea, QFrame
)
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QFont, QTextCharFormat, QTextCursor

class DictionaryPanel(QWidget):
    def __init__(self, dictionary_manager):
        super().__init__()
        self.dictionary_manager = dictionary_manager
        self.setup_ui()

    def setup_ui(self):
        """Set up the dictionary panel UI."""
        layout = QVBoxLayout()

        # Hán Việt display
        self.hanviet_label = QLabel("Hán Việt:")
        self.hanviet_label.setFont(QFont("Open Sans", 10))
        self.hanviet_display = QTextEdit()
        self.hanviet_display.setReadOnly(True)
        self.hanviet_display.setMaximumHeight(80)
        self.hanviet_display.setFont(QFont("Open Sans", 10))

        # Definition display
        self.definition_display = QTextEdit()
        self.definition_display.setReadOnly(True)
        self.definition_display.setMinimumHeight(200)
        
        # Set up fonts
        default_font = QFont("Open Sans", 10)
        self.definition_display.setFont(default_font)
        
        # Create text formats for different parts
        self.chinese_format = QTextCharFormat()
        self.chinese_format.setFontWeight(QFont.Bold)
        self.chinese_format.setFontPointSize(12)
        
        self.dict_name_format = QTextCharFormat()
        self.dict_name_format.setFontPointSize(10)
        
        self.definition_format = QTextCharFormat()
        self.definition_format.setFontPointSize(10)
        
        self.pinyin_format = QTextCharFormat()
        self.pinyin_format.setFontPointSize(10)
        self.pinyin_format.setFontItalic(True)
        
        self.hanviet_format = QTextCharFormat()
        self.hanviet_format.setFontPointSize(10)
        self.hanviet_format.setFontWeight(QFont.Bold)
        
        self.separator_format = QTextCharFormat()
        self.separator_format.setFontPointSize(8)
        
        # Set margins and spacing
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Add widgets to layout
        layout.addWidget(self.hanviet_label)
        layout.addWidget(self.hanviet_display)
        layout.addWidget(self.definition_display)
        self.setLayout(layout)

    def format_definition(self, dictionary_name: str, definition: str) -> str:
        """Format a definition with proper line breaks and indentation."""
        # Handle special formatting for ThieuChuu and LacViet dictionaries
        if dictionary_name in ['ThieuChuu', 'LacViet']:
            # Convert literal \t to actual tab characters
            lines = definition.replace('\\t', '\t').split('\n')
            formatted_lines = []
            for line in lines:
                formatted_lines.append(line)
            return '\n'.join(formatted_lines)
        else:
            # For other dictionaries, just return the definition as is
            return definition

    def add_separator(self, cursor):
        """Add a separator line between definitions."""
        cursor.insertText("------------------------------------------\n", self.separator_format)

    def format_lacviet_definition(self, definition: str, cursor: QTextCursor):
        """Format LacViet dictionary definition with special styling."""
        lines = definition.split('\n')
        for line in lines:
            # Clean up line and check for ✚ character
            line = line.strip()
            if line == 'n':
                cursor.insertText('\n', self.definition_format)
            elif '✚' in line:
                # Remove 'n' before ✚ if present
                line = line.replace('n✚', '✚')
                
                # Extract pinyin and Hán Việt
                if '[' in line and ']' in line:
                    # Split at the closing bracket
                    pre_bracket, post_bracket = line.split(']', 1)
                    pinyin = pre_bracket + ']'  # Include the closing bracket
                    cursor.insertText(pinyin, self.pinyin_format)
                    
                    remaining = post_bracket.strip()
                    if "Hán Việt:" in remaining:
                        parts = remaining.split("Hán Việt:", 1)
                        cursor.insertText(" Hán Việt: ", self.dict_name_format)
                        
                        # Handle the rest of the definition
                        rest = parts[1].strip()
                        # Split into hanviet word and meanings if there are meanings
                        if ' ' in rest:
                            hanviet, meanings = rest.split(' ', 1)
                            cursor.insertText(hanviet, self.hanviet_format)
                            cursor.insertText(" " + meanings, self.definition_format)
                        else:
                            cursor.insertText(rest, self.hanviet_format)
                        cursor.insertText("\n")
                    else:
                        cursor.insertText(f" {remaining}\n", self.definition_format)
            else:
                # Handle 'n' for newline and t{number} for indentation
                if line.strip() == 'n':
                    cursor.insertText('\n', self.definition_format)
                elif line.startswith('t') and len(line) > 1 and line[1].isdigit():
                    # Keep number after indentation
                    number = line[1]
                    text = line[2:].strip()
                    # Check if text already starts with dot
                    if text.lstrip().startswith('.'):
                        text = text.lstrip()[1:].lstrip()  # Remove leading dot and whitespace
                    cursor.insertText(f"    {number}. {text}\n", self.definition_format)
                else:
                    cursor.insertText(f"{line}\n", self.definition_format)

    def format_thieuchuu_definition(self, definition: str, cursor: QTextCursor):
        """Format ThieuChuu dictionary definition with special styling."""
        lines = definition.split('\n')
        for i, line in enumerate(lines):
            if i == 0:  # First line with word and pinyin
                if '[' in line:
                    parts = line.split('[')
                    if len(parts) == 2:
                        word = parts[0].strip()
                        cursor.insertText(f"{word.upper()} ", self.hanviet_format)  # Word in uppercase and bold
                        cursor.insertText(f"[{parts[1]} \n", self.pinyin_format)  # Pinyin in italics
                else:
                    cursor.insertText(f"{line}\n", self.definition_format)
            else:
                # Handle 'n' for newline and t{number} for indentation
                if line.strip() == 'n':
                    cursor.insertText('\n', self.definition_format)
                elif line.startswith('t') and len(line) > 1 and line[1].isdigit():
                    # Keep number after indentation
                    number = line[1]
                    text = line[2:].strip()
                    # Check if text already starts with dot
                    if text.lstrip().startswith('.'):
                        text = text.lstrip()[1:].lstrip()  # Remove leading dot and whitespace
                    cursor.insertText(f"    {number}. {text}\n", self.definition_format)
                else:
                    cursor.insertText(f"{line}\n", self.definition_format)

    def format_babylon_definition(self, definition: str, cursor: QTextCursor):
        """Format Babylon/Cedict dictionary definition with special styling."""
        cursor.insertText(definition.strip() + '\n', self.definition_format)

    def format_cedict_definition(self, definition: str, cursor: QTextCursor):
        """Format Cedict dictionary definition with special styling."""
        try:
            # Convert string representation of dict back to dict
            entry = eval(definition)  # Safe since we control the input format
            
            # Display traditional and simplified if different
            if entry['traditional'] != entry['simplified']:
                cursor.insertText(f"{entry['traditional']}/{entry['simplified']} ", self.chinese_format)
            else:
                cursor.insertText(f"{entry['traditional']} ", self.chinese_format)
            
            # Display pinyin
            cursor.insertText(f"[{entry['pinyin']}] ", self.pinyin_format)
            
            # Display definition
            cursor.insertText(f"{entry['definition']}\n", self.definition_format)
        except Exception as e:
            print(f"Error formatting Cedict definition: {e}")
            cursor.insertText(f"{definition}\n", self.definition_format)

    @pyqtSlot(str)
    def lookup_word(self, word: str):
        """
        Look up a word and display its definitions.
        
        Args:
            word (str): The word to look up
        """
        # Display Hán Việt conversion first
        self.hanviet_display.clear()
        hanviet_cursor = self.hanviet_display.textCursor()
        
        # Convert to Hán Việt using character-by-character mapping
        hanviet_text = self.dictionary_manager.convert_to_hanviet(word)
        
        # Display original text and Hán Việt
        hanviet_cursor.insertText(word + "\n", self.chinese_format)
        hanviet_cursor.insertText(hanviet_text, self.hanviet_format)

        # Clear and display dictionary definitions
        self.definition_display.clear()
        cursor = self.definition_display.textCursor()
        
        # Get all prefixes of the word
        prefixes = [word[0:i] for i in range(1, len(word) + 1)]
        
        # Process each prefix from longest to shortest
        for prefix in reversed(prefixes):
            definitions = self.dictionary_manager.lookup_word(prefix)
            if definitions:
                # First show Names
                if 'Names' in definitions:
                    cursor.insertText(f"{prefix} (Names) ", self.dict_name_format)
                    cursor.insertText(definitions['Names'] + '\n', self.definition_format)
                    self.add_separator(cursor)
                
                # Then show Names2
                if 'Names2' in definitions:
                    cursor.insertText(f"{prefix} (Names2) ", self.dict_name_format)
                    cursor.insertText(definitions['Names2'] + '\n', self.definition_format)
                    self.add_separator(cursor)
                
                # Then show VietPhrase
                if 'VietPhrase' in definitions:
                    cursor.insertText(f"{prefix} (VietPhrase) ", self.dict_name_format)
                    cursor.insertText(definitions['VietPhrase'] + '\n', self.definition_format)
                    self.add_separator(cursor)
                
                # Then show LacViet if it has an exact match
                if 'LacViet' in definitions:
                    cursor.insertText(f"{prefix} (Lạc Việt)\n", self.dict_name_format)
                    self.format_lacviet_definition(definitions['LacViet'], cursor)
                    self.add_separator(cursor)

                # Then show ThieuChuu if it has an exact match
                if 'ThieuChuu' in definitions:
                    cursor.insertText(f"{prefix} (Thiều Chửu) ", self.dict_name_format)
                    self.format_thieuchuu_definition(definitions['ThieuChuu'], cursor)
                    self.add_separator(cursor)

                # Then show Cedict
                if 'Cedict' in definitions:
                    cursor.insertText(f"{prefix} (CC-CEDICT) ", self.dict_name_format)
                    self.format_cedict_definition(definitions['Cedict'], cursor)
                    self.add_separator(cursor)
                
                # Then show Babylon
                if 'Babylon' in definitions:
                    cursor.insertText(f"{prefix} (Babylon) ", self.dict_name_format)
                    self.format_babylon_definition(definitions['Babylon'], cursor)
                    self.add_separator(cursor)


    def clear_content(self):
        """Clear the panel content."""
        self.definition_display.clear()

    def highlight_search_results(self, text: str):
        """
        Highlight search results in the definition display.
        
        Args:
            text (str): The text to highlight
        """
        if not text:
            return
            
        # Create format for highlighted text
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(Qt.yellow)
        
        # Find and highlight all occurrences
        cursor = self.definition_display.textCursor()
        cursor.movePosition(QTextCursor.Start)
        while cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor):
            if cursor.selectedText().lower() == text.lower():
                cursor.mergeCharFormat(highlight_format)
            cursor.movePosition(QTextCursor.Right)
