import os
import time
import logging
import hashlib
import mmap
from typing import Tuple, Dict, Any, Optional, List, Union, BinaryIO
from functools import lru_cache, wraps
from datetime import datetime, timedelta

from src.QTEngine.models.trie import Trie
import src.QTEngine.config as config
from concurrent.futures import ThreadPoolExecutor

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
    
    # Singleton instance
    _instance = None
    _initialized = False
    _lock = None
    
    def __new__(cls, *args, **kwargs):
        """Ensure only one instance is created."""
        if cls._instance is None:
            import threading
            cls._lock = threading.Lock()
            with cls._lock:
                if cls._instance is None:  # Double-check pattern
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self,
                 data_dir: Optional[str] = None,
                 required_files: Optional[List[str]] = None,
                 refresh_interval: timedelta = timedelta(hours=24)):
        """Initialize the DataLoader."""
        # Skip initialization if already done
        if DataLoader._initialized:
            if data_dir and data_dir != self.data_dir:
                logger.warning(f"Ignoring different data_dir: {data_dir}, using existing: {self.data_dir}")
            if required_files and required_files != self.required_files:
                logger.warning(f"Ignoring different required_files, using existing configuration")
            return
            
        with DataLoader._lock:
            if not DataLoader._initialized:
                logger.info("Initializing DataLoader singleton instance")
                self.qt_engine_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.data_dir = data_dir or os.path.join(self.qt_engine_dir, 'data')
                self.required_files = required_files or [
                    'Names2.txt', 'Names.txt', 'VietPhrase.txt', 'ChinesePhienAmWords.txt'
                ]
                self.refresh_interval = refresh_interval
                self.last_load_time = None
                self.loaded_data = None
                self._load_count = 0  # Track number of load attempts
                DataLoader._initialized = True
                logger.info(f"DataLoader initialized with data_dir: {self.data_dir}")

    def _load_cedict_parallel(self, file_path: str, num_workers: int = 8) -> Trie:
        """Load CEDICT dictionary using optimized parallel processing."""
        logger.info("Starting parallel CEDICT loading")
        start_time = time.time()
        trie = Trie()
        
        # Read lines efficiently
        with open(file_path, 'r', encoding='utf-8', buffering=64*1024) as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
        chunk_size = len(lines) // num_workers + 1
        chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
        
        def process_chunk(chunk_lines: List[str]) -> List[Tuple[str, str]]:
            entries = []
            for line in chunk_lines:
                parts = line.split(' ', 2)
                if len(parts) >= 3:
                    traditional, simplified, rest = parts
                    pinyin_end = rest.find(']')
                    if pinyin_end != -1:
                        pinyin = rest[1:pinyin_end]
                        definition = rest[pinyin_end + 2:]
                        entry_data = str({
                            'traditional': traditional,
                            'simplified': simplified,
                            'pinyin': pinyin,
                            'definition': definition
                        })
                        # Add both entries at once to reduce function calls
                        entries.extend([
                            (traditional, entry_data),
                            (simplified, entry_data)
                        ] if simplified != traditional else [(traditional, entry_data)])
            return entries
        
        # Process chunks in parallel with progress tracking
        total_entries = []
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
            for i, future in enumerate(futures, 1):
                entries = future.result()
                total_entries.extend(entries)
                logger.debug(f"Processed chunk {i}/{len(chunks)}")
        
        # Batch insert all entries at once
        logger.info(f"Batch inserting {len(total_entries)} CEDICT entries")
        trie.batch_insert(total_entries)
        
        load_time = time.time() - start_time
        logger.info(f"CEDICT loaded in {load_time:.2f}s")
        return trie
        
    def _mmap_read_lines(self, file_path: str) -> List[str]:
        """Read lines from a file using memory mapping for better performance."""
        lines = []
        with open(file_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                # Process the file in chunks using memory mapping
                current_line = bytearray()
                for chunk in iter(lambda: mm.read(1024*1024), b''):  # 1MB chunks
                    current_line.extend(chunk)
                    while b'\n' in current_line:
                        line, rest = current_line.split(b'\n', 1)
                        try:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.strip():  # Skip empty lines
                                lines.append(decoded_line)
                        except UnicodeDecodeError:
                            logger.warning(f"Skipping invalid UTF-8 line in {file_path}")
                        current_line = rest

                # Handle the last line if any
                if current_line:
                    try:
                        decoded_line = current_line.decode('utf-8')
                        if decoded_line.strip():
                            lines.append(decoded_line)
                    except UnicodeDecodeError:
                        logger.warning(f"Skipping invalid UTF-8 line in {file_path}")
        return lines

    def load_dictionary(self, file_path: str, is_chinese_phien_am: bool = False) -> Dict[str, str]:
        """Load a dictionary file efficiently using buffered reading."""
        entries = {}
        line_count = 0
        entry_count = 0
        try:
            # Use large buffer for better I/O performance
            with open(file_path, 'r', encoding='utf-8-sig', buffering=64*1024) as f:
                for line in f:
                    line_count += 1
                    if not line or line.startswith('#'):
                        continue
                        
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key and value:
                            entries[key] = value
                            entry_count += 1
            
            logger.info(f"Processed {line_count} lines, loaded {entry_count} entries from {os.path.basename(file_path)}")
            if entry_count == 0:
                logger.warning(f"No entries were loaded from {os.path.basename(file_path)}")
            return entries

            logger.info(f"Processed {len(lines)} lines, loaded {entry_count} entries from {os.path.basename(file_path)}")
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
        """Load or reload dictionary data with caching and memory monitoring."""
        
        # Track load attempts
        self._load_count += 1
        logger.info(f"Data load attempt #{self._load_count}")
        
        # Return cached data if it exists and is fresh
        if self.loaded_data is not None and specific_file is None:
            if self.last_load_time and datetime.now() - self.last_load_time < self.refresh_interval:
                logger.info("Using cached dictionary data")
                return self.loaded_data
        
        loading_info: Dict[str, Any] = {
            'files_loaded': [],
            'load_timestamp': datetime.now(),
            'load_attempt': self._load_count
        }
        
        try:
            # Track memory usage
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            logger.info(f"Memory usage before loading: {initial_memory:.2f} MB")
            
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

            # Initialize tries and load with parallel processing
            tries = {
                'names2': Trie(),
                'names': Trie(),
                'viet_phrase': Trie()
            }
            
            def load_dictionary_to_trie(name: str) -> None:
                """Load dictionary and build trie."""
                if not os.path.exists(file_paths[name]):
                    return
                    
                data = self.load_dictionary(file_paths[name])
                entries = [(k, v) for k, v in data.items()]
                tries[name].batch_insert(entries)
                logger.info(f"Loaded {len(entries)} entries for {name}")
            
            if specific_file and self.loaded_data:
                # Reload only the specified dictionary
                names2_trie, names_trie, viet_phrase_trie, chinese_phien_am_data, old_info = self.loaded_data
                if specific_file == 'Names2.txt':
                    load_dictionary_to_trie('names2')
                    tries['names2'] = names2_trie
                elif specific_file == 'Names.txt':
                    load_dictionary_to_trie('names')
                    tries['names'] = names_trie
                elif specific_file == 'VietPhrase.txt':
                    load_dictionary_to_trie('viet_phrase')
                    tries['viet_phrase'] = viet_phrase_trie
                elif specific_file == 'ChinesePhienAmWords.txt':
                    chinese_phien_am_data = self.load_dictionary(file_paths['chinese_phien_am'])
            else:
                # Initialize tries
                tries = {name: Trie() for name in ['names2', 'names', 'viet_phrase']}
                
                # Sort dictionaries by size for better parallel processing
                dict_sizes = {
                    name: os.path.getsize(file_paths[name])
                    for name in ['names2', 'names', 'viet_phrase']
                    if os.path.exists(file_paths[name])
                }
                sorted_dicts = sorted(dict_sizes.items(), key=lambda x: x[1], reverse=True)
                
                with ThreadPoolExecutor(max_workers=4) as executor:
                    # Submit larger dictionaries first
                    tasks = []
                    for name, _ in sorted_dicts:
                        tasks.append(executor.submit(load_dictionary_to_trie, name))
                    
                    # Load ChinesePhienAm in parallel
                    chinese_task = executor.submit(self.load_dictionary, file_paths['chinese_phien_am'])
                    
                    # Process results as they complete with progress tracking
                    total_size = sum(size for _, size in sorted_dicts)
                    loaded_size = 0
                    
                    # Track and report progress for each completed dictionary
                    for future, (name, size) in zip(tasks, sorted_dicts):
                        future.result()
                        loaded_size += size
                        progress = (loaded_size / total_size) * 100
                        logger.info(f"Dictionary progress: {progress:.1f}% ({name} completed)")
                        
                    # Get ChinesePhienAm results
                    chinese_phien_am_data = chinese_task.result()
                    logger.info("Dictionary loading complete")

            # Update loading information with performance metrics
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_change = final_memory - initial_memory
            
            loading_info = {
                'files_loaded': list(file_paths.keys()),
                'file_sizes': {
                    name: os.path.getsize(path) for name, path in file_paths.items()
                },
                'entry_counts': {
                    'Names2': tries['names2'].count(),
                    'Names': tries['names'].count(),
                    'VietPhrase': tries['viet_phrase'].count(),
                    'ChinesePhienAm': len(chinese_phien_am_data)
                },
                'memory': {
                    'initial_mb': initial_memory,
                    'final_mb': final_memory,
                    'change_mb': memory_change
                }
            }
            
            logger.info(f"Dictionary entry counts: {loading_info['entry_counts']}")
            logger.info(f"Memory usage after loading: {final_memory:.2f} MB (Change: {memory_change:+.2f} MB)")
            
            # Store and return results
            self.loaded_data = (
                tries['names2'],
                tries['names'],
                tries['viet_phrase'],
                chinese_phien_am_data,
                loading_info
            )
            self.last_load_time = datetime.now()
            
            # Log summary after successful load
            logger.info(f"Dictionary load #{self._load_count} completed successfully")
            return self.loaded_data

        except Exception as e:
            logger.error(f"Failed to load dictionaries (attempt #{self._load_count}): {e}")
            raise DataLoadError(str(e))

def load_data(data_dir: Optional[str] = None, required_files: Optional[List[str]] = None) -> Tuple[Trie, Trie, Trie, Dict[str, str], Dict[str, Any]]:
    """Backward-compatible function for loading data.
    
    This function maintains backward compatibility while leveraging the singleton pattern.
    It will return cached data if available, preventing unnecessary reloads.
    """
    loader = DataLoader(data_dir, required_files)  # Will return singleton instance
    logger.info("Accessing DataLoader through backward-compatible function")
    return loader.load_data()  # Will use cached data if available
