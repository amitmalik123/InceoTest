"""
Utilities Package

Centralized utilities for test automation framework.
Import commonly used utilities directly from the utils package.

Examples:
    from utils import setup_logger, settings, Assertions, SoftAssertions
    from utils import AutoHealingEngine, get_configured_db
"""

import logging


logger = logging.getLogger(__name__)

try:
    from utils.api_request_utils import APIClient
    from utils.api_response_utils import (
        get_values_from_household_api_open_accounts,
        retrieve_all_values_from_response,
        retrieve_boolean_value_from_response,
    )
except ImportError as exc:
    logger.debug("Optional API utility imports unavailable: %s", exc)
    APIClient = None
    get_values_from_household_api_open_accounts = None
    retrieve_all_values_from_response = None
    retrieve_boolean_value_from_response = None

# Assertion utilities
from utils.assertions import Assertions, SoftAssertionError, SoftAssertions, verify_all

# Auto-healing functionality
from utils.auto_healing import AutoHealingEngine

# Database utilities
try:
    from utils.database import SQLDatabase, get_configured_db, get_db_from_vault
except ImportError as exc:
    logger.debug("Optional database utility imports unavailable: %s", exc)
    SQLDatabase = None
    get_configured_db = None
    get_db_from_vault = None

# Flaky test tracking
from utils.flaky_test_tracker import FlakyTestTracker, get_tracker

# Helpers
from utils.helpers import ensure_directory_exists, generate_test_data, get_timestamp
# Logger utilities
from utils.logger import setup_logger

# Outlook email utilities
try:
    from utils.outlook_utils import OutlookClient, OutlookEmail
except ImportError as exc:
    logger.debug("Optional Outlook utility imports unavailable: %s", exc)
    OutlookClient = None
    OutlookEmail = None

# Storage utilities
from utils.storage_utils import (
    CookieManager,
    LocalStorageManager,
    SessionStorageManager,
    StorageState,
)

__all__ = [
    # Logger
    "setup_logger",
    # Assertions
    "Assertions",
    "SoftAssertionError",
    "SoftAssertions",
    "verify_all",
    # Auto-healing
    "AutoHealingEngine",
    # Database
    "get_configured_db",
    "get_db_from_vault",
    "SQLDatabase",
    # API
    "APIClient",
    "get_values_from_household_api_open_accounts",
    "retrieve_all_values_from_response",
    "retrieve_boolean_value_from_response",
    # Flaky tests
    "get_tracker",
    "FlakyTestTracker",
    # Storage
    "LocalStorageManager",
    "SessionStorageManager",
    "CookieManager",
    "StorageState",
    # Helpers
    "get_timestamp",
    "ensure_directory_exists",
    "generate_test_data",
    # Outlook
    "OutlookClient",
    "OutlookEmail",
]
