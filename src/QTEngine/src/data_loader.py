import os
import time
import logging
import hashlib
from typing import Tuple, Dict, Any, Optional, List, Union
from functools import lru_cache, wraps
from datetime import datetime, timedelta

from models.trie import Trie
import config

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
        """
        Validate a Trie data structure.
        
        Args:
            trie (Trie): Trie to validate
            min_entries (int): Minimum number of expected entries
        
        Returns:
            bool: Whether the Trie is valid
        """
        if not isinstance(trie, Trie):
            logger.error("Invalid Trie type")
            return False
        
        trie_size = trie.count()
        if trie_size < min_entries:
            logger.warning(f"Trie has fewer entries than expected: {trie_size}")
            return False
        
        return True
    
    @staticmethod
    def validate_dictionary(data: Dict[str, str], min_entries: int = 10) -> bool:
        """
        Validate a dictionary data structure.
        
        Args:
            data (Dict[str, str]): Dictionary to validate
            min_entries (int): Minimum number of expected entries
        
        Returns:
            bool: Whether the dictionary is valid
        """
        if not isinstance(data, dict):
            logger.error("Invalid dictionary type")
            return False
        
        if len(data) < min_entries:
            logger.warning(f"Dictionary has fewer entries than expected: {len(data)}")
            return False
        
        return all(isinstance(k, str) and isinstance(v, str) for k, v in data.items())

def retry_on_failure(max_retries: int = 3, delay: int = 1):
    """
    Decorator to retry a function on failure.
    
    Args:
        max_retries (int): Maximum number of retries
        delay (int): Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay * (attempt + 1))
        return wrapper
    return decorator

@lru_cache(maxsize=config.DATA_LOADER_CONFIG['cache_enabled'] and 32 or 0)
def load_file_cached(file_path: str) -> Dict[str, Any]:
    """
    Cached version of file loading with optional memoization.
    
    Args:
        file_path (str): Full path to the file
    
    Returns:
        Dict[str, Any]: Loaded data
    """
    entries = {}
    try:
        with open(file_path, 'r', encoding=config.DATA_LOADER_CONFIG['encoding']) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split('=') if '=' in line else line.split('\t')
                if len(parts) >= 2:
                    key, value = parts[0], parts[1]
                    entries[key] = value

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise DataLoadError(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        raise DataLoadError(f"Error loading {file_path}: {e}")

    return entries

class DataLoader:
    """
    Advanced data loader with caching, validation, and refresh mechanisms.
    """
    
    def __init__(self, 
                 data_dir: Optional[str] = None, 
                 required_files: Optional[List[str]] = None,
                 refresh_interval: timedelta = timedelta(hours=24)):
        """
        Initialize the DataLoader.
        
        Args:
            data_dir (Optional[str]): Custom data directory
            required_files (Optional[List[str]]): Custom list of required files
            refresh_interval (timedelta): Interval for automatic data refresh
        """
        # Get the absolute path of the QTEngine directory
        self.qt_engine_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Set data directory relative to QTEngine directory if not provided
        if data_dir is None:
            data_dir = os.path.join(self.qt_engine_dir, 'data')
        
        self.data_dir = data_dir
        self.required_files = required_files or [
            'Names2.txt', 'Names.txt', 'VietPhrase.txt', 'ChinesePhienAmWords.txt'
        ]
        self.refresh_interval = refresh_interval
        self.last_load_time = None
        self.loaded_data = None
        
    @retry_on_failure()
    def load_data(self) -> Tuple[Trie, Trie, Trie, Dict[str, str], Dict[str, Any]]:
        """
        Load data from various files into Trie structures and dictionaries.
        
        Returns:
            Tuple containing loaded data structures and loading information
        """
        # Check if data needs refreshing
        if (self.loaded_data is not None and 
            self.last_load_time is not None and 
            datetime.now() - self.last_load_time < self.refresh_interval):
            return self.loaded_data
        
        loading_info: Dict[str, Any] = {'files_loaded': [], 'load_timestamp': datetime.now()}
        
        try:
            # Construct full file paths
            file_paths = {
                'names2': os.path.join(self.data_dir, 'Names2.txt'),
                'names': os.path.join(self.data_dir, 'Names.txt'),
                'viet_phrase': os.path.join(self.data_dir, 'VietPhrase.txt'),
                'chinese_phien_am': os.path.join(self.data_dir, 'ChinesePhienAmWords.txt')
            }
            
            # Load data with validation, making Names2.txt optional
            names2_data = {}
            names2_trie = Trie()
            if os.path.exists(file_paths['names2']):
                names2_data = load_file_cached(file_paths['names2'])
                if DataValidator.validate_dictionary(names2_data):
                    for key in names2_data:
                        names2_trie.insert(key, names2_data[key])
                    if not DataValidator.validate_trie(names2_trie):
                        logger.warning("Names2.txt Trie validation failed, ignoring the file")
                        names2_data = {}
                        names2_trie = Trie()
                else:
                    logger.warning("Names2.txt data validation failed, ignoring the file")
                    names2_data = {}
            
            names_data = load_file_cached(file_paths['names'])
            viet_phrase_data = load_file_cached(file_paths['viet_phrase'])
            chinese_phien_am_data = load_file_cached(file_paths['chinese_phien_am'])
            
            # Validate loaded data
            if not all([
                DataValidator.validate_dictionary(names_data),
                DataValidator.validate_dictionary(viet_phrase_data),
                DataValidator.validate_dictionary(chinese_phien_am_data)
            ]):
                raise DataLoadError("Data validation failed")
            
            # Create Trie structures
            names_trie = Trie()
            viet_phrase_trie = Trie()
            
            for key in names_data:
                names_trie.insert(key, names_data[key])
            for key in viet_phrase_data:
                viet_phrase_trie.insert(key, viet_phrase_data[key])
            
            # Validate Trie structures
            if not all([
                DataValidator.validate_trie(names_trie),
                DataValidator.validate_trie(viet_phrase_trie)
            ]):
                raise DataLoadError("Trie validation failed")
            
            # Update loading information
            loading_info['files_loaded'] = [name for name, path in file_paths.items() if os.path.exists(path)]
            loading_info['file_sizes'] = {
                name: os.path.getsize(path) for name, path in file_paths.items() if os.path.exists(path)
            }
            
            # Cache the results
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
            logger.error(f"Data loading failed: {e}")
            raise DataLoadError(f"Comprehensive data loading failed: {e}")

# Maintain backward compatibility with existing code
def load_data(
    data_dir: Optional[str] = None, 
    required_files: Optional[List[str]] = None
) -> Tuple[Trie, Trie, Trie, Dict[str, str], Dict[str, Any]]:
    """
    Backward-compatible load_data function.
    
    Args:
        data_dir (Optional[str]): Custom data directory
        required_files (Optional[List[str]]): Custom list of required files
    
    Returns:
        Tuple containing loaded data structures and loading information
    """
    loader = DataLoader(data_dir, required_files)
    return loader.load_data()
