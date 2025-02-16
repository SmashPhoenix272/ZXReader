# ZXReader Technical Context

## Technology Stack

### Core Technologies
1. **Python**
   - Primary development language
   - Version requirements: Python 3.x
   - Key features used:
     - Type hints
     - Context managers
     - Exception handling
     - File I/O operations
     - Encoding detection and handling

2. **PyQt**
   - GUI framework
   - Components used:
     - QMainWindow
     - QWidget
     - QTextEdit
     - QListWidget
     - QComboBox
     - QMenu (context menus)
     - Custom widgets
     - State management

3. **QTEngine**
   - Custom translation engine
   - Core functionality:
     - Chinese to Sino-Vietnamese translation
     - Dictionary management with selective loading
     - Text processing with compound word support
     - Translation mapping with block tracking
     - Vietnamese word boundary detection

### Dependencies

1. **Core Dependencies**
   ```
   PyQt5
   chardet>=5.0.0  # For encoding detection
   ```

2. **QTEngine Dependencies**
   - Custom dictionaries
   - Text processing utilities
   - Character conversion tools
   - File modification tracking

3. **Development Dependencies**
   - Testing frameworks
   - Development tools
   - Debugging utilities
   - Performance monitoring tools

## Development Setup

### Project Structure
```
ZXReader/
├── src/
│   ├── core/               # Core business logic
│   │   ├── file_handler.py # Enhanced file handling
│   │   └── ...
│   ├── gui/                # GUI components
│   │   ├── dictionary_edit_dialog.py  # Dictionary editing
│   │   └── ...
│   ├── QTEngine/          # Translation engine
│   └── utils/             # Utility functions
├── dictionaries/          # External dictionaries
├── fonts/                # Font resources
└── memory-bank/          # Project documentation
```

### Key Directories

1. **src/core/**
   - Core application logic
   - Manager classes
   - Business rules
   - Enhanced file handling

2. **src/gui/**
   - UI components
   - Panel implementations
   - Window management
   - State preservation
   - Dictionary editing dialogs

3. **src/QTEngine/**
   - Translation engine
   - Dictionary management
   - Text processing
   - Performance optimization

4. **dictionaries/**
   - External dictionary files
   - Custom dictionary support
   - Dictionary synchronization
   - File modification tracking

5. **fonts/**
   - Font resources
   - Custom font support
   - Font configuration

## Technical Constraints

### 1. Performance Constraints
- Memory usage for large text files
- Dictionary lookup speed (now near-instant)
- UI responsiveness standards
- Translation processing time limits
- Encoding detection performance
- Dictionary reload time (10ms debounce)

### 2. System Requirements
- Operating system compatibility
- Minimum hardware specifications
- Screen resolution requirements
- File system access needs
- Encoding support requirements

### 3. Technical Limitations
- File size handling limits
- Dictionary size constraints
- Translation mapping complexity
- UI component restrictions
- Encoding detection accuracy

## Development Guidelines

### 1. Code Organization
- Follow MVC pattern
- Maintain modular structure
- Use clear naming conventions
- Implement proper error handling
- Maintain state consistency

### 2. File Management
- Enhanced encoding detection:
  ```python
  class FileHandler:
      def __init__(self):
          self.chinese_encodings = ['utf-8', 'gb18030', 'gbk', 'gb2312', 'big5']
          self.last_detected_encoding = None

      def detect_encoding(self, raw_data):
          # Try last successful encoding
          if self.last_detected_encoding:
              try:
                  content = raw_data.decode(self.last_detected_encoding)
                  if self.validate_chinese(content):
                      return self.last_detected_encoding
              except UnicodeDecodeError:
                  pass

          # Try chardet
          encoding_result = chardet.detect(raw_data)
          if encoding_result['confidence'] > 0.8:
              try:
                  content = raw_data.decode(encoding_result['encoding'])
                  if self.validate_chinese(content):
                      return encoding_result['encoding']
              except UnicodeDecodeError:
                  pass

          # Try each Chinese encoding
          for encoding in self.chinese_encodings:
              try:
                  content = raw_data.decode(encoding)
                  if self.validate_chinese(content):
                      return encoding
              except UnicodeDecodeError:
                  continue

          return None
  ```
- Implement efficient file reading
- Manage file resources properly
- Handle file system errors
- Cache successful encodings

### 3. UI Development
- Follow PyQt best practices
- Maintain consistent styling
- Implement responsive design
- Handle user input properly
- Preserve state across operations

### 4. State Management
- Track chapter positions:
  ```python
  class MainTranslationPanel:
      def __init__(self):
          self.current_chapter_index = 0

      def set_chapter_text(self, chapter_index):
          self.current_chapter_index = chapter_index
          # Update text display...

      def toggle_text_display(self):
          self.show_original = not self.show_original
          # Preserve position
          self.set_chapter_text(self.current_chapter_index)
  ```
- Maintain display preferences
- Handle state transitions
- Ensure consistency

### 5. Dictionary Management
```python
class DictionaryManager:
    def __init__(self):
        self.debounce_time = 10  # ms
        self.file_watchers = {}
        self.last_modified_times = {}
        
    def setup_dictionary_editing(self):
        # Right-click menu for dictionary editing
        self.context_menu = QMenu()
        self.edit_action = self.context_menu.addAction("Edit Entry")
        self.edit_action.triggered.connect(self.show_edit_dialog)
        
    def handle_dictionary_update(self, file_path):
        current_time = os.path.getmtime(file_path)
        if file_path not in self.last_modified_times or current_time > self.last_modified_times[file_path]:
            self.last_modified_times[file_path] = current_time
            self.selective_reload(file_path)
            
    def selective_reload(self, file_path):
        # Only reload modified dictionary
        dictionary_data = self.load_dictionary(file_path)
        self.update_trie(dictionary_data, file_path)
        
    def update_trie(self, data, source):
        # Optimize Trie creation for selective reloads
        if source in self.tries:
            del self.tries[source]  # Remove old trie
        self.tries[source] = Trie()
        for entry in data:
            self.tries[source].insert(entry)
```

## Integration Points

### 1. QTEngine Integration
```python
# Add QTEngine to Python path
current_dir = os.path.dirname(__file__)
qt_engine_path = os.path.join(current_dir, 'QTEngine')
sys.path.append(qt_engine_path)
os.chdir(qt_engine_path)

# Initialize QTEngine with optimized dictionary loading
qt_engine = QTEngine(selective_loading=True)
```

### 2. Dictionary Integration
- Selective dictionary loading
- File modification tracking
- Near-instant updates (10ms debounce)
- Right-click dictionary editing
- Case-sensitive handling
- Compound word support
- Block mapping optimization

### 3. Font Integration
- Load custom fonts
- Handle font registration
- Manage font fallbacks
- Support variable fonts

## Development Tools

### 1. Required Tools
- Python 3.x
- PyQt5
- chardet library
- Text editor/IDE
- Git for version control

### 2. Optional Tools
- Testing frameworks
- Debugging tools
- Performance profilers
- Code analysis tools
- Dictionary validation tools

## Technical Debt Considerations

### 1. Current Technical Debt
- Dictionary import/export system
- Advanced search capabilities
- Dictionary backup solution
- Entry validation system
- Statistics tracking implementation

### 2. Mitigation Strategies
- Regular code reviews
- Performance monitoring
- Technical documentation
- Systematic refactoring
- Dictionary validation

## Security Considerations

### 1. File System Security
- Safe file handling
- Path validation
- Resource cleanup
- Access control
- Encoding validation

### 2. Input Validation
- Text input sanitization
- File type verification
- Character encoding validation
- Dictionary entry validation
- Error boundary handling
