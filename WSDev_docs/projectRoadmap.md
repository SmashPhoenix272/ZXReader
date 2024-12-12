## Project Goals

-   Develop a fully functional Chinese novel reader application (ZXReader) as specified in `ZXR.md`.
-   Integrate QTEngine for Sino-Vietnamese translation.
-   Implement chapter management, dictionary lookup, and a customizable UI.
-   Ensure the application is user-friendly, efficient, and robust.

## Key Features

-   File Handling: Support loading text files with various encodings.
-   Chapter Detection: Automatically detect chapters using predefined regex methods.
-   Reading Functionality: Allow users to select and read chapters.
-   Translation: Provide Sino-Vietnamese translation using QTEngine.
-   Dictionary Lookup: Enable users to look up definitions from multiple dictionaries.
-   UI Customization: Offer options for themes, fonts, and resizable panels.
-   Auto Select First Chapter: Automatically select the first chapter when chapters are detected.
-   Highlight Selected Chapter: Highlight the selected chapter in the chapter panel.

## Completion Criteria

-   All core features implemented and tested.
-   UI meets design and responsiveness requirements.
-   Application handles errors gracefully.
-   Documentation is complete and up-to-date.

## Progress Tracker

-   [x] Core Framework Setup
-   [x] File Handling and Chapter Detection
-   [x] Reading and Translation
-   [ ] Dictionary Lookup
-   [ ] UI Enhancements and Customization
-   [ ] Testing and Refinement

## Completed Tasks

-   Implemented the `ChapterManager` class in `src/core/chapter_manager.py`.
-   Implemented the `FileHandler` class in `src/core/file_handler.py`.
-   Implemented the `TranslationManager` class in `src/core/translation_manager.py`.
-   Implemented the `DictionaryManager` class in `src/core/dictionary_manager.py`.
-   Implemented the `MainWindow` class in `src/gui/main_window.py`.
-   Implemented the `FileInfoPanel` class in `src/gui/file_info_panel.py`.
-   Implemented the `MainTranslationPanel` class in `src/gui/main_translation_panel.py`.
-   Implemented the `DictionaryPanel` class in `src/gui/dictionary_panel.py`.
-   Passed `file_handler` and `translation_manager` to `MainWindow` constructor.
-   Implemented the `ChapterPanel` class in `src/gui/chapter_panel.py`.
-   Integrated the `ChapterPanel` with the `ChapterManager` to display the list of chapters.
-   Implemented chapter selection and display in the `MainTranslationPanel`.
-   Implemented a dropdown menu for chapter detection methods.
-   Implemented chapter navigation.
-   Implemented file loading with encoding detection.
-   Added "Hiển thị toàn bộ" option to chapter selection dropdown.
-   Modified `ChapterManager` to handle "Hiển thị toàn bộ" option.
-   Implemented auto selection of the first chapter when chapters are detected.
-   Highlighted the selected chapter in the chapter panel.
-   Ran `src/main.py` and addressed the data loading warnings (keeping the warnings as they are).
