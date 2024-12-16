## Current Task: Develop Dictionary Lookup

### Objectives
- Implement the dictionary lookup feature as described in `ZXR.md`.
#### 3.4. Dictionary Lookup

-   **3.4.1. Overview**
    -   **Description:** This feature allows users to look up definitions of selected Chinese characters, words, or phrases. It integrates with QTEngine dictionaries (C:\Users\Zhu Xian\source\repos\ZXReader\src\QTEngine\data) and external dictionaries located in the `dictionaries` folder. The lookup process utilizes Trie data structure and longest prefix matching, that's why when translating, should temporary save the mapping for dictionary lookup ( Need to check QTEngine and Trie for this).
    -   **Behavior:** When a user interacts with text in the Main Translation Panel (single-click or double-click), the system will identify the corresponding translated or original text and highlight it. It will then perform a dictionary lookup to find and display the definition.

-   **3.4.2. User Interaction**
    -   **Single-Click:** Highlights the entire matched prefix (word or phrase) under the cursor in the Main Translation Panel based on the matched prefix from translation mapping. Then triggers a dictionary lookup for that matched prefix (word or phrase).
    -   **Double-Click:** Selects the entire matched prefix (word or phrase) under the cursor in the Main Translation Panel. Right now just need Selects, will add function for it later
    -   **Text Selection by using mouse drag:** Users can also manually select a range of text to trigger a dictionary lookup.

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

-   **3.4.7. Handling Duplicate Paragraphs**
    -   **Challenge:** When dealing with duplicate paragraphs, highlighting must be precise to avoid confusion.
    -   **Implementation:**
        -   Use unique identifiers or context-based logic to ensure highlighting only affects the specific instance being interacted with.
        -   Provide visual cues to help users understand which instance they are interacting with.
    -   **Example:**
        ```
        千叶市公立小学，一年级a班。
        千叶市公立小学，一年级a班。
        千叶市公立小学，一年级a班。
        ```
        When a user clicks on "千叶" in the second line, only that instance should be highlighted, not the same text in other lines.

-   **3.4.8. Translation Mapping Details**
    -   **Description:** The translation mapping is created during the translation process by QTEngine. It establishes a relationship between the original Chinese text and its Sino-Vietnamese translation.
    -   **Data Structure:**
        -   Keys: Original Chinese text segments
        -   Values: Corresponding translated text segments with their positions
    -   **Creation:** During translation, QTEngine records:
        -   Original text segments
        -   Their translations
        -   Position information
    -   **Usage:** Enables bidirectional highlighting between original and translated text

-   **3.4.9. Example**
    -   **Scenario:** The user is reading a chapter where the original text "千叶市公立小学" is translated to "Thiên Diệp thị công lập tiểu học".
        -   Which translated as follows in by using QTEngine's longest prefix match data:
            -   千叶=Thiên Diệp
            -   市=thị
            -   公立=công lập
            -   小学=tiểu học
        So I want the dictionary lookup working as follows:
    -   **Action:** The user single-click on "千叶" in the original text.
    -   **Result:**
        -   The system highlights "Thiên Diệp" in the translated text.
        -   The Dictionary Lookup Panel displays the definition of "千叶" retrieved from the dictionaries.

    -   **Action:** The user single-click on "Thiên Diệp" in the translated text.
    -   **Result:**
        -   The system highlights "千叶" in the original text.
        -   The Dictionary Lookup Panel displays the definition of "千叶" (or "Thiên Diệp", as they share the same definition in this context).

    -   **Action:** The user single-click on "市" in the original text.
    -   **Result:**
        -   The system highlights "thị" in the translated text.
        -   The Dictionary Lookup Panel displays the definition of "市" retrieved from the dictionaries.

    -   **Action:** The user single-click on "thị" in the translated text.
    -   **Result:**
        -   The system highlights "市" in the original text.
        -   The Dictionary Lookup Panel displays the definition of "市" (or "thị", as they share the same definition in this context).

    -   **Action:** The user single-click on "公立" in the original text.
    -   **Result:**
        -   The system highlights "công lập" in the translated text.
        -   The Dictionary Lookup Panel displays the definition of "公立" retrieved from the dictionaries.

    -   **Action:** The user single-click on "công lập" in the translated text.
    -   **Result:**
        -   The system highlights "公立" in the original text.
        -   The Dictionary Lookup Panel displays the definition of "公立" (or "công lập", as they share the same definition in this context).

    -   **Action:** The user single-click on "小学" in the original text.
    -   **Result:**
        -   The system highlights "tiểu học" in the translated text.
        -   The Dictionary Lookup Panel displays the definition of "小学" retrieved from the dictionaries.

    -   **Action:** The user single-click on "tiểu học" in the translated text.
    -   **Result:**
        -   The system highlights "小学" in the original text.
        -   The Dictionary Lookup Panel displays the definition of "小学" (or "tiểu học", as they share the same definition in this context).

-   **3.4.10. Text Segmentation and Mapping**
    -   **Process:**
        -   Original text is segmented into blocks with specific starting positions
        -   Translation follows the same structure
        -   Character positions track where each character starts
        -   Block mapping treats character groups as single units
    -   **Example Structure:**
        ```
        Original Text:    [野][比][大雄][装作][没听到][吹着口哨][抱着][后脑勺][抬头][望天]
                           |   |    |     |     |       |         |     |       |     |
                           v   v    v     v     v       v         v     v       v     v
        Character Pos:     0   1    2     4     6       10        14    16      19    21
                           |           |           |
                           v           v           v
        Block Mapping:    [B1][B2][B3] [B4]        [B5]          [B6]   [B7]   [B8]   [B9]   [B10]
                           |           |           |
                           v           v           v
        Translated Text:  [dã][so][Nobita][giả bộ như][không nghe thấy][huýt sáo][ôm][cái ót][ngẩng đầu][nhìn trời]
        ```

### Context
- The project has implemented file loading, chapter detection, display, and auto selection of the first chapter.
- The "Hiển thị toàn bộ" option has been added to the chapter selection dropdown.
- The `ChapterManager` has been modified to handle the "Hiển thị toàn bộ" option.
- The `MainTranslationPanel` automatically selects the first chapter when chapters are detected.
- The selected chapter is now highlighted in the chapter panel.
- The project has been inspected and the data loading warnings have been addressed (keeping the warnings as they are).
- The user has already run `test main.py` and confirmed there are no bugs.

### Next Steps
1. Implement dictionary lookup functionality in `src/gui/main_translation_panel.py` to handle lookup triggers and highlighting based on the translation mapping.
2. Implement definition display and search functionality in `src/gui/dictionary_panel.py`, ensuring correct formatting and display order.
3. Integrate with `src/core/dictionary_manager.py` to retrieve definitions from all dictionaries in the specified order using Trie and longest prefix match.
4. Implement custom dictionary syncing in `src/core/dictionary_manager.py`.
