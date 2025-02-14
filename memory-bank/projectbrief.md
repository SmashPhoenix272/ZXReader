# ZXReader Project Brief

## Project Overview
ZXReader is a desktop application designed to read Chinese novels and text files, providing Sino-Vietnamese translation using QTEngine. The application aims to create a user-friendly and efficient reading experience with robust features for translation, chapter management, dictionary lookup, and customization, while supporting various Chinese text encodings and maintaining consistent state across operations.

## Core Requirements

### 1. File Handling
- Enhanced encoding support:
  * UTF-8, GB18030, GBK, GB2312, BIG5
  * Smart encoding detection with validation
  * Special handling for GB2312/GB18030
  * Encoding caching for performance
- File info display (name, translated name, encoding, size)
- Robust error handling for file operations
- Efficient fallback mechanisms

### 2. Chapter Detection
- Multiple detection methods via regex
- Dynamic chapter list with translated titles
- Chapter navigation and management
- Manual chapter title editing support
- Position tracking and preservation

### 3. Reading Functionality
- Main translation panel with original and translated text
- Toggle between translation modes with position preservation
- Smooth chapter navigation
- State management across operations
- Consistent reading experience

### 4. Dictionary Lookup
- Integration with QTEngine and external dictionaries
- Support for multiple dictionary sources
- Bidirectional lookup between Chinese and Sino-Vietnamese
- Custom dictionary syncing (Names2.txt)
- Precise text highlighting and mapping
- State-aware lookups

### 5. UI Requirements
- Modern, user-friendly interface
- Light/dark/book/wood themes
- Resizable panels
- Custom font support
- Minimum window size: 800x600 pixels
- State preservation across interactions

## Technical Stack
- Language: Python
- GUI Framework: PyQt
- Translation Engine: QTEngine
- Data Structure: Trie for dictionary lookups
- Architecture: MVC pattern with modular design
- Encoding Detection: chardet with custom validation
- State Management: Position tracking and preservation

## Project Goals
1. Create an efficient and user-friendly reading experience
2. Provide accurate Sino-Vietnamese translations
3. Enable comprehensive dictionary lookup functionality
4. Support various Chinese text encodings effectively
5. Maintain high performance with large text files
6. Ensure robust error handling and stability
7. Preserve user state and preferences consistently

## Success Criteria
1. Smooth file loading and encoding detection
   - Accurate detection of various encodings
   - Proper handling of GB2312/GB18030
   - Reliable fallback mechanisms
   - Efficient encoding caching

2. Robust Chapter Management
   - Accurate chapter detection
   - Position preservation when toggling views
   - Consistent state tracking
   - Smooth navigation

3. Enhanced Reading Experience
   - Accurate text translation and highlighting
   - State preservation across operations
   - Seamless view toggling
   - Position maintenance

4. Efficient Dictionary Integration
   - Fast and accurate dictionary lookups
   - State-aware lookup behavior
   - Multiple source support
   - Custom dictionary handling

5. Responsive Interface
   - Intuitive user interface
   - Consistent state management
   - Smooth transitions
   - Reliable preferences

6. Technical Excellence
   - Stable performance with large files
   - Comprehensive error handling
   - Efficient resource usage
   - Robust state management
