import os
import time
import logging
from typing import Dict, Callable, Optional, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Timer

from src.QTEngine.src.data_loader import DataLoader, DataLoadError

logger = logging.getLogger(__name__)

def debounce(wait):
    """Decorator to debounce a function."""
    def decorator(fn):
        timer = None
        def debounced(*args, **kwargs):
            nonlocal timer
            if timer is not None:
                timer.cancel()
            timer = Timer(wait, lambda: fn(*args, **kwargs))
            timer.start()
        return debounced
    return decorator

class DataFileWatcher:
    """
    A sophisticated file watcher for data files with intelligent reloading.
    
    This class monitors specified data files and provides an efficient mechanism
    to reload data when files are modified, with minimal overhead.
    """
    
    def __init__(self, 
                 data_dir: str, 
                 reload_callback: Optional[Callable] = None,
                 check_interval: float = 1.0):
        """
        Initialize the DataFileWatcher.
        
        Args:
            data_dir (str): Directory containing data files to watch
            reload_callback (Optional[Callable]): Function to call when data is reloaded
            check_interval (float): Interval to check for file changes in seconds
        """
        self.data_dir = data_dir
        self.reload_callback = reload_callback
        self.check_interval = check_interval
        self.data_loader = DataLoader(data_dir=data_dir)
        
        # Track file modification times
        self.file_mtimes: Dict[str, float] = {}
        self._initialize_file_mtimes()
        self.observer = None
    
    def _initialize_file_mtimes(self):
        """
        Initialize modification times for all watched files.
        """
        for filename in self.data_loader.required_files:
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                self.file_mtimes[filename] = os.path.getmtime(filepath)
    
    @debounce(2.0)  # Increased to 2 seconds to prevent cascading reloads
    def reload_data(self, filename: Optional[str] = None):
        """
        Reload data with debouncing.
        
        Args:
            filename (Optional[str]): If provided, only reload this specific file
        """
        try:
            # Skip reloading if file is not in required files
            if filename and filename not in self.data_loader.required_files:
                return True
                
            # Get current mtime before reload
            filepath = os.path.join(self.data_dir, filename) if filename else None
            before_mtime = os.path.getmtime(filepath) if filepath and os.path.exists(filepath) else 0

            # Pass the specific file to load_data for selective reloading
            reloaded_data = self.data_loader.load_data(specific_file=filename)
            
            # Update file mtime after successful reload
            if filepath and os.path.exists(filepath):
                self.file_mtimes[filename] = os.path.getmtime(filepath)

            # Only call callback if the file actually changed
            if self.reload_callback and (not filepath or os.path.getmtime(filepath) > before_mtime):
                self.reload_callback(reloaded_data)
                logger.info(f"Successfully reloaded data for {filename}")
            return True
        except DataLoadError as e:
            logger.error(f"Failed to reload data: {e}")
            return False
    
    def start_watching(self, blocking: bool = False):
        """
        Start watching data files for changes.
        
        Args:
            blocking (bool): Whether to block the main thread
        """
        class DataFileHandler(FileSystemEventHandler):
            def __init__(self, watcher):
                self.watcher = watcher
            
            def on_modified(self, event):
                if event.is_directory:
                    return
                
                filename = os.path.basename(event.src_path)
                filepath = event.src_path
                
                # Only reload if it's a required file
                if filename in self.watcher.data_loader.required_files:
                    try:
                        # Get actual file modification time
                        current_mtime = os.path.getmtime(filepath)
                        last_mtime = self.watcher.file_mtimes.get(filename, 0)
                        
                        # Only reload if file actually changed
                        if current_mtime > last_mtime + 0.1:  # Add small buffer for filesystem precision
                            logger.info(f"File modified: {filename}")
                            # Update modification time only after successful load
                            prev_mtime = self.watcher.file_mtimes.get(filename, 0)
                            # Only reload the specific changed file
                            self.watcher.reload_data(filename=filename)
                    except FileNotFoundError:
                        logger.warning(f"Could not access file: {filename}")
                    except Exception as e:
                        logger.error(f"Error handling file modification for {filename}: {e}")
                else:
                    logger.debug(f"Ignoring modification of non-required file: {filename}")
        
        # Setup file system observer
        event_handler = DataFileHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.data_dir, recursive=False)
        self.observer.start()
        
        if blocking:
            try:
                while True:
                    time.sleep(self.check_interval)
            except KeyboardInterrupt:
                self.observer.stop()
            self.observer.join()
        
        return self.observer
    
    def stop(self):
        """
        Stop watching data files for changes.
        """
        if self.observer:
            self.observer.stop()
            self.observer.join()

def create_data_watcher(data_dir: str, 
                        reload_callback: Optional[Callable] = None) -> DataFileWatcher:
    """
    Convenience function to create and start a DataFileWatcher.
    
    Args:
        data_dir (str): Directory containing data files
        reload_callback (Optional[Callable]): Function to call on data reload
    
    Returns:
        DataFileWatcher: Configured and started file watcher
    """
    watcher = DataFileWatcher(data_dir, reload_callback)
    watcher.start_watching()
    return watcher
