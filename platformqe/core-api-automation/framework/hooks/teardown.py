"""
Generic Test Data Teardown
==========================

This module provides a generic cleanup manager that can be used
by any service to clean up test data after test execution.

Usage:
    from framework.hooks import teardown_test_data, CleanupManager
    
    # Simple usage
    teardown_test_data('parties')
    
    # Advanced usage with custom manager
    manager = CleanupManager('parties')
    manager.teardown()
"""

import os
import csv
from typing import Dict, List, Optional, Any

from framework.common.logger import get_logger
from framework.loaders.config_loader import get_config
from .config import HooksConfig, get_service_hooks_config

logger = get_logger(__name__)


class CleanupManager:
    """
    Generic manager for cleaning up test data for any service.
    
    This class handles:
    - Deleting data created during test setup via API
    - Restoring original CSV files
    - Clearing caches
    """
    
    def __init__(
        self,
        service_name: str,
        environment: Optional[str] = None,
        config: Optional[HooksConfig] = None,
        created_data: Optional[List[Dict]] = None
    ):
        """
        Initialize the CleanupManager.
        
        Args:
            service_name: Name of the service (e.g., 'parties', 'securities')
            environment: Environment name (defaults to config environment)
            config: Optional HooksConfig, will load default if not provided
            created_data: List of data items created during setup to be cleaned up
        """
        self.service_name = service_name
        self.config = config or get_service_hooks_config(service_name)
        self.app_config = get_config()
        self.environment = environment or self.app_config.get('environment', 'test')
        
        # Data to clean up
        self.created_data = created_data or []
        self.original_csv_data: Dict[str, List[Dict]] = {}
        
        # Initialize API client lazily
        self._api_client = None
        
        logger.info(f"CleanupManager initialized for service: {service_name}")
    
    @property
    def api_client(self):
        """Lazy initialization of API client."""
        if self._api_client is None:
            try:
                from framework.clients.api_client import ApiClientFactory
                self._api_client = ApiClientFactory.get_client(self.service_name)
            except Exception as e:
                logger.warning(f"Could not create API client: {e}")
        return self._api_client
    
    def teardown(self) -> bool:
        """
        Run all teardown operations based on configuration.
        
        Returns:
            True if teardown completed successfully, False otherwise
        """
        if not self.config.enabled:
            logger.info(f"Hooks disabled for service: {self.service_name}")
            return True
        
        logger.info(f"Starting teardown for service: {self.service_name}")
        
        try:
            # Delete data created during tests (if configured)
            if self.created_data:
                self._delete_created_data()
            
            # Restore original CSV files
            if self.original_csv_data:
                self._restore_csv_files()
            
            # Clear caches
            self._clear_cache()
            
            logger.info(f"Teardown completed for service: {self.service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Teardown failed for service {self.service_name}: {e}")
            return False
    
    def _delete_created_data(self) -> None:
        """Delete data that was created during test setup via API."""
        if not self.api_client:
            logger.warning("No API client available, skipping data deletion")
            return
        
        for item in self.created_data:
            try:
                item_id = item.get('id')
                if item_id:
                    logger.info(f"Deleting test data with ID: {item_id}")
                    self.api_client.request('DELETE', f"/{item_id}")
                    logger.info(f"Successfully deleted: {item_id}")
            except Exception as e:
                logger.error(f"Failed to delete data {item.get('id')}: {e}")
    
    def _restore_csv_files(self) -> None:
        """Restore CSV files to their original state."""
        testdata_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'testdata'
        )
        
        for csv_file, original_data in self.original_csv_data.items():
            csv_path = os.path.join(testdata_path, csv_file)
            
            try:
                if original_data:
                    fieldnames = list(original_data[0].keys()) if original_data else []
                    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(original_data)
                    logger.info(f"Restored original data to: {csv_path}")
            except Exception as e:
                logger.error(f"Failed to restore CSV {csv_file}: {e}")
    
    def _clear_cache(self) -> None:
        """Clear any cached data for the service."""
        logger.info(f"Clearing cache for service: {self.service_name}")
        
        # Clear config loader cache if it exists
        try:
            from framework.loaders.config_loader import ConfigManager
            if hasattr(ConfigManager, 'clear_cache'):
                ConfigManager.clear_cache()
        except:
            pass
        
        # Clear test data loader cache if it exists
        try:
            from framework.loaders.testdata_loader import TestDataLoader
            if hasattr(TestDataLoader, 'clear_cache'):
                TestDataLoader.clear_cache()
        except:
            pass
        
        logger.info("Cache cleared")
    
    def cleanup_specific_data(self, data_ids: List[str]) -> None:
        """
        Clean up specific data items by their IDs via API DELETE.
        
        Args:
            data_ids: List of IDs to delete
        """
        if not self.api_client:
            logger.error("No API client available for data cleanup")
            return
        
        for data_id in data_ids:
            try:
                logger.info(f"Deleting data with ID: {data_id}")
                self.api_client.request('DELETE', f"/{data_id}")
                logger.info(f"Successfully deleted: {data_id}")
            except Exception as e:
                logger.error(f"Failed to delete data {data_id}: {e}")


def teardown_test_data(
    service_name: str,
    environment: Optional[str] = None,
    config: Optional[HooksConfig] = None,
    created_data: Optional[List[Dict]] = None
) -> bool:
    """
    Convenience function to run test data teardown for a service.
    
    Args:
        service_name: Name of the service
        environment: Optional environment override
        config: Optional custom HooksConfig
        created_data: Data items created during setup that need cleanup
        
    Returns:
        True if teardown succeeded, False otherwise
    """
    manager = CleanupManager(service_name, environment, config, created_data)
    return manager.teardown()
