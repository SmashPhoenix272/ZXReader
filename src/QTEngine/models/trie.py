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
        Insert multiple words at once efficiently.
        
        Args:
            words (List[Tuple[str, str]]): List of (word, value) tuples
        """
        # Sort words to improve cache locality
        sorted_words = sorted(words, key=lambda x: x[0])
        
        # Pre-allocate common prefixes
        prefix_cache: Dict[str, TrieNode] = {'': self.root}
        
        for word, value in sorted_words:
            current = self.root
            prefix = ''
            
            # Use cached nodes for common prefixes
            for i, char in enumerate(word):
                prefix += char
                if prefix in prefix_cache:
                    current = prefix_cache[prefix]
                    continue
                    
                if char not in current.children:
                    current.children[char] = TrieNode()
                current = current.children[char]
                # Cache prefix nodes for reuse
                if i < len(word) - 1:  # Don't cache leaf nodes
                    prefix_cache[prefix] = current
                    
            current.is_end_of_word = True
            current.value = value
            self.word_count += 1
            
            # Clear cache periodically to prevent memory growth
            if self.word_count % 1000 == 0:
                prefix_cache.clear()
                prefix_cache[''] = self.root

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

    def remove(self, word: str) -> bool:
        """
        Remove a word from the Trie.
        
        Args:
            word (str): Word to remove
            
        Returns:
            bool: True if word was removed, False if not found
        """
        def _remove_helper(node: TrieNode, word: str, depth: int) -> bool:
            if depth == len(word):
                # Word found, remove it
                if node.is_end_of_word:
                    node.is_end_of_word = False
                    node.value = None
                    self.word_count -= 1
                    return True
                return False
                
            char = word[depth]
            if char not in node.children:
                return False
                
            should_delete = _remove_helper(node.children[char], word, depth + 1)
            
            # If child has no other children and is not end of word, remove it
            child = node.children[char]
            if should_delete and not child.children and not child.is_end_of_word:
                del node.children[char]
                
            return should_delete
            
        return _remove_helper(self.root, word, 0)
        
    def find(self, word: str) -> Optional[str]:
        """
        Find the value associated with a word.
        
        Args:
            word (str): Word to look up
            
        Returns:
            Optional[str]: Associated value if found, None otherwise
        """
        current = self.root
        for char in word:
            if char not in current.children:
                return None
            current = current.children[char]
        return current.value if current.is_end_of_word else None

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
