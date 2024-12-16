import os
from src.QTEngine.models.trie import Trie
from PyQt5.QtWidgets import QFileDialog, QApplication
import sys
from typing import Dict, Optional, List, Tuple

class DictionaryManager:
    # Define the order of dictionaries for display
    DICTIONARY_ORDER = ['Names', 'Names2', 'VietPhrase', 'LacViet', 'ThieuChuu', 'Babylon', 'Cedict']

    def __init__(self):
        """Initializes the Dictionary Manager."""
        self.dictionaries = {}
        self.qt_engine_dictionaries = {}  # QTEngine's dictionaries (Names, Names2, VietPhrase)
        self.chinese_phien_am_data = {}  # Dictionary for ChinesePhienAmWords
        self.load_dictionaries()

    def load_dictionaries(self):
        """Loads dictionaries from the dictionaries folder and QTEngine."""
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Load external dictionaries
        dictionaries_folder = os.path.join(project_root, 'dictionaries')
        if os.path.exists(dictionaries_folder):
            for filename in os.listdir(dictionaries_folder):
                if filename.endswith('.txt') or filename.endswith('cedict_ts.u8'):
                    filepath = os.path.join(dictionaries_folder, filename)
                    dictionary_name = filename[:-4] if filename.endswith('.txt') else 'Cedict'  # Remove .txt extension
                    print(f"Loading dictionary: {dictionary_name} from {filepath}")
                    self.dictionaries[dictionary_name] = self.load_dictionary(filepath)
                    print(f"Dictionary {dictionary_name} loaded with {len(self.dictionaries[dictionary_name].get_all_words())} words")

        # Load QTEngine dictionaries
        qt_engine_data_folder = os.path.join(project_root, 'src', 'QTEngine', 'data')
        if os.path.exists(qt_engine_data_folder):
            qt_engine_files = {
                'Names': 'Names.txt',
                'Names2': 'Names2.txt',
                'VietPhrase': 'VietPhrase.txt'
            }
            for dict_name, filename in qt_engine_files.items():
                filepath = os.path.join(qt_engine_data_folder, filename)
                if os.path.exists(filepath):
                    self.qt_engine_dictionaries[dict_name] = self.load_dictionary(filepath)
            
            # Load ChinesePhienAmWords dictionary
            chinese_phien_am_path = os.path.join(qt_engine_data_folder, 'ChinesePhienAmWords.txt')
            if os.path.exists(chinese_phien_am_path):
                self.load_chinese_phien_am(chinese_phien_am_path)

    def load_dictionary(self, filepath: str) -> Trie:
        """
        Loads a dictionary from a given file.

        Args:
            filepath (str): The path to the dictionary file.

        Returns:
            Trie: A Trie object containing the dictionary data.
        """
        trie = Trie()
        try:
            if filepath.endswith('cedict_ts.u8'):
                return self.load_cedict_dictionary(filepath)
                
            with open(filepath, 'r', encoding='utf-8-sig') as f:  # Handle UTF-8 BOM
                for line in f:
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2:
                        word, definition = parts
                        # Handle line breaks in definitions (e.g., ThieuChuu, LacViet)
                        definition = definition.replace('\\n', '\n').replace('\t', '    ')
                        trie.insert(word, definition)
        except Exception as e:
            print(f"Error loading dictionary from {filepath}: {e}")
        return trie

    def load_cedict_dictionary(self, filepath: str) -> Trie:
        """
        Loads the CC-CEDICT dictionary from a given file.

        Args:
            filepath (str): The path to the cedict file.

        Returns:
            Trie: A Trie object containing the dictionary data.
        """
        trie = Trie()
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip comments and empty lines
                        parts = line.split(' ', 2)  # Split into traditional, simplified, and rest
                        if len(parts) >= 3:
                            traditional = parts[0]
                            simplified = parts[1]
                            rest = parts[2]
                            
                            # Extract pinyin and definition
                            pinyin_end = rest.find(']')
                            if pinyin_end != -1:
                                pinyin = rest[1:pinyin_end]  # Remove brackets
                                definition = rest[pinyin_end + 2:]  # Skip '] ' to get definition
                                
                                # Store raw data for formatting in dictionary panel
                                entry_data = {
                                    'traditional': traditional,
                                    'simplified': simplified,
                                    'pinyin': pinyin,
                                    'definition': definition
                                }
                                
                                # Insert both traditional and simplified characters
                                trie.insert(traditional, str(entry_data))  # Convert dict to string for storage
                                if simplified != traditional:
                                    trie.insert(simplified, str(entry_data))
                                    
        except Exception as e:
            print(f"Error loading CC-CEDICT dictionary from {filepath}: {e}")
        return trie

    def load_chinese_phien_am(self, filepath: str):
        """
        Loads the ChinesePhienAmWords dictionary.

        Args:
            filepath (str): Path to the ChinesePhienAmWords.txt file
        """
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2:
                        word, phien_am = parts
                        self.chinese_phien_am_data[word] = phien_am
            print(f"Loaded ChinesePhienAmWords with {len(self.chinese_phien_am_data)} entries")
        except Exception as e:
            print(f"Error loading ChinesePhienAmWords from {filepath}: {e}")

    def find_longest_prefix_match(self, text: str, dictionary: Trie) -> Optional[Tuple[str, str]]:
        """
        Find the longest prefix match in a dictionary.

        Args:
            text (str): The text to look up.
            dictionary (Trie): The dictionary to search in.

        Returns:
            Optional[Tuple[str, str]]: A tuple of (matched_text, definition) if found, None otherwise.
        """
        # Try exact match first
        match, definition = dictionary.find_longest_prefix(text)
        if match and match == text:  # Only return if it's an exact match and not None
            return match, definition
        return None

    def lookup_word(self, word: str) -> Dict[str, str]:
        """
        Looks up a word in all dictionaries using exact matching.

        Args:
            word (str): The word to look up.

        Returns:
            Dict[str, str]: A dictionary containing definitions from different dictionaries.
        """
        results = {}
        
        # Follow the defined dictionary order
        for name in self.DICTIONARY_ORDER:
            # Skip if already found in this dictionary
            if name in results:
                continue
                
            # Check QTEngine dictionaries first
            if name in self.qt_engine_dictionaries:
                match = self.find_longest_prefix_match(word, self.qt_engine_dictionaries[name])
                if match:  # Only exact matches
                    results[name] = match[1]
                    
            # Then check external dictionaries
            elif name in self.dictionaries:
                match = self.find_longest_prefix_match(word, self.dictionaries[name])
                if match:  # Only exact matches
                    results[name] = match[1]
        return results

    def search_in_definitions(self, query: str) -> Dict[str, List[Tuple[str, str]]]:
        """
        Search for a query string within dictionary definitions.

        Args:
            query (str): The text to search for.

        Returns:
            Dict[str, List[Tuple[str, str]]]: Dictionary name -> list of (word, definition) pairs.
        """
        results = {}
        
        # Search in QTEngine dictionaries
        for name, dictionary in self.qt_engine_dictionaries.items():
            matches = []
            for word in dictionary.get_all_words():
                definition = dictionary.search(word)
                if definition and query.lower() in definition.lower():
                    matches.append((word, definition))
            if matches:
                results[name] = matches

        # Search in external dictionaries
        for name, dictionary in self.dictionaries.items():
            matches = []
            for word in dictionary.get_all_words():
                definition = dictionary.search(word)
                if definition and query.lower() in definition.lower():
                    matches.append((word, definition))
            if matches:
                results[name] = matches

        return results

    def sync_custom_names(self):
        """
        Allows users to load a custom Names2.txt file and sync it with QTEngine's Names2.txt.
        """
        app = QApplication(sys.argv)
        file_path, _ = QFileDialog.getOpenFileName(None, 'Open Custom Names2 File', '', 'Text Files (*.txt);;All Files (*)')
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as custom_file:
                    custom_names = custom_file.read()
                
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(current_dir))
                qt_engine_names2_path = os.path.join(project_root, 'src', 'QTEngine', 'data', 'Names2.txt')

                with open(qt_engine_names2_path, 'w', encoding='utf-8') as qt_engine_file:
                    qt_engine_file.write(custom_names)
                
                print(f"Successfully synced custom Names2.txt with QTEngine's Names2.txt")
                # Reload the dictionaries
                self.load_dictionaries()
            except Exception as e:
                print(f"Error syncing custom Names2.txt: {e}")

    def convert_to_hanviet(self, text: str) -> str:
        """
        Convert Chinese text to Hán Việt using character-by-character mapping.
        
        Args:
            text (str): The Chinese text to convert
            
        Returns:
            str: The Hán Việt reading of the text
        """
        result = []
        for char in text:
            hanviet = self.chinese_phien_am_data.get(char, char)
            result.append(hanviet)
        
        return ' '.join(result)
