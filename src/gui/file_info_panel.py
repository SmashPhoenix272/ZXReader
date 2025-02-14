import os
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout
)
from src.core.file_handler import FileHandler

class FileInfoPanel(QWidget):
    def __init__(self, parent, translation_manager):
        super().__init__()
        self.translation_manager = translation_manager
        self.file_handler = FileHandler()  # Create instance of FileHandler
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.file_name_label = QLabel("File Name: ")
        self.translated_file_name_label = QLabel("Translated File Name: ")
        self.encoding_label = QLabel("Encoding: ")
        self.file_size_label = QLabel("File Size: ")

        layout.addWidget(self.file_name_label)
        layout.addWidget(self.translated_file_name_label)
        layout.addWidget(self.encoding_label)
        layout.addWidget(self.file_size_label)

    def set_file_info(self, file_path):
        file_name = os.path.basename(file_path)
        translated_file_name = self.translation_manager.translate_text(file_name)
        
        # Use FileHandler's encoding detection
        encoding_name = self.file_handler.get_file_encoding(file_path)

        file_size = os.path.getsize(file_path)
        self.file_name_label.setText(f"File Name: {file_name}")
        self.translated_file_name_label.setText(f"Translated File Name: {translated_file_name}")
        self.encoding_label.setText(f"Encoding: {encoding_name}")
        self.file_size_label.setText(f"File Size: {file_size} bytes")
