from PyQt5.QtWidgets import QTextEdit, QWidget, QVBoxLayout

class MainTranslationPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.text_edit = QTextEdit()
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def set_text(self, text):
        self.text_edit.setText(text)
