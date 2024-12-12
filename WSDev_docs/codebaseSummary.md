## Key Components and Their Interactions

### Core

-   **File Handler:** Manages file operations, including opening, reading, and encoding detection. Interacts with Chapter Manager to process file content.
-   **Chapter Manager:** Detects chapters based on user-selected methods. Provides chapter data to the Main Translation Panel.
-   **Translation Manager:** Interfaces with QTEngine to translate text. Handles requests from the Main Translation Panel and Dictionary Lookup Panel.
-   **Dictionary Manager:** Manages dictionary data, including loading and searching. Provides definitions to the Dictionary Lookup Panel.

### GUI

-   **Main Window:** The primary application window, containing all UI elements.
-   **File Info Panel:** Displays file information. Receives data from the File Handler.
-   **Chapter Panel:** Displays the list of chapters and allows navigation. Interacts with the Chapter Manager and Main Translation Panel.
-   **Main Translation Panel:** Displays the translated text. Receives data from the Chapter Manager and interacts with the Translation Manager.
-   **Dictionary Lookup Panel:** Displays dictionary definitions. Receives requests from the Main Translation Panel and interacts with the Dictionary Manager.

## Data Flow

1. User selects a file via the File Dialog.
2. File Handler reads the file, detects encoding, and passes data to the Chapter Manager.
3. Chapter Manager detects chapters using the selected method and sends the chapter list to the Chapter Panel.
4. User selects a chapter in the Chapter Panel.
5. Chapter Manager retrieves the selected chapter's content and sends it to the Main Translation Panel.
6. Main Translation Panel displays the content and sends it to the Translation Manager for translation.
7. Translation Manager interacts with QTEngine to translate the text.
8. User selects text in the Main Translation Panel, triggering a dictionary lookup.
9. Dictionary Lookup Panel sends the selected text to the Dictionary Manager.
10. Dictionary Manager searches the dictionaries and returns definitions to the Dictionary Lookup Panel.

## External Dependencies

-   **PyQt:** Used for the GUI framework.
-   **QTEngine:** The translation engine for Chinese to Sino-Vietnamese.
-   **External Dictionaries:** Babylon, ThieuChuu, LacViet (loaded using Trie models).

## Recent Significant Changes

-   Created initial project structure and documentation.
-   Implemented basic file handling and chapter detection.
-   Integrated QTEngine for translation.
-   Passed `file_handler` and `translation_manager` to `MainWindow` constructor.

## User Feedback Integration and Its Impact on Development

-   Currently, no user feedback has been integrated.
-   Future feedback will be used to refine the UI, improve functionality, and address any issues.
