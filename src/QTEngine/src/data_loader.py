import os
import time
import logging
import hashlib
from typing import Tuple, Dict, Any, Optional, List, Union
from functools import lru_cache, wraps
from datetime import datetime, timedelta

from src.QTEngine.models.trie import Trie
import src.QTEngine.config as config

# Configure logging based on config
logging.basicConfig(
    level=getattr(logging, config.LOGGING_CONFIG['level']),
    format=config.LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)

class DataLoadError(Exception):
    """Custom exception for data loading errors."""
    pass

class DataValidator:
    """Utility class for validating loaded data."""
    
    @staticmethod
    def validate_trie(trie: Trie, min_entries: int = 10) -> bool:
        """Validate a Trie data structure."""
        if not isinstance(trie, Trie):
            logger.error("Invalid Trie type")
            return False
        
        trie_size = trie.count()
        if trie_size < min_entries:
            logger.warning(f"Trie has fewer entries than expected: {trie_size}")
            return False
        
        return True
    
    @staticmethod
    def validate_dictionary(data: Dict[str, str], min_entries: int = 0) -> bool:
        """Validate a dictionary data structure."""
        if not isinstance(data, dict):
            logger.error("Invalid dictionary type")
            return False
        
        if len(data) < min_entries:
            keys = list(data.keys())
            sample_keys = keys[:5] if keys else []
            logger.warning(f"Dictionary has fewer entries than expected ({len(data)} < {min_entries}): {sample_keys}")
        
        return True

def retry_on_failure(max_retries: int = 3, delay: int = 1):
    """Decorator that retries a function on failure with DataLoadError."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    return result
                except DataLoadError as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Loading attempt {attempt + 1} failed: {e}")
                        time.sleep(delay)
                        continue
                    logger.error(f"All {max_retries} loading attempts failed")
                    raise
            return result  # Should never reach here due to raise above
        return wrapper
    return decorator

class DataLoader:
    """Advanced data loader with caching, validation, and refresh mechanisms."""
    
    def __init__(self, 
                 data_dir: Optional[str] = None, 
                 required_files: Optional[List[str]] = None,
                 refresh_interval: timedelta = timedelta(hours=24)):
        """Initialize the DataLoader."""
        self.qt_engine_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = data_dir or os.path.join(self.qt_engine_dir, 'data')
        self.required_files = required_files or [
            'Names2.txt', 'Names.txt', 'VietPhrase.txt', 'ChinesePhienAmWords.txt'
        ]
        self.refresh_interval = refresh_interval
        self.last_load_time = None
        self.loaded_data = None

    def load_dictionary(self, file_path: str, is_chinese_phien_am: bool = False) -> Dict[str, str]:
        """Load a dictionary file with proper format handling."""
        entries = {}
        try:
            line_count = 0
            entry_count = 0
            with open(file_path, 'r', encoding=config.DATA_LOADER_CONFIG['encoding']) as f:
                for line in f:
                    line_count += 1
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # All dictionaries use = as separator
                    if '=' in line:
                        key, value = line.split('=', 1)
                    else:
                        key, *value_parts = line.split('\t')
                        value = value_parts[0] if value_parts else None

                    key = key.strip()
                    value = value.strip() if value else None
                        
                    if key and value:
                        entries[key] = value
                        entry_count += 1

            logger.info(f"Processed {line_count} lines, loaded {entry_count} entries from {os.path.basename(file_path)}")
            if entry_count == 0:
                logger.warning(f"No entries were loaded from {os.path.basename(file_path)}")
            return entries

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise DataLoadError(f"File not found: {file_path}")
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            raise DataLoadError(f"Error loading {file_path}: {e}")

    @retry_on_failure()
    def load_data(self, specific_file: Optional[str] = None) -> Tuple[Trie, Trie, Trie, Dict[str, str], Dict[str, Any]]:
        """Load or reload dictionary data."""
        loading_info: Dict[str, Any] = {'files_loaded': [], 'load_timestamp': datetime.now()}
        try:
            file_paths = {
                'names2': os.path.join(self.data_dir, 'Names2.txt'),
                'names': os.path.join(self.data_dir, 'Names.txt'),
                'viet_phrase': os.path.join(self.data_dir, 'VietPhrase.txt'),
                'chinese_phien_am': os.path.join(self.data_dir, 'ChinesePhienAmWords.txt')
            }
            
            # Verify files exist
            missing_files = [name for name, path in file_paths.items() if not os.path.exists(path)]
            if missing_files:
                raise DataLoadError(f"Missing files: {missing_files} in {self.data_dir}")

            if specific_file and self.loaded_data:
                names2_trie, names_trie, viet_phrase_trie, chinese_phien_am_data, old_info = self.loaded_data
                
                if specific_file == 'Names2.txt':
                    names2_data = self.load_dictionary(file_paths['names2'])
                    names2_trie = Trie()
                    for key, value in names2_data.items():
                        names2_trie.insert(key, value)
                        
                elif specific_file == 'Names.txt':
                    names_data = self.load_dictionary(file_paths['names'])
                    names_trie = Trie()
                    for key, value in names_data.items():
                        names_trie.insert(key, value)
                        
                elif specific_file == 'VietPhrase.txt':
                    viet_phrase_data = self.load_dictionary(file_paths['viet_phrase'])
                    viet_phrase_trie = Trie()
                    for key, value in viet_phrase_data.items():
                        viet_phrase_trie.insert(key, value)
                        
                elif specific_file == 'ChinesePhienAmWords.txt':
                    chinese_phien_am_data = self.load_dictionary(
                        file_paths['chinese_phien_am']
                    )
                
            else:
                # Load all data
                names2_trie = Trie()
                names_trie = Trie()
                viet_phrase_trie = Trie()
                
                # Load dictionaries
                names2_data = self.load_dictionary(file_paths['names2']) if os.path.exists(file_paths['names2']) else {}
                names_data = self.load_dictionary(file_paths['names'])
                viet_phrase_data = self.load_dictionary(file_paths['viet_phrase'])
                chinese_phien_am_data = self.load_dictionary(file_paths['chinese_phien_am'])

                # Populate tries
                for key, value in names2_data.items():
                    names2_trie.insert(key, value)
                for key, value in names_data.items():
                    names_trie.insert(key, value)
                for key, value in viet_phrase_data.items():
                    viet_phrase_trie.insert(key, value)

            # Update loading information
            loading_info['files_loaded'] = list(file_paths.keys())
            loading_info['file_sizes'] = {
                name: os.path.getsize(path) for name, path in file_paths.items()
            }
            loading_info['entry_counts'] = {
                'Names2': names2_trie.count(),
                'Names': names_trie.count(),
                'VietPhrase': viet_phrase_trie.count(),
                'ChinesePhienAm': len(chinese_phien_am_data)
            }

            logger.info(f"Dictionary entry counts: {loading_info['entry_counts']}")

            # Cache and return results
            self.loaded_data = (
                names2_trie,
                names_trie,
                viet_phrase_trie,
                chinese_phien_am_data,
                loading_info
            )
            self.last_load_time = datetime.now()
            return self.loaded_data

        except Exception as e:
            logger.error(f"Failed to load dictionaries: {e}")
            raise DataLoadError(str(e))

def load_data(data_dir: Optional[str] = None, required_files: Optional[List[str]] = None) -> Tuple[Trie, Trie, Trie, Dict[str, str], Dict[str, Any]]:
    """Backward-compatible function for loading data."""
    loader = DataLoader(data_dir, required_files)
    return loader.load_data()
