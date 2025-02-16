# ZXReader Active Context

## Current Focus: Dictionary Management and Performance Optimization

### Recent Changes
1. **Dictionary Management Improvements**
   - Added right-click menu for dictionary editing
   - Created dictionary edit dialog
   - Implemented dictionary update functionality
   - Added text case modification options
   - Fixed line ending issues in dictionary files

2. **Dictionary Performance Optimization**
   - Added selective dictionary loading
   - Reduced debounce time to 10ms
   - Added file modification tracking
   - Improved Trie creation for selective reloads
   - Prevented duplicate reloads
   - Reduced wait time from 5s to near-instant

3. **Text Selection and Translation**
   - Fixed Vietnamese word boundary detection
   - Improved compound word handling (e.g. 'không muốn')
   - Fixed dictionary lookup for translated text
   - Better block mapping between languages

### Current State
- Dictionary editing and management fully operational
- Optimized dictionary reload performance
- Improved text selection and translation accuracy
- Core file handling and chapter management working
- Translation system operational
- UI panels in place and functioning
- File encoding support working for various Chinese encodings
- Show/hide original text maintains chapter position

### Active Decisions
1. **Dictionary Management Strategy**
   - Enable right-click editing for quick updates
   - Implement selective dictionary reloading
   - Track file modifications for efficient updates
   - Optimize Trie creation process
   
2. **Performance Optimization**
   - Use selective loading to reduce memory usage
   - Implement efficient file modification tracking
   - Minimize dictionary reload time
   - Prevent unnecessary reloads

3. **Text Selection Strategy**
   - Handle Vietnamese word boundaries accurately
   - Support compound word detection
   - Improve block mapping for translations
   - Maintain text case consistency

### Next Steps
1. **Dictionary Feature Enhancement**
   - Implement additional dictionary editing features
   - Add dictionary import/export functionality
   - Improve dictionary search capabilities
   - Add dictionary backup functionality

2. **Performance Monitoring**
   - Monitor dictionary reload performance
   - Track memory usage during updates
   - Optimize large dictionary handling
   - Implement performance metrics

3. **UI Refinements**
   - Enhance dictionary edit dialog
   - Improve right-click menu usability
   - Add dictionary statistics display
   - Implement dictionary entry validation

### Current Challenges
1. **Technical Challenges**
   - Accurate encoding detection
   - Performance with large files
   - Memory management
   - State preservation

2. **Implementation Decisions**
   - Encoding detection order
   - Caching strategies
   - Error handling approaches
   - UI feedback methods

### Testing Focus
1. **Functionality Testing**
   - File encoding detection accuracy
   - Chapter position preservation
   - Text display consistency
   - Error handling

2. **Performance Testing**
   - File loading speed
   - Memory usage
   - UI responsiveness
   - Large file handling

### Documentation Needs
1. **Code Documentation**
   - Encoding detection logic
   - State management
   - Error handling procedures
   - Performance considerations

2. **User Documentation**
   - Supported encodings
   - File loading behavior
   - Error messages and solutions
   - UI interaction guidelines

## Immediate Tasks
1. Monitor encoding detection accuracy
2. Optimize file loading performance
3. Improve error messages
4. Add encoding selection UI
5. Document new functionality

## Future Considerations
1. **Performance Optimization**
   - Smarter encoding caching
   - Lazy loading for large files
   - Background processing

2. **Feature Enhancements**
   - Manual encoding selection
   - Encoding conversion tools
   - Better progress indicators
   - Advanced file info display

3. **User Experience**
   - Clearer error messages
   - Loading progress feedback
   - Encoding preferences
   - Performance settings
