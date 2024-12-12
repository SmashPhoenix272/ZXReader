import os
from src.QTEngine.models.trie import Trie

class DictionaryManager:
    def __init__(self):
        """Initializes the Dictionary Manager."""
        self.dictionaries = {}
        self.load_dictionaries()

    def load_dictionaries(self):
        """Loads dictionaries from the dictionaries folder."""
        # Get the project root directory (2 levels up from current file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))  # Only go up 2 levels to reach ZXReader
        dictionaries_folder = os.path.join(project_root, 'dictionaries')
        
        if not os.path.exists(dictionaries_folder):
            print(f"Dictionaries folder not found at: {dictionaries_folder}")
            return

        for filename in os.listdir(dictionaries_folder):
            if filename.endswith('.txt'):
                filepath = os.path.join(dictionaries_folder, filename)
                dictionary_name = filename[:-4]  # Remove .txt extension
                self.dictionaries[dictionary_name] = self.load_dictionary(filepath)

    def load_dictionary(self, filepath):
        """
        Loads a dictionary from a given file.

        Args:
            filepath (str): The path to the dictionary file.

        Returns:
            Trie: A Trie object containing the dictionary data.
        """
        trie = Trie()
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:  # Handle UTF-8 BOM
                for line in f:
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2:
                        word, definition = parts
                        # Handle line breaks in definitions (e.g., ThieuChuu, LacViet)
                        definition = definition.replace('\\n', '\n')
                        trie.insert(word, definition)
        except Exception as e:
            print(f"Error loading dictionary from {filepath}: {e}")
        return trie

    def lookup_word(self, word):
        """
        Looks up a word in the loaded dictionaries.

        Args:
            word (str): The word to look up.

        Returns:
            dict: A dictionary containing definitions from different dictionaries.
        """
        results = {}
        for name, trie in self.dictionaries.items():
            definition = trie.search(word)
            if definition:
                results[name] = definition
        return results
