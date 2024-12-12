import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget
import chardet

class FileHandler:
    def __init__(self):
        self.parent = QWidget()

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Open Text File", "", "Text Files (*.txt);;All Files (*)")
        return file_path

    def read_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                encoding_result = chardet.detect(raw_data)
                encoding = encoding_result['encoding']
                if encoding:
                    try:
                        content = raw_data.decode(encoding)
                        return content
                    except UnicodeDecodeError:
                        QMessageBox.critical(self.parent, "Error", f"Could not decode file with encoding: {encoding}")
                        return None
                else:
                    QMessageBox.critical(self.parent, "Error", "Could not detect file encoding.")
                    return None
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Could not read file: {e}")
            return None
