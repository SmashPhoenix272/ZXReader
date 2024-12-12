from typing import Dict, List, Tuple, Optional, Union
import sys

class TrieNode:
    __slots__ = ['children', 'is_end_of_word', 'value']
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_word: bool = False
        self.value: Optional[str] = None

class Trie:
    def __init__(self, memory_optimize: bool = False):
        """
        Initialize a Trie data structure.
        
        Args:
            memory_optimize (bool): If True, uses more memory-efficient strategies.
        """
        self.root: TrieNode = TrieNode()
        self.word_count: int = 0
        self._memory_optimize = memory_optimize

    def insert(self, word: str, value: str) -> None:
        """
        Insert a word and its associated value into the Trie.
        
        Args:
            word (str): The key to insert
            value (str): The value associated with the key
        """
        current = self.root
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.is_end_of_word = True
        current.value = value
        self.word_count += 1

        # Optional memory optimization
        if self._memory_optimize and sys.getsizeof(current.children) > 1024:
            current.children = dict(list(current.children.items())[:10])  # Keep only 10 most recent

    def batch_insert(self, words: List[Tuple[str, str]]) -> None:
        """
        Insert multiple words at once.
        
        Args:
            words (List[Tuple[str, str]]): List of (word, value) tuples
        """
        for word, value in words:
            self.insert(word, value)

    def contains(self, word: str) -> bool:
        """
        Check if a word exists in the Trie.
        
        Args:
            word (str): Word to check
        
        Returns:
            bool: True if word exists, False otherwise
        """
        current = self.root
        for char in word:
            if char not in current.children:
                return False
            current = current.children[char]
        return current.is_end_of_word

    def count(self) -> int:
        """
        Get the total number of words in the Trie.
        
        Returns:
            int: Number of words
        """
        return self.word_count

    def find_longest_prefix(self, text: str) -> Tuple[str, Optional[str]]:
        """
        Find the longest prefix match in the Trie.
        
        Args:
            text (str): Text to find prefix in
        
        Returns:
            Tuple[str, Optional[str]]: Longest prefix and its associated value
        """
        current = self.root
        longest_prefix = ""
        longest_value = None
        prefix = []
        for char in text:
            if char not in current.children:
                break
            current = current.children[char]
            prefix.append(char)
            if current.is_end_of_word:
                longest_prefix = ''.join(prefix)
                longest_value = current.value
        return longest_prefix, longest_value

    def get_all_words(self) -> List[Tuple[str, str]]:
        """
        Retrieve all words and their values from the Trie.
        
        Returns:
            List[Tuple[str, str]]: List of (word, value) tuples
        """
        words = []
        def dfs(node: TrieNode, current_word: str):
            if node.is_end_of_word:
                words.append((current_word, node.value))
            for char, child_node in node.children.items():
                dfs(child_node, current_word + char)
        
        dfs(self.root, "")
        return words