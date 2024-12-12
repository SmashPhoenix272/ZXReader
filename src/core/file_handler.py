import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget

class FileHandler:
    def __init__(self):
        self.parent = QWidget()

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Open Text File", "", "Text Files (*.txt);;All Files (*)")
        return file_path

    def read_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Could not read file: {e}")
            return None
