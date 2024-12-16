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
    -   **Description:** The Dictionary Lookup feature enables users to find definitions of selected Chinese text. It uses QTEngine dictionaries (Names, Names2, VietPhrase) and external dictionaries in the `dictionaries` folder. The lookup employs a Trie data structure and longest prefix matching, leveraging a mapping created during translation by QTEngine ( in text_processing.py).
    -   **Behavior:** A single-click, double-click, or text selection in the Main Translation Panel triggers a lookup, highlighting the corresponding text and displaying the definition.

-   **3.4.2. User Interaction**
    -   **Single-Click:** Highlights the longest matching prefix in both original and translated text.
    -   **Double-Click:** Selects the word/phrase under the cursor, triggering a lookup.
    -   **Text Selection:** Allows manual selection of text for lookup.

-   **3.4.3. Lookup Process**
    -   **Identification:** The system identifies the selected text in either the original or translated text.
    -   **Highlighting:** The corresponding text in the other panel is highlighted using the translation mapping. Check **3.4.8. Translation Mapping Details**
    -   **Definition Retrieval:**
        -   For translated text, the system retrieves the original Chinese text using the stored mapping.
        -   The original Chinese text is used as the key for dictionary lookup.
        -   The system searches QTEngine dictionaries and external dictionaries (Babylon, ThieuChuu, LacViet) using Trie and longest prefix match.
        -   If found, the definition is displayed in the Dictionary Lookup Panel.

-   **3.4.4. Dictionary Lookup Panel**
    -   **Display:** Definitions are shown in the order: Names, Names2, VietPhrase, LacViet, ThieuChuu, Babylon.
    -   **Formatting:** Line breaks in ThieuChuu and LacViet entries are handled (e.g., "龢=hòa [huo2]\n\t1. Ðiều hòa, hợp."). Definitions are presented clearly.
    -   **Search:** Users can search for specific words/phrases within the panel.

-   **3.4.5. Custom Dictionary Syncing**
    -   Users can add a `Names2.txt` file to customize the dictionary. The system syncs this file with QTEngine's internal `Names2.txt`.

-   **3.4.6. Error Handling**
    -   **Not Found:** A message is displayed if no definition is found.

-   **3.4.7. Handling Duplicate Paragraphs**
    -   When dealing with multiple duplicate paragraphs like:
    
        千叶市公立小学，一年级a班。
        千叶市公立小学，一年级a班。
        千叶市公立小学，一年级a班。
        It’s crucial to ensure that highlighting is precise to avoid confusion across duplicates:
    -   **Highlighting Mechanism:**
        -   Implement a system that distinguishes between instances of highlighted words/phrases across different paragraphs.
        -   Use unique identifiers or context-based logic to ensure that when a user clicks on a word/phrase in one line, only that instance is highlighted without affecting duplicates in other lines.
    -   **User Feedback:**
        -   Provide visual cues such as distinct colors or styles for highlighted terms based on their context to enhance clarity.
        -   Ensure that users receive immediate feedback about which specific instance they are interacting with.

-   **3.4.8. Translation Mapping Details**
    -   **Description:** The translation mapping is created during the translation process by QTEngine. It establishes a relationship between the original Chinese text and its Sino-Vietnamese translation, facilitating user interaction across panels.
    -   **Data Structure:** The mapping is stored as a dictionary where:
        -   **Keys:** Original Chinese text segments.
        -   **Values:** Corresponding translated Sino-Vietnamese text segments, including their start and end positions in both the original and translated texts.
    -   **Mapping Creation:** During translation, QTEngine records:
        -   Original text segments.
        -   Corresponding translations.
        -   Their positions within the text.
    -   **Mapping Usage:** When a user:
        -   Clicks or selects text in the original panel, the corresponding translated text is highlighted in the translated panel.
        -   Example: Check **3.4.9. Example**
    -   **User Interaction:** This feature enhances user experience by allowing seamless navigation between original and translated texts, making it easier to understand context and meaning.

-   **3.4.9. Example**
    -   **Scenario:** User reads "千叶市公立小学" (original) which translates to "Thiên Diệp thị công lập tiểu học".
    -   **Single-Click "千叶":** Highlights "Thiên Diệp", displays definition of "千叶".
    -   **Single-Click "Thiên Diệp":** Highlights "千叶", displays definition of "千叶".
    -   **Double-Click "千叶":** Selects "Thiên Diệp", displays definition of "千叶".
    -   **Double-Click "Thiên Diệp":** Selects "千叶", displays definition of "千叶".
    -   And so on for "市", "公立", "小学", etc.
    
-   **3.4.10. Text Segmentation and Mapping**
    -   The original text is segmented into blocks, each with a specific starting position. The translation also follows this structure. Here's how it works:
        -   **Character Positions:** These are the indices of characters in the original text. They help track where each character starts.
        -   **Block Mapping:** This treats groups of characters as a single unit, which can be useful for handling translations that span multiple characters or words.
    -   **ASCII Representation**
        -   Below is an ASCII representation that aligns with your debug output:
        
        ```
        text
        Original Text:    [野][比][大雄][装作][没听到][吹着口哨][抱着][后脑勺][抬头][望天]
                           |   |    |     |     |       |         |     |       |     |
                           v   v    v     v     v       v         v     v       v     v
        Character Positions: 0   1    2     4     6       10        14    16      19    21
                           |           |           |
                           v           v           v
        Block Mapping:    [B1][B2][B3] [B4]        [B5]          [B6]   [B7]   [B8]   [B9]   [B10]
                           |           |           |
                           v           v           v
        Translated Text:  [dã][so][Nobita][giả bộ như][không nghe thấy][huýt sáo][ôm][cái ót][ngẩng đầu][nhìn trời]
        ```
    -   **Explanation**
        -   **Character Positions:** Each character in the original text has a specific position:
            -   '野' starts at position 0
            -   '比' starts at position 1
            -   '大雄' starts at position 2 (treated as a single block)
            -   '装作' starts at position 4 (treated as a single block)
            -   And so on...
        -   **Block Mapping:** Each block represents a logical unit of text that maps to a translation:
            -   B1 corresponds to '野' -> 'dã'
            -   B2 corresponds to '比' -> 'so'
            -   B3 corresponds to '大雄' -> 'Nobita'
            -   B4 corresponds to '装作' -> 'giả bộ như'
            -   Etc.
        -   **Translated Text:** The translated text is aligned with these blocks, showing how each segment translates.
    -   This representation helps visualize how character positions and block mappings work together. By using both systems, you can accurately track user interactions and ensure that entire words or phrases are highlighted when selected. This approach enhances user experience by providing intuitive and precise text handling in translation applications.

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

1.  **Core Framework:**
    -   Set up the project structure.
    -   Implement basic UI layout with resizable panels.
    -   Integrate QTEngine.
2.  **File Handling and Chapter Detection:**
    -   Implement file loading with encoding detection.
    -   Develop chapter detection using `detect_chapters_methods.py`.
    -   Create the File Info and Chapter panels.
3.  **Reading and Translation:**
    -   Implement the main translation panel.
    -   Enable parallel display of Chinese and translated text.
4.  **Dictionary Lookup:**
    -   Develop the dictionary lookup panel.
    -   Load and integrate external dictionaries.
    -   Implement custom dictionary syncing.
5.  **UI Enhancements and Customization:**
    -   Implement light/dark/book/wood themes.
    -   Add support for custom fonts.
    -   Ensure UI responsiveness.
6.  **Testing and Refinement:**
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
