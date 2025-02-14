import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget
import chardet

class FileHandler:
    def __init__(self):
        self.parent = QWidget()
        # Common Chinese encodings to try in order of preference
        self.chinese_encodings = ['utf-8', 'gb18030', 'gbk', 'gb2312', 'big5']
        self.last_detected_encoding = None  # Track successful encoding

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Open Text File", "", "Text Files (*.txt);;All Files (*)")
        return file_path

    def read_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                
                # If we successfully used an encoding before, try it first
                if self.last_detected_encoding:
                    try:
                        content = raw_data.decode(self.last_detected_encoding)
                        if any('\u4e00' <= char <= '\u9fff' for char in content):
                            return content
                    except UnicodeDecodeError:
                        pass
                
                # Then try chardet
                encoding_result = chardet.detect(raw_data)
                if encoding_result and encoding_result['confidence'] > 0.7:
                    try:
                        content = raw_data.decode(encoding_result['encoding'])
                        if any('\u4e00' <= char <= '\u9fff' for char in content):
                            self.last_detected_encoding = encoding_result['encoding']
                            return content
                    except UnicodeDecodeError:
                        pass
                
                # Finally try each Chinese encoding
                for encoding in self.chinese_encodings:
                    try:
                        content = raw_data.decode(encoding)
                        # Basic validation - check if the text contains Chinese characters
                        if any('\u4e00' <= char <= '\u9fff' for char in content):
                            self.last_detected_encoding = encoding
                            return content
                    except UnicodeDecodeError:
                        continue
                
                # If all attempts fail, show error
                QMessageBox.critical(self.parent, "Error", "Could not decode file with any supported encoding.")
                return None
                
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Could not read file: {e}")
            return None

    def get_file_encoding(self, file_path):
        """Get the encoding of a file without reading its entire content."""
        try:
            with open(file_path, 'rb') as file:
                # Read only first 4KB for encoding detection
                raw_data = file.read(4096)
                
                # Try chardet first with higher confidence threshold
                encoding_result = chardet.detect(raw_data)
                if encoding_result and encoding_result['confidence'] > 0.8:
                    try:
                        raw_data.decode(encoding_result['encoding'])
                        # Special case: if detected as GB18030 but actually GB2312
                        if encoding_result['encoding'].lower() == 'gb18030':
                            try:
                                raw_data.decode('gb2312')
                                return 'gb2312'  # If it can be decoded as GB2312, prefer that
                            except UnicodeDecodeError:
                                pass
                        return encoding_result['encoding']
                    except UnicodeDecodeError:
                        pass
                
                # Try UTF-8 explicitly since it's most common
                try:
                    raw_data.decode('utf-8')
                    return 'utf-8'
                except UnicodeDecodeError:
                    pass
                
                # Try each Chinese encoding
                for encoding in self.chinese_encodings:
                    try:
                        raw_data.decode(encoding)
                        # Special case: if trying GB18030 and GB2312 also works
                        if encoding == 'gb18030':
                            try:
                                raw_data.decode('gb2312')
                                return 'gb2312'  # If it can be decoded as GB2312, prefer that
                            except UnicodeDecodeError:
                                pass
                        return encoding
                    except UnicodeDecodeError:
                        continue
                
                return "Unknown"
                
        except Exception:
            return "Unknown"
