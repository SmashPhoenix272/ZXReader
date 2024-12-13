## ZXReader Development Prompt - v2.1

**Prompt Version:** 2.1

**Last Updated:** 2023-12-13

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
-   Updated dictionary lookup to trigger on double-click or text selection.
-   Clarified handling of line breaks in ThieuChuu and LacViet dictionary entries.
-   Added support for searching specific words or phrases in the Dictionary Lookup Panel.
-   Included instructions for custom dictionary syncing for `Names2.txt`.
-   Implemented dictionary lookup functionality, including integration with QTEngine and external dictionaries.

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

-   **3.4.1. Overview**
    -   **Description:** This feature allows users to look up definitions of selected Chinese characters, words, or phrases. It integrates with QTEngine dictionaries (Names, Names2, VietPhrase) and external dictionaries located in the `dictionaries` folder. The lookup process utilizes Trie data structure and longest prefix matching, that's why when translating, should temporary save the mapping for dictionary lookup.
    -   **Behavior:** When a user interacts with text in the Main Translation Panel (single-click or double-click), the system will identify the corresponding translated or original text and highlight it. It will then perform a dictionary lookup to find and display the definition.

-   **3.4.2. User Interaction**
    -   **Single-Click:** Highlights the matched prefix (word or phrase) in the Main Translation Panel based on the longest prefix match in both the original and translated text.
    -   **Double-Click:** Selects the entire word or phrase under the cursor in the Main Translation Panel. This action triggers a dictionary lookup.
    -   **Text Selection:** Users can also manually select a range of text to trigger a dictionary lookup.

-   **3.4.3. Lookup Process**
    -   **Identification:** The system identifies the selected text (character, word, or phrase) in either the original or translated text displayed in the Main Translation Panel.
    -   **Highlighting:**
        -   Upon identifying the selected text, the system highlights the corresponding text in the other panel. For example, if the user selects "千叶" in the original text, the system will highlight "Thiên Diệp" in the translated text, and vice versa.
        -   The highlighting is based on the translation mapping stored during the initial text translation by QTEngine.
    -   **Definition Retrieval:**
        -   The system uses the identified text as a key for dictionary lookup.
        -   It searches for the key in the QTEngine dictionaries (Names, Names2, VietPhrase) and external dictionaries (Babylon, ThieuChuu, LacViet) using Trie and longest prefix match.
        -   If a definition is found, it is displayed in the Dictionary Lookup Panel.

-   **3.4.4. Dictionary Lookup Panel**
    -   **Display:** Shows the definitions found from the various dictionaries. Show in the following order Names, Names2, VietPhrase, LacViet, ThieuChuu, Babylon.
    -   **Formatting:**
        -   Handles line breaks in entries from ThieuChuu and LacViet dictionaries (e.g., "龢=hòa [huo2]\n\t1. Ðiều hòa, hợp.").
        -   Presents definitions in a clear and readable format.
    -   **Search Functionality:** Allows users to perform searches within the Dictionary Lookup Panel for specific words or phrases.

-   **3.4.5. Custom Dictionary Syncing**
    -   **User-Defined Dictionaries:** Users can add their own `Names2.txt` file to customize the dictionary.
    -   **Synchronization:** The system synchronizes the user-provided `Names2.txt` with QTEngine's internal `Names2.txt` to incorporate user-defined translations.

-   **3.4.6. Error Handling**
    -   **Not Found:** If no definition is found for the selected character/word/phrase, a message is displayed to the user in the Dictionary Lookup Panel.

-   **3.4.7. Example**
    -   **Scenario:** The user is reading a chapter where the original text "千叶市公立小学" is translated to "Thiên Diệp thị công lập tiểu học".
    -   **Action:** The user single-clicks on "千叶" in the original text.
    -   **Result:**
        -   The system highlights "Thiên Diệp" in the translated text.
        -   The Dictionary Lookup Panel displays the definition of "千叶" retrieved from the dictionaries.
    -   **Action:** The user double-clicks on "Thiên Diệp" in the translated text.
    -   **Result:**
        -   The system highlights "千叶" in the original text.
        -   The Dictionary Lookup Panel displays the definition of "千叶" (or "Thiên Diệp", as they share the same definition in this context).
    -   **Action:** The user manually selects "公立小学" in the original text.
    -   **Result:**
        -   The system highlights "công lập tiểu học" in the translated text.
        -   The Dictionary Lookup Panel displays the definition of "公立小学" based on the longest prefix match and Trie search.

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
