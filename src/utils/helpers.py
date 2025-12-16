"""
Utility Helper Functions Module for Business Intelligence System
Contains common helper functions used throughout the application
"""

import os
import sys
import json
import logging
import hashlib
import random
import string
import inspect
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from pathlib import Path
import csv
import pickle
import gzip
import shutil
import re
import math
import statistics
from decimal import Decimal, ROUND_HALF_UP
import time
from contextlib import contextmanager
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# File and Directory Operations
# ============================================================================

def ensure_directory(directory_path: str) -> bool:
    """
    Ensure a directory exists, create if it doesn't
    
    Args:
        directory_path: Path to directory
    
    Returns:
        bool: True if directory exists or was created
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        return False


def get_file_size(file_path: str, human_readable: bool = True) -> Union[int, str]:
    """
    Get file size in bytes or human-readable format
    
    Args:
        file_path: Path to file
        human_readable: Return human-readable string if True
    
    Returns:
        Union[int, str]: File size
    """
    try:
        size = os.path.getsize(file_path)
        
        if human_readable:
            # Convert to human readable format
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    return f"{size:.2f} {unit}"
                size /= 1024.0
            return f"{size:.2f} PB"
        else:
            return size
    except Exception as e:
        logger.error(f"Error getting file size for {file_path}: {e}")
        return 0 if not human_readable else "0 B"


def safe_delete(file_path: str, max_retries: int = 3) -> bool:
    """
    Safely delete a file with retries
    
    Args:
        file_path: Path to file
        max_retries: Maximum number of retry attempts
    
    Returns:
        bool: True if file was deleted
    """
    for attempt in range(max_retries):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Deleted file: {file_path}")
                return True
            else:
                logger.debug(f"File does not exist: {file_path}")
                return True
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed to delete {file_path}: {e}")
            time.sleep(0.1 * (attempt + 1))  # Exponential backoff
    
    logger.error(f"Failed to delete file after {max_retries} attempts: {file_path}")
    return False


def copy_file_safe(source: str, destination: str, overwrite: bool = True) -> bool:
    """
    Copy file with error handling
    
    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Overwrite if destination exists
    
    Returns:
        bool: True if copy successful
    """
    try:
        # Check if source exists
        if not os.path.exists(source):
            logger.error(f"Source file does not exist: {source}")
            return False
        
        # Check if destination exists
        if os.path.exists(destination) and not overwrite:
            logger.warning(f"Destination file exists and overwrite is False: {destination}")
            return False
        
        # Ensure destination directory exists
        dest_dir = os.path.dirname(destination)
        ensure_directory(dest_dir)
        
        # Copy file
        shutil.copy2(source, destination)
        logger.debug(f"Copied {source} to {destination}")
        return True
    
    except Exception as e:
        logger.error(f"Error copying {source} to {destination}: {e}")
        return False


def find_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
    """
    Find all files with given extensions in directory
    
    Args:
        directory: Directory to search
        extensions: List of file extensions (with or without dot)
    
    Returns:
        List[str]: List of file paths
    """
    files = []
    try:
        # Normalize extensions
        normalized_extensions = [ext if ext.startswith('.') else f'.{ext}' 
                                for ext in extensions]
        
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if any(filename.lower().endswith(ext.lower()) 
                      for ext in normalized_extensions):
                    files.append(os.path.join(root, filename))
        
        logger.debug(f"Found {len(files)} files with extensions {extensions} in {directory}")
    
    except Exception as e:
        logger.error(f"Error finding files in {directory}: {e}")
    
    return files


# ============================================================================
# Data Processing Helpers
# ============================================================================

def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize a filename by removing invalid characters
    
    Args:
        filename: Original filename
        max_length: Maximum length of filename
    
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Truncate if too long
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        max_name_length = max_length - len(ext)
        sanitized = name[:max_name_length] + ext
    
    return sanitized


def generate_random_string(length: int = 8, 
                          include_digits: bool = True,
                          include_special: bool = False) -> str:
    """
    Generate a random string
    
    Args:
        length: Length of string
        include_digits: Include digits
        include_special: Include special characters
    
    Returns:
        str: Random string
    """
    characters = string.ascii_letters
    
    if include_digits:
        characters += string.digits
    
    if include_special:
        characters += "!@#$%^&*()_-+=[]{}|;:,.<>?"
    
    return ''.join(random.choice(characters) for _ in range(length))


def calculate_hash(data: Union[str, bytes], algorithm: str = 'sha256') -> str:
    """
    Calculate hash of data
    
    Args:
        data: Data to hash (string or bytes)
        algorithm: Hash algorithm
    
    Returns:
        str: Hash string
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    if algorithm == 'md5':
        hash_obj = hashlib.md5()
    elif algorithm == 'sha1':
        hash_obj = hashlib.sha1()
    elif algorithm == 'sha256':
        hash_obj = hashlib.sha256()
    elif algorithm == 'sha512':
        hash_obj = hashlib.sha512()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    hash_obj.update(data)
    return hash_obj.hexdigest()


def format_currency(amount: Union[int, float, Decimal], 
                   currency_symbol: str = '$',
                   decimal_places: int = 2) -> str:
    """
    Format amount as currency
    
    Args:
        amount: Amount to format
        currency_symbol: Currency symbol
        decimal_places: Number of decimal places
    
    Returns:
        str: Formatted currency string
    """
    if isinstance(amount, Decimal):
        amount = float(amount)
    
    # Handle negative amounts
    is_negative = amount < 0
    amount = abs(amount)
    
    # Format with commas and decimal places
    formatted = f"{amount:,.{decimal_places}f}"
    
    # Add currency symbol and negative sign
    if is_negative:
        return f"-{currency_symbol}{formatted}"
    else:
        return f"{currency_symbol}{formatted}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format value as percentage
    
    Args:
        value: Value to format (0.5 = 50%)
        decimal_places: Number of decimal places
    
    Returns:
        str: Formatted percentage string
    """
    return f"{value * 100:.{decimal_places}f}%"


def round_to_nearest(value: float, nearest: float = 0.01) -> float:
    """
    Round value to nearest specified increment
    
    Args:
        value: Value to round
        nearest: Nearest increment to round to
    
    Returns:
        float: Rounded value
    """
    return round(value / nearest) * nearest


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values
    
    Args:
        old_value: Old value
        new_value: New value
    
    Returns:
        float: Percentage change (as decimal, 0.1 = 10%)
    """
    if old_value == 0:
        return float('inf') if new_value > 0 else 0
    
    return (new_value - old_value) / old_value


def calculate_moving_average(values: List[float], window_size: int) -> List[float]:
    """
    Calculate moving average
    
    Args:
        values: List of values
        window_size: Size of moving window
    
    Returns:
        List[float]: Moving averages
    """
    if not values or window_size <= 0:
        return []
    
    if window_size > len(values):
        window_size = len(values)
    
    moving_averages = []
    for i in range(len(values) - window_size + 1):
        window = values[i:i + window_size]
        moving_averages.append(statistics.mean(window))
    
    return moving_averages


# ============================================================================
# Date and Time Helpers
# ============================================================================

def parse_date(date_string: str, 
               formats: List[str] = None) -> Optional[datetime]:
    """
    Parse date string with multiple format attempts
    
    Args:
        date_string: Date string to parse
        formats: List of date formats to try
    
    Returns:
        Optional[datetime]: Parsed datetime or None
    """
    if formats is None:
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y%m%d',
            '%b %d, %Y',
            '%B %d, %Y',
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse date: {date_string}")
    return None


def format_timedelta(delta: timedelta, 
                    include_seconds: bool = False) -> str:
    """
    Format timedelta as human-readable string
    
    Args:
        delta: Time delta to format
        include_seconds: Include seconds in output
    
    Returns:
        str: Formatted time delta
    """
    total_seconds = int(delta.total_seconds())
    
    # Calculate components
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    
    if days > 0:
        parts.append(f"{days}d")
    
    if hours > 0:
        parts.append(f"{hours}h")
    
    if minutes > 0:
        parts.append(f"{minutes}m")
    
    if include_seconds and seconds > 0:
        parts.append(f"{seconds}s")
    
    if not parts:  # Less than a minute
        if include_seconds:
            return f"{seconds}s"
        else:
            return "0m"
    
    return " ".join(parts)


def get_date_range(start_date: Union[str, datetime], 
                   end_date: Union[str, datetime],
                   step: str = 'day') -> List[datetime]:
    """
    Generate list of dates between start and end
    
    Args:
        start_date: Start date
        end_date: End date
        step: Step size ('day', 'week', 'month')
    
    Returns:
        List[datetime]: List of dates
    """
    # Parse dates if strings
    if isinstance(start_date, str):
        start_date = parse_date(start_date)
    if isinstance(end_date, str):
        end_date = parse_date(end_date)
    
    if not start_date or not end_date:
        return []
    
    # Ensure start <= end
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date)
        
        if step == 'day':
            current_date += timedelta(days=1)
        elif step == 'week':
            current_date += timedelta(weeks=1)
        elif step == 'month':
            # Add approximately one month
            year = current_date.year
            month = current_date.month + 1
            if month > 12:
                month = 1
                year += 1
            try:
                current_date = current_date.replace(year=year, month=month)
            except ValueError:
                # Handle invalid dates (e.g., Feb 31)
                current_date += timedelta(days=31)
    
    return dates


def is_business_day(date: datetime) -> bool:
    """
    Check if date is a business day (Monday-Friday)
    
    Args:
        date: Date to check
    
    Returns:
        bool: True if business day
    """
    return date.weekday() < 5  # Monday=0, Friday=4


# ============================================================================
# Validation Helpers
# ============================================================================

def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
    
    Returns:
        bool: True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str, country_code: str = 'US') -> bool:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
        country_code: Country code for validation
    
    Returns:
        bool: True if valid phone format
    """
    # Simple validation - can be extended per country
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    if country_code == 'US':
        # US format: 10 digits
        return bool(re.match(r'^\d{10}$', phone))
    else:
        # Generic international validation
        return bool(re.match(r'^\d{7,15}$', phone))


def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
    
    Returns:
        bool: True if valid URL format
    """
    pattern = r'^(https?://)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*/?$'
    return bool(re.match(pattern, url, re.IGNORECASE))


def validate_file_path(path: str, check_exists: bool = False) -> Tuple[bool, str]:
    """
    Validate file path
    
    Args:
        path: Path to validate
        check_exists: Check if file exists
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Check for invalid characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        if char in path:
            return False, f"Invalid character in path: '{char}'"
    
    # Check path length
    if len(path) > 260:  # Windows max path length
        return False, f"Path too long ({len(path)} > 260 characters)"
    
    # Check if file exists (if requested)
    if check_exists and not os.path.exists(path):
        return False, "File does not exist"
    
    return True, ""


# ============================================================================
# Performance and Debugging Helpers
# ============================================================================

@contextmanager
def timer(name: str = "Operation"):
    """
    Context manager to measure execution time
    
    Args:
        name: Name of the operation
    
    Usage:
        with timer("My operation"):
            # code to time
    """
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        logger.info(f"{name} took {elapsed:.4f} seconds")


def measure_performance(func: Callable) -> Callable:
    """
    Decorator to measure function performance
    
    Args:
        func: Function to decorate
    
    Returns:
        Callable: Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"Starting {func_name}")
        
        with timer(func_name):
            result = func(*args, **kwargs)
        
        logger.debug(f"Completed {func_name}")
        return result
    
    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0, 
          backoff_factor: float = 2.0,
          exceptions: tuple = (Exception,)):
    """
    Decorator to retry function on exception
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts
        backoff_factor: Multiplier for delay after each attempt
        exceptions: Exceptions to catch and retry
    
    Returns:
        Callable: Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. "
                                  f"Retrying in {current_delay:.1f}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            
            return func(*args, **kwargs)  # Should not reach here
        
        return wrapper
    return decorator


def memoize(ttl: Optional[int] = None, maxsize: int = 128):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds (None = unlimited)
        maxsize: Maximum cache size
    
    Returns:
        Callable: Decorated function
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_keys = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = pickle.dumps((args, frozenset(kwargs.items())))
            
            # Check cache
            if key in cache:
                result, timestamp = cache[key]
                
                # Check TTL
                if ttl is None or (time.time() - timestamp) < ttl:
                    return result
            
            # Call function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache[key] = (result, time.time())
            cache_keys.append(key)
            
            # Enforce maxsize
            if len(cache_keys) > maxsize:
                old_key = cache_keys.pop(0)
                if old_key in cache:
                    del cache[old_key]
            
            return result
        
        return wrapper
    return decorator


# ============================================================================
# Data Serialization Helpers
# ============================================================================

def save_to_json(data: Any, file_path: str, 
                 indent: int = 4, ensure_ascii: bool = False) -> bool:
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        file_path: Path to JSON file
        indent: JSON indentation
        ensure_ascii: Ensure ASCII encoding
    
    Returns:
        bool: True if successful
    """
    try:
        ensure_directory(os.path.dirname(file_path))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        
        logger.debug(f"Saved data to JSON: {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {e}")
        return False


def load_from_json(file_path: str, default: Any = None) -> Any:
    """
    Load data from JSON file
    
    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist
    
    Returns:
        Any: Loaded data or default
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"JSON file not found: {file_path}")
            return default
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.debug(f"Loaded data from JSON: {file_path}")
        return data
    
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {e}")
        return default


def save_to_pickle(data: Any, file_path: str, 
                   compress: bool = False) -> bool:
    """
    Save data to pickle file
    
    Args:
        data: Data to save
        file_path: Path to pickle file
        compress: Use gzip compression
    
    Returns:
        bool: True if successful
    """
    try:
        ensure_directory(os.path.dirname(file_path))
        
        if compress:
            with gzip.open(file_path, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open(file_path, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        logger.debug(f"Saved data to pickle: {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving pickle to {file_path}: {e}")
        return False


def load_from_pickle(file_path: str, 
                     default: Any = None,
                     compress: bool = False) -> Any:
    """
    Load data from pickle file
    
    Args:
        file_path: Path to pickle file
        default: Default value if file doesn't exist
        compress: File is gzip compressed
    
    Returns:
        Any: Loaded data or default
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"Pickle file not found: {file_path}")
            return default
        
        if compress:
            with gzip.open(file_path, 'rb') as f:
                data = pickle.load(f)
        else:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
        
        logger.debug(f"Loaded data from pickle: {file_path}")
        return data
    
    except Exception as e:
        logger.error(f"Error loading pickle from {file_path}: {e}")
        return default


# ============================================================================
# Error Handling Helpers
# ============================================================================

def safe_execute(func: Callable, *args, 
                 default: Any = None,
                 log_error: bool = True,
                 **kwargs) -> Any:
    """
    Execute function safely, catching exceptions
    
    Args:
        func: Function to execute
        default: Default value if exception occurs
        log_error: Log error if exception occurs
        *args: Function arguments
        **kwargs: Function keyword arguments
    
    Returns:
        Any: Function result or default
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.error(f"Error in {func.__name__}: {e}")
        return default


def get_error_details(exception: Exception) -> Dict[str, Any]:
    """
    Get detailed error information
    
    Args:
        exception: Exception object
    
    Returns:
        Dict[str, Any]: Error details
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    return {
        'type': exc_type.__name__ if exc_type else 'Unknown',
        'message': str(exception),
        'traceback': traceback.format_exc(),
        'file': inspect.getfile(inspect.currentframe()) if inspect.currentframe() else 'Unknown',
        'line': inspect.getlineno(inspect.currentframe()) if inspect.currentframe() else 'Unknown',
        'timestamp': datetime.now().isoformat(),
    }


class ErrorContext:
    """Context manager for error handling with custom actions"""
    
    def __init__(self, on_error: Callable = None, 
                 on_success: Callable = None,
                 reraise: bool = True):
        """
        Initialize error context
        
        Args:
            on_error: Function to call on error (receives exception)
            on_success: Function to call on success
            reraise: Re-raise exception after handling
        """
        self.on_error = on_error
        self.on_success = on_success
        self.reraise = reraise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_value is not None:
            # Error occurred
            if self.on_error:
                self.on_error(exc_value)
            
            if self.reraise:
                return False  # Re-raise exception
            else:
                return True   # Suppress exception
        else:
            # No error
            if self.on_success:
                self.on_success()
        
        return False


# ============================================================================
# String and Text Helpers
# ============================================================================

def truncate_text(text: str, max_length: int, 
                 ellipsis: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        ellipsis: Ellipsis string to append
    
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    if max_length <= len(ellipsis):
        return ellipsis[:max_length]
    
    return text[:max_length - len(ellipsis)] + ellipsis


def slugify(text: str) -> str:
    """
    Convert text to URL-safe slug
    
    Args:
        text: Text to slugify
    
    Returns:
        str: Slugified text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace non-alphanumeric characters with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text


def pluralize(count: int, singular: str, 
              plural: Optional[str] = None) -> str:
    """
    Get plural form based on count
    
    Args:
        count: Count
        singular: Singular form
        plural: Plural form (if None, adds 's')
    
    Returns:
        str: Appropriate form
    """
    if count == 1:
        return singular
    
    if plural is None:
        # Simple pluralization
        if singular.endswith('y'):
            return singular[:-1] + 'ies'
        elif singular.endswith('s') or singular.endswith('x') or singular.endswith('z'):
            return singular + 'es'
        else:
            return singular + 's'
    else:
        return plural


def generate_progress_bar(progress: float, 
                         width: int = 20,
                         filled_char: str = '█',
                         empty_char: str = '░') -> str:
    """
    Generate text progress bar
    
    Args:
        progress: Progress (0.0 to 1.0)
        width: Width of progress bar
        filled_char: Character for filled portion
        empty_char: Character for empty portion
    
    Returns:
        str: Progress bar string
    """
    progress = max(0.0, min(1.0, progress))
    filled_width = int(progress * width)
    empty_width = width - filled_width
    
    bar = filled_char * filled_width + empty_char * empty_width
    percentage = f"{progress * 100:.1f}%"
    
    return f"[{bar}] {percentage}"


# ============================================================================
# System Information Helpers
# ============================================================================

def get_system_info() -> Dict[str, Any]:
    """
    Get system information
    
    Returns:
        Dict[str, Any]: System information
    """
    import platform
    import psutil
    
    info = {
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
        },
        'python': {
            'version': platform.python_version(),
            'implementation': platform.python_implementation(),
            'compiler': platform.python_compiler(),
        },
        'memory': {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent,
        },
        'disk': {
            'total': psutil.disk_usage('/').total,
            'used': psutil.disk_usage('/').used,
            'free': psutil.disk_usage('/').free,
            'percent': psutil.disk_usage('/').percent,
        },
        'cpu': {
            'count': psutil.cpu_count(),
            'percent': psutil.cpu_percent(interval=1),
            'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
        },
        'timestamp': datetime.now().isoformat(),
    }
    
    return info


def get_memory_usage() -> Dict[str, Any]:
    """
    Get current memory usage
    
    Returns:
        Dict[str, Any]: Memory usage information
    """
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    return {
        'rss': process.memory_info().rss,  # Resident Set Size
        'vms': process.memory_info().vms,  # Virtual Memory Size
        'percent': process.memory_percent(),
        'available': psutil.virtual_memory().available,
        'total': psutil.virtual_memory().total,
    }


# ============================================================================
# Data Conversion Helpers
# ============================================================================

def convert_bytes_to_human_readable(bytes_value: int) -> str:
    """
    Convert bytes to human-readable string
    
    Args:
        bytes_value: Bytes value
    
    Returns:
        str: Human-readable string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def convert_dict_keys_to_strings(data: Dict[Any, Any]) -> Dict[str, Any]:
    """
    Convert dictionary keys to strings
    
    Args:
        data: Dictionary with any keys
    
    Returns:
        Dict[str, Any]: Dictionary with string keys
    """
    result = {}
    for key, value in data.items():
        str_key = str(key)
        
        if isinstance(value, dict):
            result[str_key] = convert_dict_keys_to_strings(value)
        elif isinstance(value, list):
            result[str_key] = [
                convert_dict_keys_to_strings(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[str_key] = value
    
    return result


def flatten_dict(nested_dict: Dict[str, Any], 
                 separator: str = '.',
                 prefix: str = '') -> Dict[str, Any]:
    """
    Flatten nested dictionary
    
    Args:
        nested_dict: Nested dictionary
        separator: Separator for nested keys
        prefix: Prefix for keys
    
    Returns:
        Dict[str, Any]: Flattened dictionary
    """
    items = []
    for key, value in nested_dict.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, separator, new_key).items())
        else:
            items.append((new_key, value))
    
    return dict(items)


# ============================================================================
# Application-Specific Helpers
# ============================================================================

def generate_report_filename(report_type: str, 
                            timestamp: Optional[datetime] = None,
                            extension: str = "pdf") -> str:
    """
    Generate standardized report filename
    
    Args:
        report_type: Type of report
        timestamp: Report timestamp (default: current time)
        extension: File extension
    
    Returns:
        str: Generated filename
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    date_str = timestamp.strftime("%Y%m%d")
    time_str = timestamp.strftime("%H%M%S")
    
    filename = f"{report_type}_{date_str}_{time_str}.{extension}"
    return sanitize_filename(filename)


def validate_business_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate business data structure
    
    Args:
        data: Business data to validate
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, error_messages)
    """
    errors = []
    
    # Check required fields for sales data
    if 'sales' in data:
        for i, sale in enumerate(data['sales']):
            if 'amount' not in sale:
                errors.append(f"Sale {i}: Missing 'amount' field")
            elif not isinstance(sale['amount'], (int, float, Decimal)):
                errors.append(f"Sale {i}: 'amount' must be numeric")
            elif sale['amount'] < 0:
                errors.append(f"Sale {i}: 'amount' cannot be negative")
    
    # Check required fields for customer data
    if 'customers' in data:
        for i, customer in enumerate(data['customers']):
            if 'email' in customer and not validate_email(customer['email']):
                errors.append(f"Customer {i}: Invalid email format")
    
    return len(errors) == 0, errors


def calculate_business_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate common business metrics
    
    Args:
        data: Business data
    
    Returns:
        Dict[str, Any]: Calculated metrics
    """
    metrics = {}
    
    # Sales metrics
    if 'sales' in data and data['sales']:
        sales = data['sales']
        
        amounts = [sale.get('amount', 0) for sale in sales]
        quantities = [sale.get('quantity', 1) for sale in sales]
        
        metrics['total_sales'] = sum(amounts)
        metrics['average_sale'] = statistics.mean(amounts) if amounts else 0
        metrics['total_units'] = sum(quantities)
        metrics['average_units_per_sale'] = (
            statistics.mean(quantities) if quantities else 0
        )
        
        # Growth metrics (if we have date data)
        dated_sales = [s for s in sales if 'date' in s]
        if len(dated_sales) >= 2:
            dated_sales.sort(key=lambda x: x.get('date', ''))
            first_sales = dated_sales[:len(dated_sales)//2]
            last_sales = dated_sales[len(dated_sales)//2:]
            
            first_total = sum(s.get('amount', 0) for s in first_sales)
            last_total = sum(s.get('amount', 0) for s in last_sales)
            
            if first_total > 0:
                metrics['sales_growth'] = (last_total - first_total) / first_total
    
    # Customer metrics
    if 'customers' in data and data['customers']:
        customers = data['customers']
        
        metrics['total_customers'] = len(customers)
        
        # Segment customers if we have segment data
        segments = {}
        for customer in customers:
            segment = customer.get('segment', 'Unknown')
            segments[segment] = segments.get(segment, 0) + 1
        
        metrics['customer_segments'] = segments
    
    return metrics


# ============================================================================
# Main Execution (Testing)
# ============================================================================

if __name__ == "__main__":
    # Test some helper functions
    print("Testing helper functions...")
    
    # File operations
    test_dir = "test_directory"
    ensure_directory(test_dir)
    print(f"Directory created: {os.path.exists(test_dir)}")
    
    # String operations
    random_str = generate_random_string(10)
    print(f"Random string: {random_str}")
    
    # Date operations
    date_str = "2024-01-15"
    parsed = parse_date(date_str)
    print(f"Parsed date: {parsed}")
    
    # Validation
    test_email = "test@example.com"
    print(f"Valid email '{test_email}': {validate_email(test_email)}")
    
    # Clean up
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print(f"Test directory cleaned up")
    
    print("Helper functions test completed!")