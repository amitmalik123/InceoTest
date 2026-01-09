"""
Parties Test Suite - Pytest Configuration
==========================================

This conftest.py file provides pytest fixtures and hooks specific to the
parties test suite. It uses the generic framework hooks for setup/teardown.

Features:
- Automatic setup of party test data before test session
- Dynamic test data generation and CSV updates
- Automatic teardown after test session
- Service-specific fixtures for parties tests
"""

import pytest
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from framework.common.logger import get_logger
from framework.hooks import setup_test_data, teardown_test_data, TestDataManager, CleanupManager

logger = get_logger(__name__)

# Service name constant
SERVICE_NAME = 'parties'

# Module-level manager for sharing state between setup and teardown
_test_data_manager = None


def pytest_configure(config):
    """
    Called after command line options have been parsed and all plugins loaded.
    Runs parties-specific setup before any tests are collected.
    """
    global _test_data_manager
    
    # Check if we're running parties tests
    testcase_file = config.getoption('--testcase-file', default=None)
    service_name = config.getoption('--service-name', default=None)
    
    # Only run setup for parties tests
    if service_name == SERVICE_NAME or (testcase_file and SERVICE_NAME in testcase_file.lower()):
        logger.info(f"Detected {SERVICE_NAME} test suite - running setup hooks")
        
        try:
            # Get environment from CLI or default
            env = config.getoption('--env', default=None) or os.environ.get('ENV_NAME', 'TSADEV')
            
            # Create and run TestDataManager
            _test_data_manager = TestDataManager(SERVICE_NAME, environment=env)
            success = _test_data_manager.setup()
            
            # Store results for later use
            config._parties_setup_results = {
                'success': success,
                'service': SERVICE_NAME,
                'environment': env
            }
            
            logger.info(f"Setup completed with success={success}")
            
        except Exception as e:
            logger.error(f"Error running {SERVICE_NAME} setup: {e}")


def pytest_unconfigure(config):
    """
    Called before test process is exited.
    Runs parties-specific teardown after all tests complete.
    """
    global _test_data_manager
    
    # Check if we ran parties tests
    if hasattr(config, '_parties_setup_results'):
        logger.info(f"Running {SERVICE_NAME} teardown hooks")
        
        try:
            # Get created data from setup manager
            created_data = _test_data_manager.created_data if _test_data_manager else []
            
            # Run cleanup using CleanupManager
            cleanup = CleanupManager(
                SERVICE_NAME,
                created_data=created_data
            )
            cleanup.teardown()
            
        except Exception as e:
            logger.error(f"Error running {SERVICE_NAME} teardown: {e}")


@pytest.fixture(scope="session")
def parties_setup_results(request):
    """
    Provides access to the parties setup results.
    Can be used by tests to get information about the setup operation.
    """
    return getattr(request.config, '_parties_setup_results', {})


@pytest.fixture(scope="session")
def test_data_manager():
    """
    Provides access to the TestDataManager instance.
    Useful for tests that need to create or query party data.
    """
    global _test_data_manager
    if _test_data_manager is None:
        env = os.environ.get('ENV_NAME', 'TSADEV')
        _test_data_manager = TestDataManager(SERVICE_NAME, environment=env)
    return _test_data_manager


@pytest.fixture(scope="session")
def existing_parties(test_data_manager):
    """
    Provides a list of existing parties queried from the database.
    
    Usage:
        def test_something(existing_parties):
            for party in existing_parties:
                party_id = party['id']
                # use party_id in test
    """
    if not test_data_manager or not test_data_manager.db_client:
        return []
    
    try:
        query = "SELECT Id as id FROM Party WHERE Status = 'Active' ORDER BY CreatedDate DESC LIMIT 10;"
        results = test_data_manager.db_client.execute(query)
        return results or []
    except Exception as e:
        logger.error(f"Failed to query existing parties: {e}")
        return []

