from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTextEdit
from PyQt5.QtCore import pyqtSlot

class DictionaryPanel(QWidget):
    def __init__(self, dictionary_manager):
        super().__init__()
        self.dictionary_manager = dictionary_manager
        layout = QVBoxLayout()
        self.definition_display = QTextEdit()
        self.definition_display.setReadOnly(True)
        layout.addWidget(self.definition_display)
        self.setLayout(layout)

    @pyqtSlot(str)
    def lookup_word(self, word):
        definitions = self.dictionary_manager.lookup(word)
        if definitions:
            self.definition_display.setText("\n".join(definitions))
        else:
            self.definition_display.setText("No definition found.")

    def clear_content(self):
        self.definition_display.clear()
