import os
import time
import logging
from typing import Dict, Callable, Optional, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.QTEngine.src.data_loader import DataLoader, DataLoadError

logger = logging.getLogger(__name__)

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
    
    def check_and_reload(self) -> bool:
        """
        Check if any data files have been modified and reload if necessary.
        
        Returns:
            bool: True if data was reloaded, False otherwise
        """
        files_modified = False
        
        for filename in self.data_loader.required_files:
            filepath = os.path.join(self.data_dir, filename)
            
            if not os.path.exists(filepath):
                continue
            
            current_mtime = os.path.getmtime(filepath)
            
            # Check if file has been modified
            if filename not in self.file_mtimes or current_mtime != self.file_mtimes[filename]:
                logger.info(f"Detected changes in {filename}")
                self.file_mtimes[filename] = current_mtime
                files_modified = True
        
        # If any files were modified, reload data
        if files_modified:
            try:
                # Reload data
                reloaded_data = self.data_loader.load_data()
                
                # Call reload callback if provided
                if self.reload_callback:
                    self.reload_callback(reloaded_data)
                
                logger.info("Data successfully reloaded")
                return True
            except DataLoadError as e:
                logger.error(f"Failed to reload data: {e}")
                return False
        
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
                if filename in self.watcher.data_loader.required_files:
                    logger.info(f"File modified: {filename}")
                    self.watcher.check_and_reload()
        
        # Setup file system observer
        event_handler = DataFileHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.data_dir, recursive=False)
        self.observer.start()
        
        if blocking:
            try:
                while True:
                    time.sleep(self.check_interval)
                    self.check_and_reload()
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
