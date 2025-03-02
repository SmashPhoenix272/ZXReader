# Dictionary Loading System

[Previous content remains unchanged...]

# Dictionary Edit Dialog System

## Core Components
1. Text Input Management:
   - Read-only Chinese text display
   - Read-only Hán Việt display
   - Editable definition field
   - Context preview with selection support

2. Case Modification System:
   - First letter capitalization for words
   - Single/multiple word support
   - Proper case handling for Names/Names2
   - Automatic case application for new entries

3. Context Preview System:
   - Fixed-width context window (~15 chars per side)
   - Dynamic text selection tracking
   - HTML-based highlighting
   - Navigation controls for selection expansion

## Selection Management
1. Selection Tracking:
   - Start and end position tracking
   - Character-by-character expansion
   - Context window adjustment
   - Selection validation

2. Dictionary Mode Handling:
   - Automatic mode detection (add/edit)
   - Dictionary type preservation
   - Cross-dictionary entry checking
   - Proper case defaults for new entries

3. UI Updates:
   - Dynamic title updates
   - Selection highlighting
   - Navigation button states
   - Text field synchronization

## Data Validation
- Selection boundary validation
- Dictionary entry existence checks
- Text format validation
- Mode transition validation

## UI Components
1. Text Fields:
   - Chinese text display
   - Hán Việt display
   - Definition input
   - Context preview

2. Case Modification Controls:
   - Individual letter buttons
   - Word-based operations
   - Proper case button
   - All first letters button

3. Context Navigation:
   - Previous/Next buttons
   - Selection expansion
   - Visual indicators for more context
   - Modern styling elements

## Error Handling
- Selection boundary protection
- Invalid selection prevention
- Dictionary lookup failures
- Text update synchronization

## Performance Optimization
### Dictionary Loading System
- Parallel processing with size-based prioritization
- Memory-optimized data structures (~745MB total usage)
- Buffered I/O operations for better performance
- Progress tracking and metrics collection
- DataLoader singleton with caching

### Performance Metrics
| Operation | Time (s) | Memory (MB) |
|-----------|----------|-------------|
| Initial Load | ~4.5 | 745 |
| External Dict | ~1.0 | - |
| Total Startup | ~7.9 | - |

### Dictionary Processing
- Efficient batch operations for large dictionaries
- Optimized text parsing and formatting
- Memory-conscious data structures
- Resource monitoring and cleanup

### UI Considerations
- Efficient text updates
- Minimal redraws
- Smooth navigation
- Proper resource cleanup
- Progress feedback for long operations
