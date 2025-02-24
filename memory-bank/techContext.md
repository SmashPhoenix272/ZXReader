# Dictionary Loading System

## Data Formats
- Names2.txt: Key-value pairs with = or tab separator
- Names.txt: Key-value pairs with = or tab separator 
- VietPhrase.txt: Key-value pairs with = or tab separator
- ChinesePhienAmWords.txt: Chinese-Vietnamese translations using = separator (e.g., "上=thượng")

## Dictionary Loading Process
1. Base Loading:
   - Support both = and tab separators
   - Strip whitespace from keys and values
   - Skip empty lines and comments (#)
   - Track line counts and entry counts

2. Format Detection:
   - Check for = separator first
   - Fall back to tab separator if = not found
   - Skip invalid entries (missing key or value)

3. Error Handling:
   - File existence verification
   - Entry validation with configurable thresholds
   - Detailed logging of loading issues
   - Retry mechanism for load failures

4. Performance:
   - Single pass file reading
   - Efficient string parsing
   - Minimize memory allocations
   - Early validation and error detection

## Data Validation
- Dictionary validation with minimum entry thresholds
- Names/Names2: No minimum (allow few entries)
- VietPhrase: 10+ entries required 
- ChinesePhienAm: 10+ entries required
- Trie validation for relevant dictionaries

## Logging
- File sizes and locations
- Entry counts per dictionary
- Line processing statistics
- Loading issues and warnings
- Format detection results

## Memory Management
- Clear unused data
- Proper cache handling
- Resource cleanup
- Memory-efficient data structures

## Error Recovery
- Retry failed loads
- Maintain existing data on partial failures
- Clear error messages
- Proper error propagation
