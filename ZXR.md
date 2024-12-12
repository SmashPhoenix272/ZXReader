## ZXReader Development Prompt - v2.1

  

**Prompt Version:** 2.1

**Last Updated:** 2023-11-21

**Changelog:**

-   Reorganized sections for better coherence.
-   Added definitions for technical terms.
-   Specified Python with PyQt as the programming language.
-   Provided more detailed UI specifications.
-   Outlined error handling procedures.
-   Included edge cases for chapter detection and dictionary lookup.
-   Broke down the project into milestones.
-   Removed redundant sections.
-   Added a section on feature relationships.
-   Added a glossary of terms.
-   Added more specific guidelines for UI aesthetics.
-   Clarified how to handle failed chapter detection.
-   Specified the behavior for triggering dictionary lookups.
-   Provided more details on custom font loading.
-   Added a general guideline on error handling.

  

### 1. Introduction

  

This document outlines the requirements for developing ZXReader, a software application designed to read Chinese novels and text files, translating content to Sino-Vietnamese using the QTEngine. The goal is to create a user-friendly and efficient reader with robust features for translation, chapter management, dictionary lookup, and customization.

  

### 2. Definitions

  

-   **Sino-Vietnamese:** A vocabulary of the Vietnamese language that borrows from the Chinese language.
-   **QTEngine:** A translation engine that translates Chinese to Sino-Vietnamese based on the longest prefix match using dictionary data.
-   **Trie:** A tree-like data structure used for efficient retrieval of a key in a dataset of strings.

  

### 3. Features

  

#### 3.1. File Handling

  

-   **Description:** ZXReader must support loading text files in various encodings (UTF-8, GBK, etc.) using File Dialogs.
-   **Input:** User selects a text file through a file dialog.
-   **Output:** The selected file is loaded into ZXReader.
-   **Error Handling:**
    -   If the file cannot be opened, display an error message to the user.
    -   If the file encoding is not supported, display an error message and attempt to auto-detect the encoding.
-   **File Info Panel:** Display the following information:
    -   File name
    -   Translated file name (using QTEngine)
    -   Encoding
    -   File size

  

#### 3.2. Chapter Detection

  

-   **Description:** Implement a chapter panel that detects chapters using predefined regex methods from `detect_chapters_methods.py` located in the `src` folder.
-   **Input:** The loaded text file.
-   **Output:** A list of detected chapters with translated titles.
-   **Error Handling:**
    -   If no chapters are detected, display a message to the user.
    -   If a chapter title cannot be translated, display the original Chinese title.
    -   If a selected chapter detection method fails to detect any chapters, display a message to the user indicating that no chapters were found with the current method and suggest trying a different method or manually defining chapters.
-   **Chapter Panel:**
    -   A dropdown menu to select detection methods.
    -   Dynamically update the chapter list when the detection method is changed.
    -   Translate chapter titles using QTEngine.
    -   Reset and retranslate chapter titles if the user changes the novel or detection method.
    -   Highlight the selected chapter.
    -   Next/previous buttons to navigate to the selected chapter.
-   **Edge Cases:**
    -   Handle chapters with no titles or unusual formatting.
    -   Allow users to manually edit chapter titles.

  

#### 3.3. Reading Functionality

  

-   **Description:** Users should be able to select chapters to read, with the selected chapter's text displayed in a main translation panel.
-   **Input:** User selects a chapter from the chapter panel.
-   **Output:** The selected chapter's text is displayed in the main translation panel.
-   **Error Handling:**
    -   If the selected chapter cannot be loaded, display an error message.
-   **Main Translation Panel:**
    -   Default to showing translated text (Sino-Vietnamese).
    -   Include a toggle option to display both Chinese and translated text in parallel.

  

#### 3.4. Dictionary Lookup

  

-   **Description:** Users must be able to select characters/words/phrases and check definitions against QTEngine dictionaries (Names, Names2, VietPhrase) and additional dictionaries like those in the `dictionaries` folder.
-   **Input:** User selects text in the main translation panel.
-   **Output:** Definitions from the selected dictionaries are displayed in the dictionary lookup panel.
-   **Error Handling:**
    -   If no definition is found, display a message to the user.
-   **Dictionary Lookup Panel:**
    -   Display definitions from QTEngine dictionaries (Names, Names2, VietPhrase).
    -   Load Babylon, ThieuChuu, and LacViet dictionaries (UTF-8 BOM) using Trie models.
    -   Handle line breaks in ThieuChuu and LacViet dictionary entries (e.g., 龢=hòa [huo2]\n\t1. Ðiều hòa, hợp.).
    -   Allow users to search for specific words or phrases.
-   **Triggering Lookup:**
    -   When the user double-clicks a word or selects a phrase in the Main Translation Panel, automatically trigger a dictionary lookup and display the results in the Dictionary Lookup Panel.
-   **Custom Dictionary Syncing:**
    -   Allow users to load a custom `Names2.txt` file.
    -   Sync the custom `Names2.txt` with QTEngine’s `Names2.txt`.

  

### 4. UI Requirements

  

-   **Design:** Modern, user-friendly, with options for light/dark themes or a book/wood theme.
-   **Icons:** Use icons and indicators for various functions.
-   **Resizable Panels:** Allow users to adjust the size of each panel.
-   **Custom Fonts:**
    -   Support custom fonts that users can add to a `fonts` folder.
    -   Load custom fonts from settings.
    -   ZXReader should support common font formats like TTF and OTF. If a font file cannot be loaded, display an error message to the user.
-   **Responsiveness:** Ensure the UI is responsive on different screen sizes.
-   **UI CAN'T BE UGLY.**
-   **Aesthetics:**
    -   Use a clean and modern design language.
    -   Ensure good contrast between text and background.
    -   Use a consistent color scheme throughout the application.
    -   Avoid cluttered layouts and excessive use of animations.
-   **Specifics:**
    -   **Main Window:**
        -   Minimum size: 800x600 pixels.
        -   Resizable: Yes.
    -   **File Info Panel:**
        -   Position: Top-left.
        -   Width: 20% of the main window width.
        -   Display: File name, translated file name, encoding, file size.
    -   **Chapter Panel:**
        -   Position: Left, below the File Info Panel.
        -   Width: 20% of the main window width.
        -   Features: Dropdown for detection methods, chapter list, next/previous buttons.
    -   **Main Translation Panel:**
        -   Position: Center.
        -   Width: 60% of the main window width.
        -   Features: Toggle for parallel display, text area for displaying chapter content.
    -   **Dictionary Lookup Panel:**
        -   Position: Right.
        -   Width: 20% of the main window width.
        -   Features: Search bar, definition display area.

  

### 5. Technical Details

  

-   **Programming Language:** Python with PyQt for the GUI.
-   **Translation Engine:** QTEngine (integrated as described below).
-   **Absolute Paths in QTEngine:**

    ```python
    # Add the QTEngine directory to Python path
    current_dir = os.path.dirname(__file__)
    qt_engine_path = os.path.join(current_dir, 'QTEngine')
    sys.path.append(qt_engine_path)
    os.chdir(qt_engine_path)  # Change working directory to QTEngine folder

    # Initialize QTEngine
    qt_engine = QTEngine()
    ```

-   **File Dialogs:**

    ```python
    import sys
    from PyQt5.QtWidgets import QApplication, QFileDialog

    def open_file_dialog():
        app = QApplication(sys.argv)
        file_path, _ = QFileDialog.getOpenFileName(None, 'Open Text File', '', 'Text Files (*.txt);;All Files (*)')
        if file_path:
            # Use the absolute path returned by the file dialog
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
        return None
    ```

-   **Error Handling:**
    -   Implement robust error handling throughout the application. All errors should be handled gracefully, and informative error messages should be displayed to the user when appropriate. Log errors to a file for debugging purposes.

  

### 6. Feature Relationships

  

-   **File Handling** provides input to **Chapter Detection** and **Reading Functionality**.
-   **Chapter Detection** provides input to **Reading Functionality**.
-   **Reading Functionality** interacts with **Dictionary Lookup**.
-   **Dictionary Lookup** utilizes data from **File Handling** (for custom dictionaries).

  

### 7. Milestones

  

1. **Core Framework:**
    -   Set up the project structure.
    -   Implement basic UI layout with resizable panels.
    -   Integrate QTEngine.
2. **File Handling and Chapter Detection:**
    -   Implement file loading with encoding detection.
    -   Develop chapter detection using `detect_chapters_methods.py`.
    -   Create the File Info and Chapter panels.
3. **Reading and Translation:**
    -   Implement the main translation panel.
    -   Enable parallel display of Chinese and translated text.
4. **Dictionary Lookup:**
    -   Develop the dictionary lookup panel.
    -   Load and integrate external dictionaries.
    -   Implement custom dictionary syncing.
5. **UI Enhancements and Customization:**
    -   Implement light/dark/book/wood themes.
    -   Add support for custom fonts.
    -   Ensure UI responsiveness.
6. **Testing and Refinement:**
    -   Conduct thorough testing.
    -   Address bugs and user feedback.

  

### 8. Potential Improvements or Additions

  

-   **User Experience Enhancements:**
    -   Include keyboard shortcuts for common actions.
    -   Provide a user tutorial or guide within the application.
-   **Performance Considerations:**
    -   Optimize loading times for large text files.
    -   Implement caching mechanisms for frequently accessed data.

  

### 9. Glossary of Terms

  

-   **Sino-Vietnamese:** A vocabulary of the Vietnamese language that borrows from the Chinese language.
-   **QTEngine:** A translation engine that translates Chinese to Sino-Vietnamese based on the longest prefix match using dictionary data.
-   **Trie:** A tree-like data structure used for efficient retrieval of a key in a dataset of strings.
-   **Regex:** Regular expression, a sequence of characters that define a search pattern.
-   **UTF-8 BOM:** Byte Order Mark, a special marker added at the beginning of a UTF-8 encoded file.

  

### 10. Evaluation

  

**Strengths:**

-   Detailed feature descriptions with clear input/output specifications.
-   Specific instructions on UI design and technical implementation.
-   Comprehensive error handling and edge case considerations.
-   Well-organized structure with clear milestones.
-   Addresses ambiguities from previous versions.

  

**Weaknesses:**

-   Could still benefit from more examples for complex features.
-   Some sections might be too verbose for an LLM.

  

**Score:** 97/100

  

**Feedback:** The prompt is well-structured, provides detailed instructions, and addresses ambiguities from previous versions. Further refinement should focus on optimizing for LLM understanding and reducing any potential ambiguity. The prompt is very close to the target score of 98+/100. Further testing with LLMs will be crucial to identify any remaining areas for improvement.
