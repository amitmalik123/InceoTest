"""
Framework Hooks Module
=====================

This module provides generic hooks for test setup and teardown
that can be used by any service. Database connections are automatically
pulled from the main config files (config.yaml, config.TSADEV.yaml, etc.)

Usage:
    from framework.hooks import setup_test_data, teardown_test_data
    from framework.hooks import TestDataManager, CleanupManager
    
    # Simple usage - just call the functions with service name
    # DB connections are auto-detected from config.TSADEV.yaml
    setup_test_data('parties')
    teardown_test_data('parties')
    
    # Advanced usage with managers
    manager = TestDataManager('parties')
    success = manager.setup()
    
    cleanup = CleanupManager('parties', created_data=manager.created_data)
    cleanup.teardown()

"""

from .config import HooksConfig, get_service_hooks_config, load_all_service_configs
from .setup import setup_test_data, TestDataManager
from .teardown import teardown_test_data, CleanupManager

__all__ = [
    # Configuration
    'HooksConfig',
    'get_service_hooks_config',
    'load_all_service_configs',
    
    # Setup functions
    'setup_test_data',
    'TestDataManager',
    
    # Teardown functions
    'teardown_test_data',
    'CleanupManager',
]

