from typing import List, Tuple, Dict, Optional
from src.QTEngine.models.trie import Trie
from .character_utils import replace_special_chars, LATIN_CHARS
import re
import logging

class Block:
    def __init__(self, original: str, translated: str, orig_start: int, trans_start: int):
        self.original = original
        self.translated = translated
        self.orig_start = orig_start
        self.orig_end = orig_start + len(original)
        self.trans_start = trans_start
        self.trans_end = trans_start + len(translated)

class TranslationMapping:
    def __init__(self):
        self.blocks: List[Block] = []
        self.original_to_block: Dict[str, List[Block]] = {}  # One original text might map to multiple blocks (duplicates)
        self.translated_to_block: Dict[str, List[Block]] = {}  # One translated text might map to multiple blocks
        self.current_original_pos = 0
        self.current_translated_pos = 0

    def add_block(self, original: str, translated: str):
        """Add a new block to the mapping."""
        block = Block(original, translated, self.current_original_pos, self.current_translated_pos)
        self.blocks.append(block)
        
        # Update mappings
        if original not in self.original_to_block:
            self.original_to_block[original] = []
        self.original_to_block[original].append(block)
        
        if translated not in self.translated_to_block:
            self.translated_to_block[translated] = []
        self.translated_to_block[translated].append(block)
        
        # Update positions
        self.current_original_pos = block.orig_end
        self.current_translated_pos = block.trans_end

    def get_translated_segment(self, original: str, position: Optional[int] = None) -> Optional[Tuple[str, int, int]]:
        """
        Get translated segment and its position for an original text segment.
        If position is provided, returns the block closest to that position.
        """
        blocks = self.original_to_block.get(original)
        if not blocks:
            return None
            
        if position is not None:
            # Find the block closest to the given position
            closest_block = min(blocks, key=lambda b: abs(b.orig_start - position))
            return (closest_block.translated, closest_block.trans_start, closest_block.trans_end)
        
        # If no position provided, return the first occurrence
        block = blocks[0]
        return (block.translated, block.trans_start, block.trans_end)

    def get_original_segment(self, translated: str, position: Optional[int] = None) -> Optional[Tuple[str, int, int]]:
        """
        Get original segment and its position for a translated text segment.
        If position is provided, returns the block closest to that position.
        """
        blocks = self.translated_to_block.get(translated)
        if not blocks:
            return None
            
        if position is not None:
            # Find the block closest to the given position
            closest_block = min(blocks, key=lambda b: abs(b.trans_start - position))
            return (closest_block.original, closest_block.orig_start, closest_block.orig_end)
        
        # If no position provided, return the first occurrence
        block = blocks[0]
        return (block.original, block.orig_start, block.orig_end)

def convert_to_sino_vietnamese(
    text: str, 
    names2: Trie, 
    names: Trie, 
    viet_phrase: Trie, 
    chinese_phien_am: Dict[str, str]
) -> Tuple[str, TranslationMapping]:
    """
    Convert Chinese text to Sino-Vietnamese using block-based mapping.

    Args:
        text (str): The input Chinese text.
        names2 (Trie): Trie containing Names2.txt data.
        names (Trie): Trie containing Names.txt data.
        viet_phrase (Trie): Trie containing VietPhrase.txt data.
        chinese_phien_am (Dict[str, str]): Dictionary containing ChinesePhienAmWords.txt data.

    Returns:
        Tuple[str, TranslationMapping]: The converted Sino-Vietnamese text and mapping information.
    """
    if not isinstance(text, str):
        raise ValueError(f"Input text must be a string, got {type(text)}")
    
    if not text:
        logging.warning("Empty input text provided")
        return "", TranslationMapping()
    
    # Validate Trie and dictionary inputs
    for name, obj in [('names2', names2), ('names', names), ('viet_phrase', viet_phrase)]:
        if not isinstance(obj, Trie):
            raise ValueError(f"{name} must be a Trie object")
    
    if not isinstance(chinese_phien_am, dict):
        raise ValueError("chinese_phien_am must be a dictionary")

    text = replace_special_chars(text)
    
    tokens = []
    mapping = TranslationMapping()
    i = 0
    
    while i < len(text):
        # Check for a sequence of Latin characters
        latin_start = i
        while i < len(text) and text[i] in LATIN_CHARS:
            i += 1
        if i > latin_start:
            latin_text = text[latin_start:i]
            tokens.append(latin_text)
            mapping.add_block(latin_text, latin_text)
            continue
        
        # Try Names2 first
        name2_match, value = names2.find_longest_prefix(text[i:])
        if name2_match and value is not None:
            translated = split_value(value)
            tokens.append(translated)
            mapping.add_block(name2_match, translated)
            i += len(name2_match)
            continue
        
        # Try Names
        name_match, value = names.find_longest_prefix(text[i:])
        if name_match and value is not None:
            translated = split_value(value)
            tokens.append(translated)
            mapping.add_block(name_match, translated)
            i += len(name_match)
            continue
        
        # Try VietPhrase
        viet_phrase_match, value = viet_phrase.find_longest_prefix(text[i:])
        if viet_phrase_match and value is not None:
            translated = split_value(value)
            tokens.append(translated)
            mapping.add_block(viet_phrase_match, translated)
            i += len(viet_phrase_match)
            continue
        
        # Try Chinese Phien Am Words
        if text[i:i+1] in chinese_phien_am:
            translated = chinese_phien_am[text[i:i+1]]
            tokens.append(translated)
            mapping.add_block(text[i:i+1], translated)
            i += 1
            continue
        
        # If no match found, add the character as is
        tokens.append(text[i])
        mapping.add_block(text[i], text[i])
        i += 1

    # Rephrase the tokens
    result = rephrase(tokens)

    # Apply regex transformations
    result = re.sub(r'([\[\“\‘])\s*(\w)', lambda m: m.group(1) + m.group(2).upper(), result)
    result = re.sub(r'\s+([”\’\]])', r'\1', result)
    result = re.sub(r'([?!⟨:«])\s+(\w)', lambda m: m.group(1) + ' ' + m.group(2).upper(), result)
    result = re.sub(r'\s+([;:?!.])', r'\1', result)
    result = re.sub(r'(?<!\.)\.(?!\.)\s+(\w)', lambda m: '. ' + m.group(1).upper(), result)
    
    return result, mapping

def split_value(value: str) -> str:
    """
    Split a value with multiple definitions and return the first non-empty definition.
    
    Args:
        value (str): Input value potentially containing multiple definitions.
    
    Returns:
        str: First non-empty definition of the value, or a space if empty.
    """
    if '=' in value:
        parts = value.split('=', 1)
        value = parts[1]
    
    split_parts = value.replace("|", "/").split("/")
    
    if not split_parts[0].strip():
        return ' '
    
    for part in split_parts:
        stripped_part = part.strip()
        if stripped_part:
            return stripped_part
    
    return value

def rephrase(tokens: List[str]) -> str:
    """
    Rephrase the tokens to form a properly formatted sentence.

    Args:
        tokens (List[str]): A list of tokens to be rephrased.

    Returns:
        str: The rephrased text.
    """
    non_word = set('"[{ ,!?;\'.')
    result = []
    upper = False
    last_token_empty = False

    for i, token in enumerate(tokens):
        if token.strip():  # Non-empty token
            if i == 0 or (not upper and token not in non_word):
                if result and not last_token_empty:
                    result.append(' ')
                if not token[0].isupper():  # Only capitalize if not already capitalized
                    token = token.capitalize()
                upper = True
            elif token not in non_word and not last_token_empty:
                result.append(' ')
            result.append(token)
            last_token_empty = False
        else:  # Empty or whitespace token
            result.append(token)  # Preserve the original whitespace
            last_token_empty = True

    text = ''.join(result)
    return text

def process_paragraph(
    paragraph: str, 
    names2: Trie, 
    names: Trie, 
    viet_phrase: Trie, 
    chinese_phien_am: Dict[str, str]
) -> Tuple[str, TranslationMapping]:
    """
    Process a single paragraph by converting it to Sino-Vietnamese.

    Args:
        paragraph (str): The input paragraph in Chinese.
        names2 (Trie): Trie containing Names2.txt data.
        names (Trie): Trie containing Names.txt data.
        viet_phrase (Trie): Trie containing VietPhrase.txt data.
        chinese_phien_am (Dict[str, str]): Dictionary containing ChinesePhienAmWords.txt data.

    Returns:
        Tuple[str, TranslationMapping]: The processed paragraph in Sino-Vietnamese and mapping information.
    """
    lines = paragraph.splitlines(keepends=True)
    result_lines = []
    mapping = TranslationMapping()
    
    current_orig_pos = 0
    current_trans_pos = 0
    
    for line in lines:
        leading_space = ''
        for char in line:
            if char.isspace():
                leading_space += char
            else:
                break
                
        content = line.lstrip()
        if content:
            converted, line_mapping = convert_to_sino_vietnamese(content, names2, names, viet_phrase, chinese_phien_am)
            result_lines.append(leading_space + converted)
            
            # Adjust positions for leading space
            space_offset = len(leading_space)
            
            # Update positions for this line's blocks
            for block in line_mapping.blocks:
                block.orig_start += current_orig_pos + space_offset
                block.orig_end += current_orig_pos + space_offset
                block.trans_start += current_trans_pos + space_offset
                block.trans_end += current_trans_pos + space_offset
                mapping.blocks.append(block)
                
                # Update the mapping dictionaries
                if block.original not in mapping.original_to_block:
                    mapping.original_to_block[block.original] = []
                mapping.original_to_block[block.original].append(block)
                
                if block.translated not in mapping.translated_to_block:
                    mapping.translated_to_block[block.translated] = []
                mapping.translated_to_block[block.translated].append(block)
            
            # Update positions for next line
            current_orig_pos += len(line)
            current_trans_pos += len(leading_space + converted)
        else:
            result_lines.append(line)
            # Update positions for empty lines
            current_orig_pos += len(line)
            current_trans_pos += len(line)
    
    return ''.join(result_lines), mapping

def preprocess_text(text: str) -> str:
    """
    Preprocess input text for translation.
    
    Args:
        text (str): Input text to preprocess
    Returns:
        str: Preprocessed text
    """
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text

def process_paragraph_new(
    paragraph: str, 
    names2_trie: Dict[str, str], 
    names_trie: Dict[str, str], 
    viet_phrase_trie: Dict[str, str], 
    chinese_phien_am_data: Dict[str, str]
) -> Tuple[str, TranslationMapping]:
    """
    Process and translate a paragraph.
    
    Args:
        paragraph (str): Input paragraph
        names2_trie (Dict[str, str]): Names2 translation dictionary
        names_trie (Dict[str, str]): Names translation dictionary
        viet_phrase_trie (Dict[str, str]): VietPhrase translation dictionary
        chinese_phien_am_data (Dict[str, str]): Chinese Phien Am translation dictionary
    Returns:
        Tuple[str, TranslationMapping]: Translated paragraph and mapping information
    """
    preprocessed_text = preprocess_text(paragraph)
    
    translated_segments = []
    mapping = TranslationMapping()
    
    for segment in preprocessed_text.split():
        translation = (
            viet_phrase_trie.get(segment) or
            names_trie.get(segment) or
            names2_trie.get(segment) or
            segment
        )
        translated_segments.append(translation)
        mapping.add_mapping(segment, translation)
    
    return ' '.join(translated_segments), mapping

def convert_to_sino_vietnamese_new(text: str) -> str:
    """
    Fallback method to convert text to Sino-Vietnamese.
    
    Args:
        text (str): Input text
    Returns:
        str: Converted text
    """
    return text
