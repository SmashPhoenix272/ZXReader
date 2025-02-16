# ZXReader

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green?style=for-the-badge&logo=qt)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

A powerful desktop application designed for reading Chinese novels with Sino-Vietnamese translation support. ZXReader provides an efficient and user-friendly reading experience with robust features for translation, chapter management, dictionary lookup, and customization.

## Features

### File Handling
- Support for multiple Chinese encodings (UTF-8, GB18030, GBK, GB2312, BIG5)
- Smart encoding detection with validation
- Efficient handling of large text files
- Robust error handling and recovery

### Reading Experience
- Side-by-side display of original Chinese text and Sino-Vietnamese translation
- Chapter-based navigation with translated titles
- Position preservation when toggling between original and translated text
- Customizable display options

### Translation System
- Integrated QTEngine for accurate Chinese to Sino-Vietnamese translation
- Context-aware translation with compound word support
- Real-time dictionary lookup with multiple sources
- Bidirectional lookup between Chinese and Sino-Vietnamese

### Dictionary Management
- Multiple dictionary sources integration
- Right-click dictionary editing capability
- Custom dictionary synchronization
- Near-instant dictionary updates
- Case-sensitive word handling
- Compound word support

### User Interface
- Modern, intuitive interface
- Resizable panels for customized layout
- Custom font support
- Multiple theme options (coming soon)
- Minimum window size: 800x600 pixels

## Technology

### Stack
- **Language:** Python 3.x
- **GUI Framework:** PyQt5
- **Translation Engine:** QTEngine
- **Encoding Detection:** chardet 5.0.0+
- **Architecture:** MVC pattern with modular design

### Requirements
```bash
Python 3.x
PyQt5
chardet>=5.0.0
```

## Project Structure
```
ZXReader/
├── src/
│   ├── core/               # Core business logic
│   ├── gui/                # GUI components
│   ├── QTEngine/          # Translation engine
│   └── utils/             # Utility functions
├── dictionaries/          # External dictionaries
└── fonts/                # Font resources
```

## Development Status

### Completed Features
- Enhanced file encoding detection and support
- Chapter detection and management
- QTEngine integration for translation
- Dictionary management with editing capabilities
- Basic UI components and layout
- File information display
- Position tracking and preservation

### In Development
- Dictionary import/export system
- Advanced search capabilities
- Dictionary backup solution
- Theme implementation (light/dark/book/wood)
- Performance optimizations for large files

### Coming Soon
- Theme customization options
- Advanced dictionary management features
- Performance optimizations
- Comprehensive documentation
- Keyboard shortcuts

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---
<div align="center">
<b>ZXReader</b> | A Modern Chinese Novel Reader with Sino-Vietnamese Translation
</div>
