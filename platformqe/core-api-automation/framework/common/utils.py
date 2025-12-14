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

def random_email():
    """Generate a random email address."""
    return faker.email()

def random_firstname():
    """Generate a random first name."""
    return faker.first_name()

def random_lastname():
    """Generate a random last name."""
    return faker.last_name()

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