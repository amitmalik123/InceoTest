from faker import Faker
import random
import string
import logging
import os
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException, Timeout, HTTPError
from urllib3.util.retry import Retry
from .logger import get_logger

logger = get_logger(__name__)


faker = Faker()

def random_string(length=8):
    """Generate a random string of given length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_int(min_value=1, max_value=1000):
    """Generate a random integer within the specified range."""
    return random.randint(min_value, max_value)
def random_numeric(length=8):
    """Generate a random numeric string of given length."""
    return ''.join(random.choices(string.digits, k=length))

def random_email():
    """Generate a random email address."""
    return faker.email()

def random_firstname():
    """Generate a random first name."""
    return faker.first_name()

def random_lastname():
    """Generate a random last name."""
    return faker.last_name()

def random_date(start_date='-30y', end_date='today', pattern='%Y-%m-%d'):
    """Generate a random date string between start_date and end_date."""
    return faker.date_between(start_date=start_date, end_date=end_date).strftime(pattern)

def random_float(min_value=0.0, max_value=100.0, decimals=2):
    """Generate a random float within the specified range, rounded to ``decimals`` places."""
    return round(random.uniform(min_value, max_value), decimals)

# Internal counters for alternate() so each unique set of choices keeps its own cycle position.
_alternate_counters: dict = {}

def alternate(*choices):
    """Return one of ``choices`` cyclically.

    Each call with the same set of choices advances to the next option, wrapping
    around at the end. e.g. alternate('A', 'B') yields 'A', 'B', 'A', 'B', ...
    """
    if not choices:
        raise ValueError("alternate() requires at least one choice")
    key = tuple(choices)
    idx = _alternate_counters.get(key, 0)
    _alternate_counters[key] = idx + 1
    return choices[idx % len(choices)]

def get_composite_key(item, key_field):
    """
    Generate composite key from single field or list of fields.
    
    Args:
        item (dict): Data item to extract key from
        key_field (str or list): Single field name or list of field names
    
    Returns:
        Key value (str/int/tuple): Single value or tuple for composite keys
    """
    if isinstance(key_field, list):
        return tuple(item.get(f) for f in key_field)
    return item.get(key_field)

def parse_json_response(response) -> dict:
    """
    Safely parse JSON response with error handling.
    
    Args:
        response: Response object with json() method
    
    Returns:
        Parsed JSON dict or None if parsing failed
    """
    try:
        return response.json()
    except Exception as e:
        logger.warning(f"Failed to parse JSON response: {e}")
        return None


def normalize_path(path_str):
    """
    Normalize path to work cross-platform (Windows and Linux/Unix).
    Converts any path separator (\\, /, or mixed) to the OS-appropriate separator.
    
    Args:
        path_str (str): Path string with any separator format
    
    Returns:
        str: Normalized path with OS-appropriate separators
    
    Examples:
        Windows: 'parties\\payloads\\file.json' -> 'parties\\payloads\\file.json'
        Linux: 'parties\\payloads\\file.json' -> 'parties/payloads/file.json'
        Mixed: 'parties/payloads\\file.json' -> OS-appropriate format
    """
    if not path_str or not isinstance(path_str, str):
        return path_str
    
    # Replace all backslashes and forward slashes with OS separator
    normalized = path_str.replace('\\', os.sep).replace('/', os.sep)
    
    # Use normpath to clean up any redundant separators
    normalized = os.path.normpath(normalized)
    
    return normalized