import cProfile
import logging
from typing import Callable

def profile_function(func: Callable) -> Callable:
    """
    Decorator to profile a function's performance.

    Args:
        func (Callable): The function to be profiled.

    Returns:
        Callable: The wrapped function with profiling.
    """
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        
        stats = pr.getstats()
        total_calls = sum(stat.callcount for stat in stats)
        total_time = sum(stat.totaltime for stat in stats)
        
        logging.info(f"Performance profile for {func.__name__}:")
        logging.info(f"Total function calls: {total_calls}")
        logging.info(f"Total time: {total_time:.6f} seconds")
        
        return result
    return wrapper
