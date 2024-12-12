from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout
)

class FileInfoPanel(QWidget):
    def __init__(self, file_handler, translation_manager):
        super().__init__()
        self.file_handler = file_handler
        self.translation_manager = translation_manager
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

    def set_file_info(self, file_path, translated_file_path):
        self.file_name_label.setText(f"File Name: {file_path}")
        self.translated_file_name_label.setText(f"Translated File Name: {translated_file_path}")
        #self.encoding_label.setText(f"Encoding: {encoding}")
        #self.file_size_label.setText(f"File Size: {file_size}")
