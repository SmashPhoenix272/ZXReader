# ZXReader System Patterns

## System Architecture

### Core Components
1. **File Management**
[Previous file management content remains unchanged...]

4. **Dictionary System**
   ```mermaid
   flowchart TD
       DictionaryManager[DictionaryManager] --> DictionaryEdit[Dictionary Edit]
       DictionaryEdit --> RightClickMenu[Right-Click Menu]
       DictionaryEdit --> EditDialog[Edit Dialog]
       EditDialog --> CaseModification[Case Modification]
       EditDialog --> ContextPreview[Context Preview]
       EditDialog --> SelectionExpansion[Selection Expansion]
       
       DictionaryManager --> Performance[Performance Optimization]
       Performance --> SelectiveLoading[Selective Loading]
       Performance --> FileTracking[File Modification Tracking]
       Performance --> TrieOptimization[Trie Optimization]
       Performance --> DebouncedUpdates[Debounced Updates]
       
       DictionaryManager --> TextHandling[Text Handling]
       TextHandling --> WordBoundary[Vietnamese Word Boundary]
       TextHandling --> CompoundWords[Compound Words]
       TextHandling --> BlockMapping[Block Mapping]
       
       CaseModification --> FirstLetter[First Letter Changes]
       CaseModification --> ProperCase[Proper Case Rules]
       CaseModification --> AutoCase[Automatic Case]
       
       ContextPreview --> TextHighlight[Text Highlighting]
       ContextPreview --> Navigation[Navigation Controls]
       ContextPreview --> SelectionTracking[Selection Tracking]
       
       SelectionExpansion --> BoundaryCheck[Boundary Validation]
       SelectionExpansion --> DictionarySwitch[Dictionary Mode Switch]
       SelectionExpansion --> StateUpdate[State Updates]
       
       DictionaryManager --> QTDictionaries[QT Dictionaries]
       DictionaryManager --> ExternalDictionaries[External Dictionaries]
       DictionaryManager --> CustomDictionaries[Custom Dictionaries]
   ```

[Rest of the file remains unchanged...]
