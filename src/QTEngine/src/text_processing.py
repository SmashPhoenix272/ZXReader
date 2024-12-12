from typing import List, Tuple, Dict, Optional
from models.trie import Trie
from .character_utils import replace_special_chars, LATIN_CHARS
import re
import logging

def convert_to_sino_vietnamese(
    text: str, 
    names2: Trie, 
    names: Trie, 
    viet_phrase: Trie, 
    chinese_phien_am: Dict[str, str]
) -> str:
    """
    Convert Chinese text to Sino-Vietnamese.

    Args:
        text (str): The input Chinese text.
        names2 (Trie): Trie containing Names2.txt data.
        names (Trie): Trie containing Names.txt data.
        viet_phrase (Trie): Trie containing VietPhrase.txt data.
        chinese_phien_am (Dict[str, str]): Dictionary containing ChinesePhienAmWords.txt data.

    Returns:
        str: The converted Sino-Vietnamese text.

    Raises:
        ValueError: If input parameters are invalid.
    """
    # Input validation
    if not isinstance(text, str):
        raise ValueError(f"Input text must be a string, got {type(text)}")
    
    if not text:
        logging.warning("Empty input text provided")
        return ""
    
    # Validate Trie and dictionary inputs
    for name, obj in [('names2', names2), ('names', names), ('viet_phrase', viet_phrase)]:
        if not isinstance(obj, Trie):
            raise ValueError(f"{name} must be a Trie object")
    
    if not isinstance(chinese_phien_am, dict):
        raise ValueError("chinese_phien_am must be a dictionary")

    text = replace_special_chars(text)
    
    tokens = []
    i = 0
    chunk_size = 1000  # Process text in chunks of 1000 characters internally
    
    while i < len(text):
        chunk = text[i:i+chunk_size]
        j = 0
        
        while j < len(chunk):
            # Check for a sequence of Latin characters
            latin_start = j
            while j < len(chunk) and chunk[j] in LATIN_CHARS:
                j += 1
            if j > latin_start:
                latin_text = chunk[latin_start:j]
                tokens.append(latin_text)
                continue
            
            # Check Names2 first (with value splitting)
            name2_match, value = names2.find_longest_prefix(chunk[j:])
            if name2_match and value is not None:
                tokens.append(split_value(value))
                j += len(name2_match)
                continue
            
            # Check Names (with value splitting)
            name_match, value = names.find_longest_prefix(chunk[j:])
            if name_match and value is not None:
                tokens.append(split_value(value))
                j += len(name_match)
                continue
            
            # Check VietPhrase
            viet_phrase_match, value = viet_phrase.find_longest_prefix(chunk[j:])
            if viet_phrase_match and value is not None:
                tokens.append(split_value(value))
                j += len(viet_phrase_match)
                continue
            
            # Check Chinese Phien Am Words
            if chunk[j:j+1] in chinese_phien_am:
                tokens.append(chinese_phien_am[chunk[j:j+1]])
                j += 1
                continue
            
            # If no match found, add the character as is
            tokens.append(chunk[j])
            j += 1
        
        i += chunk_size

    # Rephrase the tokens
    result = rephrase(tokens)

    # Apply regex transformations directly to the result
    # Remove spaces after left quotation marks and capitalize first word
    result = re.sub(r'([\[\“\‘])\s*(\w)', lambda m: m.group(1) + m.group(2).upper(), result)
    # Remove spaces before right quotation marks
    result = re.sub(r'\s+([”\’\]])', r'\1', result)
    # Capitalize first word after ? and ! marks
    result = re.sub(r'([?!⟨:«])\s+(\w)', lambda m: m.group(1) + ' ' + m.group(2).upper(), result)
    # Remove spaces before colon and semicolon
    result = re.sub(r'\s+([;:?!.])', r'\1', result)
    # Capitalize first word after a single dot, but not after triple dots
    result = re.sub(r'(?<!\.)\.(?!\.)\s+(\w)', lambda m: '. ' + m.group(1).upper(), result)
    return result


def split_value(value: str) -> str:
    """
    Split a value with multiple definitions and return the first non-empty definition.
    
    Args:
        value (str): Input value potentially containing multiple definitions.
    
    Returns:
        str: First non-empty definition of the value, or a space if empty.
    """
    # Check for '=' first to handle special cases like "的=/như thế/đích"
    if '=' in value:
        parts = value.split('=', 1)
        value = parts[1]
    
    # Split by '/' or '|' and return the first non-empty part
    split_parts = value.replace("|", "/").split("/")
    
    # If the first part is an empty string, return a space
    if not split_parts[0].strip():
        return ' '
    
    # Find the first non-empty part
    for part in split_parts:
        stripped_part = part.strip()
        if stripped_part:
            return stripped_part
    
    # If no non-empty part found, return the original value
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
) -> str:
    """
    Process a single paragraph by converting it to Sino-Vietnamese.

    Args:
        paragraph (str): The input paragraph in Chinese.
        names2 (Trie): Trie containing Names2.txt data.
        names (Trie): Trie containing Names.txt data.
        viet_phrase (Trie): Trie containing VietPhrase.txt data.
        chinese_phien_am (Dict[str, str]): Dictionary containing ChinesePhienAmWords.txt data.

    Returns:
        str: The processed paragraph in Sino-Vietnamese.
    """
    # Split the paragraph into lines while preserving empty lines
    lines = paragraph.splitlines(keepends=True)
    result_lines = []
    
    for line in lines:
        # Preserve leading whitespace
        leading_space = ''
        for char in line:
            if char.isspace():
                leading_space += char
            else:
                break
                
        # Convert the actual content
        content = line.lstrip()
        if content:  # Only convert non-empty content
            converted = convert_to_sino_vietnamese(content, names2, names, viet_phrase, chinese_phien_am)
            result_lines.append(leading_space + converted)
        else:  # Preserve empty lines
            result_lines.append(line)
    
    return ''.join(result_lines)


def preprocess_text(text: str) -> str:
    """
    Preprocess input text for translation.
    
    :param text: Input text to preprocess
    :return: Preprocessed text
    """
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Convert to lowercase (optional, depends on translation strategy)
    text = text.lower()
    
    # Remove punctuation (optional)
    text = re.sub(r'[^\w\s]', '', text)
    
    return text


def process_paragraph_new(
    paragraph: str, 
    names2_trie: Dict[str, str], 
    names_trie: Dict[str, str], 
    viet_phrase_trie: Dict[str, str], 
    chinese_phien_am_data: Dict[str, str]
) -> str:
    """
    Process and translate a paragraph.
    
    :param paragraph: Input paragraph
    :param names2_trie: Names2 translation dictionary
    :param names_trie: Names translation dictionary
    :param viet_phrase_trie: VietPhrase translation dictionary
    :param chinese_phien_am_data: Chinese Phien Am translation dictionary
    :return: Translated paragraph
    """
    # Placeholder for backward compatibility
    preprocessed_text = preprocess_text(paragraph)
    
    # Implement basic translation logic
    translated_segments = []
    for segment in preprocessed_text.split():
        # Attempt translations in order of priority
        translation = (
            viet_phrase_trie.get(segment) or
            names_trie.get(segment) or
            names2_trie.get(segment) or
            segment
        )
        translated_segments.append(translation)
    
    return ' '.join(translated_segments)


def convert_to_sino_vietnamese_new(text: str) -> str:
    """
    Fallback method to convert text to Sino-Vietnamese.
    
    :param text: Input text
    :return: Converted text
    """
    # Placeholder implementation
    return text
