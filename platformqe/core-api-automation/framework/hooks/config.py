"""
Hooks Configuration
===================

This module provides configuration management for test hooks.
It focuses on prerequisite test case execution (e.g., POST to create test data)
before running other tests.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from framework.common.logger import get_logger
from framework.loaders.config_loader import get_config

logger = get_logger(__name__)


@dataclass
class HooksConfig:
    """
    Configuration for service-specific hooks.
    
    This class manages prerequisite test case configuration for services
    that need to create test data before running tests.
    
    Attributes:
        service_name: Name of the service (e.g., 'parties', 'securities')
        enabled: Whether hooks are enabled for this service
        prerequisite_testcase: Config for prerequisite test case execution
    """
    service_name: str
    enabled: bool = True
    
    # Data limits for CSV updates
    max_records: int = 10
    
    # Prerequisite test case to run before other tests
    # Dict with: enabled, count, testcase_file, test_data_file, extract_from_response, update_csv_file, csv_columns
    prerequisite_testcase: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_service_name(cls, service_name: str) -> 'HooksConfig':
        """
        Create HooksConfig for a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            HooksConfig with settings from SERVICE_DEFAULTS
        """
        return cls(
            service_name=service_name,
            enabled=True
        )


SERVICE_DEFAULTS: Dict[str, Dict] = {
    'parties': {
        'max_records': 10,
        # Prerequisite test case to run before other tests
        'prerequisite_testcase': {
            'enabled': True,
            'count': 3,  # Number of party IDs to create
            'testcase_file': 'parties/testcases/TestCase_Party_POST.json',
            'test_data_file': 'parties/data_driven/Data_parties_POST.csv',
            'extract_from_response': {
                'field': 'partyId',  # Field to extract from API response
                'assign_to': 'id'    # Variable name to use
            },
            'update_csv_file': 'parties/data_driven/Data_parties_GET.csv',
            'csv_columns': ['environment', 'id']
        }
    },
    'MoveMoneyAPI': {
        'max_records': 10,
        # Prerequisite test cases for MoveMoneyAPI service
        # Supports multiple endpoints: requests and instructions
        'prerequisite_testcase': {
            # === INSTRUCTIONS ENDPOINT ===
            
                'enabled': True,
                'count': 1,  # Create instructionId and version for GET/PUT/DELETE flow 
                'testcase_file': 'MoveMoneyAPI/testcases/TestCase_instructions_POST.json',
                'test_data_file': 'MoveMoneyAPI/data_driven/Data_instructions_Hook_POST.csv',
                'extract_from_response': {
                    'fields': [
                        {
                            'field': 'instructionId',
                            'assign_to': 'instructionId'
                        },
                        {
                            'field': 'version',
                            'assign_to': 'version'
                        }
                    ]
                },

                'update_csv_file': 'MoveMoneyAPI/data_driven/Data_instructions_instructionId_GET.csv',
                'csv_columns': ['environment', 'instructionId', 'version'],
            }
        
    }
}
 


def get_service_hooks_config(service_name: str) -> HooksConfig:
    """
    Get hooks configuration for a service.
    
    Args:
        service_name: Name of the service
        
    Returns:
        HooksConfig for the service
    """
    # Create config
    hooks_config = HooksConfig.from_service_name(service_name)
    
    # Apply service-specific defaults if available (try exact match first, then lowercase)
    if service_name in SERVICE_DEFAULTS:
        defaults = SERVICE_DEFAULTS[service_name]
        hooks_config.max_records = defaults.get('max_records', 10)
        hooks_config.prerequisite_testcase = defaults.get('prerequisite_testcase', {})
        logger.debug(f"[HOOKS CONFIG] Loaded config for service: {service_name}")
        
        # Log endpoint-specific configurations
        prereq_tc = hooks_config.prerequisite_testcase
        if isinstance(prereq_tc, dict):
            for endpoint_name, endpoint_config in prereq_tc.items():
                if isinstance(endpoint_config, dict) and endpoint_config.get('enabled'):
                    # Extract field names
                    extract_fields = []
                    extract_cfg = endpoint_config.get('extract_from_response', {})
                    if 'fields' in extract_cfg and isinstance(extract_cfg['fields'], list):
                        extract_fields = [f.get('assign_to') for f in extract_cfg['fields']]
                    
                    logger.debug(f"[HOOKS CONFIG] Loaded prerequisite test case for {endpoint_name} endpoint")
                    logger.debug(f"  - Testcase file: {endpoint_config.get('testcase_file')}")
                    logger.debug(f"  - Extract fields: {extract_fields}")
                    logger.debug(f"  - Update CSV: {endpoint_config.get('update_csv_file')}")
    
    return hooks_config


def load_all_service_configs() -> Dict[str, HooksConfig]:
    """
    Load hooks configurations for all services that have testdata folders.
    
    Returns:
        Dictionary mapping service name to HooksConfig
    """
    configs = {}
    testdata_path = os.path.join(os.path.dirname(__file__), '..', '..', 'testdata')
    
    if os.path.exists(testdata_path):
        for item in os.listdir(testdata_path):
            item_path = os.path.join(testdata_path, item)
            if os.path.isdir(item_path) and not item.startswith('_'):
                configs[item] = get_service_hooks_config(item)
    
    return configs


def restore_csv_file(csv_file: str, original_data: List[Dict]) -> bool:
    """
    Restore a CSV file to its original state.
    Shared utility function used by both TestDataManager and CleanupManager.
    
    Args:
        csv_file: Relative path to CSV file from testdata folder
        original_data: List of dictionaries representing original CSV rows
        
    Returns:
        True if successful, False otherwise
    """
    import csv
    
    testdata_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'testdata'
    )
    csv_path = os.path.join(testdata_path, csv_file)
    
    try:
        if original_data:
            fieldnames = list(original_data[0].keys()) if original_data else []
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(original_data)
            logger.info(f"Restored original data to: {csv_path}")
            return True
    except Exception as e:
        logger.error(f"Failed to restore CSV {csv_file}: {e}")
        return False
