"""
Utilities Package

Centralized utilities for test automation framework.
Import commonly used utilities directly from the utils package.

Examples:
    from utils import setup_logger, settings, Assertions, SoftAssertions
    from utils import AutoHealingEngine, get_configured_azure_db
"""

# API utilities
from config.stp.api_endpoints import APIEndpoints
from utils.api_request_utils import APIClient
from utils.api_response_utils import (
    get_values_from_household_api_open_accounts,
    retrieve_all_values_from_response,
    retrieve_boolean_value_from_response,
)

# Assertion utilities
from utils.assertions import Assertions, SoftAssertions, verify_all

# Auto-healing functionality
from utils.auto_healing import AutoHealingEngine

# Database utilities
from utils.database import AzureSQLDatabase, get_configured_azure_db

# Flaky test tracking
from utils.flaky_test_tracker import FlakyTestTracker, get_tracker

# Helpers
from utils.helpers import ensure_directory_exists, generate_test_data, get_timestamp
from utils.lighthouse_runner import LighthouseRunner

# Logger utilities
from utils.logger import setup_logger

# Settings and configuration
from utils.settings import Settings, settings

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
    # Settings
    "Settings",
    "settings",
    # Assertions
    "Assertions",
    "SoftAssertions",
    "verify_all",
    # Auto-healing
    "AutoHealingEngine",
    # Database
    "get_configured_azure_db",
    "AzureSQLDatabase",
    # API
    "APIEndpoints",
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
]
