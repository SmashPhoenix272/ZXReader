"""
Configuration constants for QTEngine.

This module centralizes configuration parameters to make them easily 
modifiable without changing core implementation code.
"""

import os
from typing import Dict, Any

# Project Paths
PROJECT_PATHS = {
    'root': os.path.dirname(os.path.abspath(__file__)),
    'src': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'),
    'data': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'),
    'models': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
}

# Data Loader Configuration
DATA_LOADER_CONFIG = {
    'data_directory': PROJECT_PATHS['data'],
    'required_files': [
        'Names2.txt', 
        'Names.txt', 
        'VietPhrase.txt'
    ],
    'encoding': 'utf-8',
    'min_entries': 10,  # Minimum entries required for a valid translation file
    'cache_enabled': True,
    'cache_duration_minutes': 60
}

# Translation Configuration
TRANSLATION_CONFIG = {
    'default_strategy': 'trie_based',
    'fallback_strategy': 'character_conversion',
    'performance_logging': True,
    'quality_threshold': 0.7,
    'parallel_processing': True,
    'use_rust_trie': True  # New configuration for Rust Trie
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.path.join(PROJECT_PATHS['root'], 'qtengine.log')
}

def get_config(config_type: str = 'default') -> Dict[str, Any]:
    """
    Retrieve configuration dictionary based on type.
    
    :param config_type: Type of configuration to retrieve
    :return: Configuration dictionary
    """
    config_map = {
        'data_loader': DATA_LOADER_CONFIG,
        'translation': TRANSLATION_CONFIG,
        'logging': LOGGING_CONFIG,
        'default': {**DATA_LOADER_CONFIG, **TRANSLATION_CONFIG, **LOGGING_CONFIG}
    }
    
    return config_map.get(config_type, config_map['default'])

# Optional: Validate configuration on import
def validate_config():
    """
    Validate configuration settings.
    """
    assert os.path.exists(PROJECT_PATHS['data']), f"Data directory not found: {PROJECT_PATHS['data']}"
    assert len(DATA_LOADER_CONFIG['required_files']) > 0, "No required files specified"
    assert DATA_LOADER_CONFIG['min_entries'] >= 0, "Minimum entries must be non-negative"

validate_config()
