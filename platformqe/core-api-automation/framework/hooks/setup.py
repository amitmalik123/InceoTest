"""
Generic Test Data Setup
=======================

This module provides a generic test data manager that can be used
by any service to set up test data before test execution via API calls.

Usage:
    from framework.hooks import setup_test_data, TestDataManager
    
    # Simple usage with default config
    setup_test_data('parties')
    
    # Advanced usage with custom manager
    manager = TestDataManager('parties')
    manager.setup()
"""

import os
import csv
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from framework.common.logger import get_logger
from framework.loaders.config_loader import get_config
from framework.common.template_utils import render_template
from .config import HooksConfig, get_service_hooks_config

logger = get_logger(__name__)


class TestDataManager:
    """
    Generic manager for setting up test data for any service.
    
    This class handles:
    - Executing prerequisite API calls to create test data
    - Extracting values from API responses
    - Updating CSV files with dynamic values
    """
    
    def __init__(
        self,
        service_name: str,
        environment: Optional[str] = None,
        config: Optional[HooksConfig] = None
    ):
        """
        Initialize the TestDataManager.
        
        Args:
            service_name: Name of the service (e.g., 'parties', 'securities')
            environment: Environment name (defaults to config environment)
            config: Optional HooksConfig, will load default if not provided
        """
        self.service_name = service_name
        self.config = config or get_service_hooks_config(service_name)
        self.app_config = get_config()
        self.environment = environment or self.app_config.get('environment', 'test')
        
        # Initialize API client lazily
        self._api_client = None
        
        # Track created data for cleanup
        self.created_data: List[Dict] = []
        self.original_csv_data: Dict[str, List[Dict]] = {}
        
        logger.info(f"TestDataManager initialized for service: {service_name}")
    
    @property
    def api_client(self):
        """Lazy initialization of API client."""
        if self._api_client is None:
            try:
                from framework.clients.api_client import ApiClientFactory
                self._api_client = ApiClientFactory.get_client(self.service_name)
                logger.info(f"API client created for: {self.service_name}")
            except Exception as e:
                logger.warning(f"Could not create API client: {e}")
        return self._api_client
    
    def setup(self) -> bool:
        """
        Run all setup operations based on configuration.
        
        Returns:
            True if setup completed successfully, False otherwise
        """
        if not self.config.enabled:
            logger.info(f"Hooks disabled for service: {self.service_name}")
            return True
        
        logger.info(f"Starting setup for service: {self.service_name}")
        
        try:
            # Execute prerequisite test case if configured
            prereq = self.config.prerequisite_testcase
            logger.info(f"[DEBUG] prerequisite_testcase config: {prereq}")
            logger.info(f"[DEBUG] prereq exists: {bool(prereq)}, enabled: {prereq.get('enabled') if prereq else 'N/A'}")
            if prereq and prereq.get('enabled'):
                logger.info(f"Executing prerequisite test case")
                result = self._execute_prerequisite_testcase()
            else:
                logger.info(f"No prerequisite test case configured or disabled")
            
            logger.info(f"Setup completed for service: {self.service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Setup failed for service {self.service_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _execute_prerequisite_testcase(self) -> Optional[Dict]:
        """
        Execute a prerequisite test case (e.g., POST to create test data)
        multiple times based on 'count' config and extract values from responses.
        
        Returns:
            Dictionary of extracted values from last execution, or None if failed
        """
        prereq_config = self.config.prerequisite_testcase
        testcase_file = prereq_config.get('testcase_file')
        test_data_file = prereq_config.get('test_data_file')
        count = prereq_config.get('count', 1)  # Number of times to execute
        
        if not testcase_file:
            logger.warning("No prerequisite testcase_file configured")
            return None
        
        logger.info(f"Executing prerequisite test case: {testcase_file} ({count} times)")
        
        # Collect all extracted values
        all_extracted_values = []
        
        for i in range(count):
            logger.info(f"Creating prerequisite data {i+1}/{count}")
            extracted = self._execute_single_prerequisite(prereq_config, testcase_file, test_data_file)
            if extracted:
                all_extracted_values.append(extracted)
        
        if not all_extracted_values:
            logger.error("No prerequisite data was created")
            return None
        
        # Update CSV with all extracted values
        update_csv = prereq_config.get('update_csv_file')
        if update_csv:
            csv_columns = prereq_config.get('csv_columns', ['environment', 'id'])
            self._update_csv_with_values(update_csv, all_extracted_values, csv_columns)
        
        return all_extracted_values[-1]  # Return last extracted values
    
    def _execute_single_prerequisite(
        self,
        prereq_config: Dict,
        testcase_file: str,
        test_data_file: str
    ) -> Optional[Dict]:
        """
        Execute a single prerequisite test case and extract values.
        
        Returns:
            Dictionary of extracted values, or None if failed
        """
        try:
            # Get base paths
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            testdata_path = os.path.join(base_path, 'testdata')
            
            # Load the test case
            testcase_path = os.path.join(testdata_path, testcase_file)
            if not os.path.exists(testcase_path):
                logger.error(f"Test case file not found: {testcase_path}")
                return None
            
            with open(testcase_path, 'r', encoding='utf-8') as f:
                testcases = json.load(f)
            
            # Get first test case (typically TC001 for POST)
            testcase = testcases[0] if isinstance(testcases, list) else testcases
            
            # Load test data from CSV if specified
            context = {'environment': self.environment}
            if test_data_file:
                csv_path = os.path.join(testdata_path, test_data_file)
                if os.path.exists(csv_path):
                    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            # Use first row that matches environment (or any row)
                            if row.get('environment', '').upper() == self.environment.upper() or not row.get('environment'):
                                context.update(row)
                                break
                            context.update(row)
                            break
            
            # Load and render payload
            payload = None
            payload_data = testcase.get('payload')
            logger.debug(f"[HOOKS DEBUG] payload_data type: {type(payload_data)}, value: {payload_data}")
            
            if payload_data:
                if isinstance(payload_data, dict):
                    # Payload is already a dict with template variables
                    logger.debug(f"[HOOKS DEBUG] Payload is a dict, rendering with context")
                    payload_json_str = json.dumps(payload_data)
                    rendered_payload = render_template(payload_json_str, context)
                    payload = json.loads(rendered_payload)
                elif isinstance(payload_data, str):
                    # Payload is a file path
                    logger.debug(f"[HOOKS DEBUG] Payload is a file path: {payload_data}")
                    payload_path = os.path.join(testdata_path, payload_data)
                    if os.path.exists(payload_path):
                        with open(payload_path, 'r', encoding='utf-8') as f:
                            payload_template = f.read()
                        # Render template with context variables
                        rendered_payload = render_template(payload_template, context)
                        payload = json.loads(rendered_payload)
                    else:
                        logger.error(f"Payload file not found: {payload_path}")
                        return None
            
            # Get API endpoint info
            endpoint = testcase.get('endpoint', '')
            method = testcase.get('method', 'POST').upper()
            headers = testcase.get('headers_additional', {})
            
            # Get API client
            if not self.api_client:
                logger.error("No API client available for prerequisite test")
                return None
            
            # Execute the API call
            logger.info(f"Making prerequisite API call: {method} {endpoint}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2) if payload else 'None'}")
            
            # Prepare request kwargs
            request_kwargs = {}
            if payload:
                request_kwargs['json'] = payload
            if headers:
                request_kwargs['headers'] = headers
            
            # Use the generic request method
            response = self.api_client.request(method, endpoint, **request_kwargs)
            
            if not response:
                logger.error("No response from prerequisite API call")
                return None
            
            # Check response status
            expected_status = int(testcase.get('expected_status', 201))
            if response.status_code != expected_status:
                logger.error(f"Prerequisite test failed: Expected {expected_status}, got {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
            
            logger.info(f"Prerequisite API call successful: {response.status_code}")
            
            # Extract values from response
            extracted_values = {}
            response_data = response.json() if response.text else {}
            
            extract_config = prereq_config.get('extract_from_response', {})
            logger.debug(f"[HOOKS DEBUG] extract_config: {extract_config}")
            logger.debug(f"[HOOKS DEBUG] extract_config is truthy: {bool(extract_config)}")
            if extract_config:
                # Support both single field and multiple fields (as dict or list)
                if isinstance(extract_config, dict):
                    # Check if it's a simple field extraction or a fields array
                    if 'fields' in extract_config:
                        # Multiple fields in array format
                        fields_list = extract_config.get('fields', [])
                        for field_config in fields_list:
                            if isinstance(field_config, dict):
                                field = field_config.get('field', '')
                                assign_to = field_config.get('assign_to', field)
                                logger.debug(f"[HOOKS DEBUG] field='{field}', assign_to='{assign_to}'")
                                value = self._extract_value_from_response(response_data, field)
                                if value:
                                    extracted_values[assign_to] = value
                                    logger.info(f"✅ Extracted {assign_to}={value}")
                                    self.created_data.append({
                                        'id': value,
                                        'service': self.service_name,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                else:
                                    logger.warning(f"⚠️ Failed to extract '{field}' from response_data. Available keys: {list(response_data.keys())}")
                    else:
                        # Single field format
                        field = extract_config.get('field', '')
                        assign_to = extract_config.get('assign_to', field)
                        logger.debug(f"[HOOKS DEBUG] field='{field}', assign_to='{assign_to}'")
                        
                        # Handle nested fields (e.g., "data.partyId")
                        value = self._extract_value_from_response(response_data, field)
                        logger.debug(f"[HOOKS DEBUG] _extract_value_from_response returned: {value}")
                        if value:
                            extracted_values[assign_to] = value
                            logger.info(f"✅ Extracted {assign_to}={value}")
                            
                            # Track created data for cleanup
                            self.created_data.append({
                                'id': value,
                                'service': self.service_name,
                                'timestamp': datetime.now().isoformat()
                            })
                        else:
                            logger.warning(f"⚠️ Failed to extract '{field}' from response_data. Available keys: {list(response_data.keys())}")
            else:
                logger.warning(f"⚠️ extract_config is empty or not truthy: {extract_config}")
            
            return extracted_values
            
        except Exception as e:
            logger.error(f"Failed to execute prerequisite test case: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def _extract_value_from_response(self, response_data: Dict, field: str) -> Optional[Any]:
        """
        Extract a value from response data, handling nested fields.
        
        Args:
            response_data: Response JSON data
            field: Field path (e.g., 'partyId' or 'data.partyId' or 'items.0.id')
            
        Returns:
            Extracted value or None
        """
        if not field or not response_data:
            return None
        
        parts = field.split('.')
        value = response_data
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif isinstance(value, list):
                try:
                    idx = int(part)
                    value = value[idx] if idx < len(value) else None
                except ValueError:
                    # Try to find in list items
                    for item in value:
                        if isinstance(item, dict) and part in item:
                            value = item[part]
                            break
                    else:
                        return None
            else:
                return None
            
            if value is None:
                return None
        
        return value
    
    def _update_csv_with_values(
        self,
        csv_file: str,
        all_extracted_values: List[Dict],
        columns: List[str]
    ) -> None:
        """
        Update CSV file with extracted values from prerequisite tests.
        Supports merge mode: preserves existing columns and updates only extracted fields.
        
        Args:
            csv_file: Relative path to CSV file from testdata folder
            all_extracted_values: List of dictionaries with extracted values
            columns: List of column names for the CSV
        """
        testdata_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'testdata'
        )
        csv_path = os.path.join(testdata_path, csv_file)
        
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            
            # Check if file exists for merge mode
            existing_rows = []
            existing_columns = []
            if os.path.exists(csv_path):
                with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    existing_columns = reader.fieldnames if reader.fieldnames else []
                    existing_rows = list(reader)
                
                # Backup original data
                self.original_csv_data[csv_file] = existing_rows
                
                logger.info(f"Merge mode: Updating existing CSV with {len(all_extracted_values)} extracted values")
                
                # Update existing rows with extracted values (one extracted value per row)
                for idx, extracted in enumerate(all_extracted_values):
                    if idx < len(existing_rows):
                        # Update only the extracted columns in this row
                        for key, value in extracted.items():
                            existing_rows[idx][key] = value
                        logger.info(f"Row {idx+1}: Updated {list(extracted.keys())} with values {list(extracted.values())}")
                
                # Use existing columns if file existed, otherwise use provided columns
                final_columns = existing_columns if existing_columns else columns
            else:
                logger.info(f"New mode: Creating new CSV with {len(all_extracted_values)} prerequisite entries")
                
                # Create new rows from extracted values
                existing_rows = []
                for extracted in all_extracted_values:
                    row = {'environment': self.environment}
                    for col in columns:
                        if col != 'environment' and col in extracted:
                            row[col] = extracted[col]
                    existing_rows.append(row)
                
                final_columns = columns
            
            # Write updated CSV with all columns (existing + new)
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=final_columns)
                writer.writeheader()
                writer.writerows(existing_rows)
            
            logger.info(f"Updated {csv_path} with {len(existing_rows)} entries")
            
        except Exception as e:
            logger.error(f"Failed to update CSV {csv_file}: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def restore_csv_files(self) -> None:
        """Restore CSV files to their original state."""
        from .config import restore_csv_file
        
        for csv_file, original_data in self.original_csv_data.items():
            restore_csv_file(csv_file, original_data)
    
    def cleanup(self) -> None:
        """Clean up any resources."""
        logger.info(f"Cleanup completed for: {self.service_name}")


def setup_test_data(
    service_name: str,
    environment: Optional[str] = None,
    config: Optional[HooksConfig] = None
) -> bool:
    """
    Convenience function to run test data setup for a service.
    
    Args:
        service_name: Name of the service
        environment: Optional environment override
        config: Optional custom HooksConfig
        
    Returns:
        True if setup succeeded, False otherwise
    """
    manager = TestDataManager(service_name, environment, config)
    return manager.setup()
