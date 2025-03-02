import os
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.QTEngine.models.trie import Trie
from PyQt5.QtWidgets import QFileDialog, QApplication
import sys
from typing import Dict, Optional, List, Tuple

logger = logging.getLogger(__name__)

class DictionaryManager:
    # Define the order of dictionaries for display
    DICTIONARY_ORDER = ['Names', 'Names2', 'VietPhrase', 'LacViet', 'ThieuChuu', 'Babylon', 'Cedict']

    def __init__(self):
        """Initializes the Dictionary Manager."""
        from src.QTEngine.src.data_loader import DataLoader
        
        logger.info("Initializing DictionaryManager")
        self.dictionaries = {}
        
        # Get dictionaries from QTEngine's singleton DataLoader
        data_loader = DataLoader()
        if data_loader.loaded_data:
            logger.info("Reusing dictionaries from QTEngine's DataLoader")
            self.names2_trie, self.names_trie, self.viet_phrase_trie, self.chinese_phien_am_data, _ = data_loader.loaded_data
            # Map to our dictionary structure
            self.qt_engine_dictionaries = {
                'Names2': self.names2_trie,
                'Names': self.names_trie,
                'VietPhrase': self.viet_phrase_trie
            }
        else:
            logger.warning("QTEngine dictionaries not loaded, initializing empty")
            self.qt_engine_dictionaries = {}
            self.chinese_phien_am_data = {}
            
        self.load_dictionaries()

    def load_dictionaries(self, specific_file: Optional[str] = None):
        """
        Loads dictionaries from the dictionaries folder and QTEngine.
        
        Args:
            specific_file (Optional[str]): If provided, only reload this specific dictionary
        """
        self._loading_start_time = time.time()
        logger.info("Starting dictionary loading process")
        
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        if specific_file:
            # Handle QTEngine dictionaries
            qt_engine_data_folder = os.path.join(project_root, 'src', 'QTEngine', 'data')
            qt_engine_files = {
                'Names': 'Names.txt',
                'Names2': 'Names2.txt',
                'VietPhrase': 'VietPhrase.txt'
            }
            
            # Check if it's a QTEngine dictionary
            for dict_name, filename in qt_engine_files.items():
                if filename == specific_file:
                    filepath = os.path.join(qt_engine_data_folder, filename)
                    if os.path.exists(filepath):
                        self.qt_engine_dictionaries[dict_name] = self.load_dictionary(filepath)
                    return
            
            # Check if it's ChinesePhienAmWords
            if specific_file == 'ChinesePhienAmWords.txt':
                chinese_phien_am_path = os.path.join(qt_engine_data_folder, 'ChinesePhienAmWords.txt')
                if os.path.exists(chinese_phien_am_path):
                    self.load_chinese_phien_am(chinese_phien_am_path)
                return
        else:
            # Load all dictionaries in parallel
            dictionaries_folder = os.path.join(project_root, 'dictionaries')
            if os.path.exists(dictionaries_folder):
                # Collect dictionary files
                dictionary_files = []
                for filename in os.listdir(dictionaries_folder):
                    if filename.endswith('.txt') or filename.endswith('cedict_ts.u8'):
                        filepath = os.path.join(dictionaries_folder, filename)
                        dictionary_name = filename[:-4] if filename.endswith('.txt') else 'Cedict'
                        dictionary_files.append((dictionary_name, filepath))
                
                # Load dictionaries in parallel
                parallel_start = time.time()
                logger.info("Starting parallel dictionary loading")
                with ThreadPoolExecutor(max_workers=4) as executor:
                    # Submit all load tasks
                    load_start = time.time()
                    future_to_dict = {
                        executor.submit(self.load_dictionary, filepath): (name, filepath)
                        for name, filepath in dictionary_files
                    }
                    
                    # Process results as they complete
                    for future in as_completed(future_to_dict):
                        name, filepath = future_to_dict[future]
                        try:
                            trie = future.result()
                            self.dictionaries[name] = trie
                            word_count = len(trie.get_all_words())
                            logger.info(f"Dictionary {name} loaded with {word_count} words")
                        except Exception as e:
                            logger.error(f"Error loading dictionary {name}: {e}")
                
                total_load_time = time.time() - parallel_start
                logger.info(f"All external dictionaries loaded in parallel in {total_load_time:.2f}s")

            # Skip loading QTEngine dictionaries since we're using the singleton instance
            if not self.qt_engine_dictionaries:
                logger.warning("QTEngine dictionaries not available from singleton, skipping")

    def load_dictionary(self, filepath: str, buffer_size: int = 1024*1024) -> Trie:
        """
        Loads a dictionary from a given file with optimized buffering and batch processing.

        Args:
            filepath (str): The path to the dictionary file.
            buffer_size (int): Size of read buffer in bytes (default 1MB).

        Returns:
            Trie: A Trie object containing the dictionary data.
        """
        trie = Trie()
        try:
            if filepath.endswith('cedict_ts.u8'):
                return self.load_cedict_dictionary(filepath)

            # Pre-allocate lists for batch processing
            entries = []
            translation_table = str.maketrans({'\\': '\n', '\t': '    '})
            
            # Use buffered reading for better I/O performance
            with open(filepath, 'r', encoding='utf-8-sig', buffering=buffer_size) as f:
                # Read file in chunks
                chunk = f.read(buffer_size)
                buffer = ""
                
                while chunk:
                    buffer += chunk
                    lines = buffer.split('\n')
                    
                    # Process all complete lines
                    for line in lines[:-1]:
                        if '=' in line:  # Fast check without strip()
                            word, definition = line.split('=', 1)
                            if word and definition:  # Valid entry check
                                # Use translate instead of multiple replaces
                                definition = definition.translate(translation_table)
                                entries.append((word.strip(), definition.strip()))
                    
                    # Keep the partial last line
                    buffer = lines[-1]
                    chunk = f.read(buffer_size)
                
                # Process the last line if any
                if buffer and '=' in buffer:
                    word, definition = buffer.split('=', 1)
                    if word and definition:
                        definition = definition.translate(translation_table)
                        entries.append((word.strip(), definition.strip()))
            
            # Batch insert all entries at once using optimized method
            if entries:
                logger.debug(f"Batch inserting {len(entries)} entries from {filepath}")
                trie.batch_insert(entries)
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
        entries = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):  # Skip comments and empty lines
                        continue
                        
                    parts = line.split(' ', 2)  # Split into traditional, simplified, and rest
                    if len(parts) < 3:
                        continue
                        
                    traditional = parts[0]
                    simplified = parts[1]
                    rest = parts[2]
                    
                    # Extract pinyin and definition
                    pinyin_end = rest.find(']')
                    if pinyin_end == -1:
                        continue
                        
                    pinyin = rest[1:pinyin_end]  # Remove brackets
                    definition = rest[pinyin_end + 2:]  # Skip '] ' to get definition
                    
                    # Store raw data for formatting in dictionary panel
                    entry_data = str({  # Pre-convert to string
                        'traditional': traditional,
                        'simplified': simplified,
                        'pinyin': pinyin,
                        'definition': definition
                    })
                    
                    # Collect both traditional and simplified entries
                    entries.append((traditional, entry_data))
                    if simplified != traditional:
                        entries.append((simplified, entry_data))
                
            # Batch insert all entries at once
            if entries:
                logger.debug(f"Batch inserting {len(entries)} entries from CEDICT")
                trie.batch_insert(entries)
                                    
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
            entry_count = len(self.chinese_phien_am_data)
            logger.info(f"Loaded ChinesePhienAmWords with {entry_count} entries")
        except Exception as e:
            logger.error(f"Error loading ChinesePhienAmWords from {filepath}: {e}")
        
        # Log total loading time at the end of dictionary loading
        if hasattr(self, '_loading_start_time'):
            total_time = time.time() - self._loading_start_time
            logger.info(f"Total dictionary loading completed in {total_time:.2f}s")
            delattr(self, '_loading_start_time')  # Clean up timing variable

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

    def add_to_dictionary(self, dictionary_name: str, word: str, definition: str) -> bool:
        """
        Add a new entry to a dictionary.
        
        Args:
            dictionary_name (str): Name of the dictionary to add to
            word (str): Word to add
            definition (str): Definition of the word
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get dictionary path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            
            if dictionary_name in ["Names", "Names2", "VietPhrase"]:
                filename = f'{dictionary_name}.txt'
                dictionary_path = os.path.join(project_root, 'src', 'QTEngine', 'data', filename)
            else:
                return False
            
            # Read existing content
            with open(dictionary_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            
            # Check if word already exists
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{word}="):
                    # Update existing entry
                    lines[i] = f"{word}={definition}\n"
                    break
            else:
                # Add new entry
                # Ensure the last line ends with a newline
                if lines and not lines[-1].endswith('\n'):
                    lines.append('\n')
                # Add the new entry on a new line
                lines.append(f"{word}={definition}\n")
            
            # Write back to file
            with open(dictionary_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            # Only reload the specific dictionary
            self.load_dictionaries(specific_file=filename)
            
            return True
            
        except Exception as e:
            print(f"Error adding to dictionary {dictionary_name}: {e}")
            return False

    def get_definition(self, dictionary_name: str, word: str) -> Optional[str]:
        """
        Get definition from a specific dictionary.
        
        Args:
            dictionary_name (str): Name of the dictionary
            word (str): Word to look up
            
        Returns:
            Optional[str]: Definition if found, None otherwise
        """
        if dictionary_name in self.qt_engine_dictionaries:
            match = self.find_longest_prefix_match(word, self.qt_engine_dictionaries[dictionary_name])
            if match and match[0] == word:  # Only return if exact match
                return match[1]
        return None
