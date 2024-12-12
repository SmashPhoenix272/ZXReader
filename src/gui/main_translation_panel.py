from PyQt5.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from typing import Optional
from src.core.chapter_manager import ChapterManager
from src.core.translation_manager import TranslationManager

class MainTranslationPanel(QWidget):
    def __init__(self, parent: Optional[QWidget], chapter_manager: ChapterManager, translation_manager: TranslationManager):
        super().__init__(parent)
        self.chapter_manager = chapter_manager
        self.translation_manager = translation_manager
        self.text_edit = QTextEdit()
        self.show_original_text = False
        self.toggle_button = QPushButton("Show Original Text")
        self.toggle_button.clicked.connect(self.toggle_text_display)

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.toggle_button)
        layout.addLayout(button_layout)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def set_chapter_text(self, chapter_index: int) -> None:
        original_text = self.chapter_manager.get_chapter_text(chapter_index)
        if original_text:
            paragraphs = original_text.splitlines()
            translated_paragraphs = [self.translation_manager.translate_text(p) for p in paragraphs]
            if self.show_original_text:
                combined_text = ""
                for original, translated in zip(paragraphs, translated_paragraphs):
                    combined_text += f"{original}\n{translated}\n\n"
                self.text_edit.setText(combined_text)
            else:
                self.text_edit.setText("\n\n".join(translated_paragraphs))

    def set_text(self, text: str) -> None:
        self.chapter_manager.set_text(text)
        if self.chapter_manager.chapters:
            self.set_chapter_text(0)
        else:
            self.text_edit.setText("")

    def toggle_text_display(self):
        self.show_original_text = not self.show_original_text
        if self.show_original_text:
            self.toggle_button.setText("Hide Original Text")
        else:
            self.toggle_button.setText("Show Original Text")
        if self.chapter_manager.chapters:
            self.set_chapter_text(0)
