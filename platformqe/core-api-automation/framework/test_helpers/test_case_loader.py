"""
Test Case Loader

Handles testcase file discovery, loading, and filtering for pytest parametrization.
Supports CSV test data expansion for data-driven testing.
"""

import os
import json
import glob
from typing import List, Dict
from framework.common.logger import get_logger
from framework.common.utils import normalize_path
from framework.loaders.testdata_loader import TestDataLoader
from framework.loaders.testcase_loader import TestCaseLoader as BasicTestCaseLoader

logger = get_logger(__name__)


class TestCaseLoader:
    """
    Loads and filters test cases for pytest parametrization.
    Handles file discovery, filtering, and test_data expansion.
    """
    
    def __init__(self, pytest_config):
        """
        Initialize test case loader.
        
        Args:
            pytest_config: Pytest config object with command-line options
        """
        self.config = pytest_config
        logger.debug("TestCaseLoader initialized")
    
    def load_and_filter_cases(self) -> List[Dict]:
        """
        Load testcases, apply filters, expand with test_data.
        This is the main entry point called from pytest_generate_tests.
        
        Returns:
            List of parametrized test case dictionaries
        """
        # Load all test cases
        all_cases = self._load_testcases()
        
        if not all_cases:
            logger.warning("No test cases loaded")
            return []
        
        logger.info(f"Total test cases loaded: {len(all_cases)}")
        
        # Apply filters from CLI
        filtered_cases = self._apply_filters(all_cases)
        
        logger.info(f"Filtered to {len(filtered_cases)} test case(s) after applying filters")
        
        # Expand cases with test_data if specified
        param_cases = self._expand_with_test_data(filtered_cases)
        
        logger.info(f"Final parametrized test cases: {len(param_cases)}")
        
        return param_cases
    
    def _load_testcases(self) -> List[Dict]:
        """
        Load testcases from file or auto-discover.
        
        Returns:
            List of test case dictionaries
        """
        testcase_file = self.config.getoption('--testcase-file')
        
        if testcase_file:
            # Use specified testcase file
            return self._load_from_file(testcase_file)
        else:
            # Auto-discover testcase files
            return self._auto_discover_testcases()
    
    def _load_from_file(self, testcase_file: str) -> List[Dict]:
        """
        Load testcases from specified file using BasicTestCaseLoader.
        
        Args:
            testcase_file: Path to testcase JSON file
        
        Returns:
            List of test case dictionaries
        """
        if not os.path.exists(testcase_file):
            logger.error(f"Testcase file not found: {testcase_file}")
            return []
        
        try:
            # Use BasicTestCaseLoader for file I/O
            basic_loader = BasicTestCaseLoader(testcase_file)
            all_cases = basic_loader.load()
            
            # Filter for test cases with test_type (pytest requirement)
            all_cases = [c for c in all_cases if isinstance(c, dict) and 'test_type' in c]
            
            logger.info(f"Loaded {len(all_cases)} test cases from {testcase_file}")
            return all_cases
            
        except Exception as e:
            logger.error(f"Failed to load testcase file {testcase_file}: {e}")
            return []
    
    def _auto_discover_testcases(self) -> List[Dict]:
        """
        Auto-discover testcase files in testdata directory.
        Uses BasicTestCaseLoader for each file.
        
        Returns:
            List of test case dictionaries from all discovered files
        """
        # Look for testcase JSON files in testdata directory
        testcase_dir = os.path.join('testdata', '*', 'testcases')
        testcase_files = glob.glob(os.path.join(testcase_dir, '*.json'))
        
        if not testcase_files:
            logger.info('No testcase files found in testdata/*/testcases/')
            return []
        
        logger.info(f'Auto-discovered {len(testcase_files)} testcase file(s)')
        
        # Load all discovered testcase files using BasicTestCaseLoader
        all_cases = []
        for tc_file in testcase_files:
            if os.path.exists(tc_file):
                try:
                    # Use BasicTestCaseLoader for file I/O
                    basic_loader = BasicTestCaseLoader(tc_file)
                    file_cases = basic_loader.load()
                    
                    # Filter for test cases with test_type (pytest requirement)
                    file_cases = [c for c in file_cases if isinstance(c, dict) and 'test_type' in c]
                    all_cases.extend(file_cases)
                    
                    logger.debug(f"Loaded {len(file_cases)} test cases from {tc_file}")
                except Exception as e:
                    logger.error(f"Failed to load {tc_file}: {e}")
        
        return all_cases
    
    def _apply_filters(self, cases: List[Dict]) -> List[Dict]:
        """
        Apply CLI filters to test cases.
        
        Args:
            cases: List of test case dictionaries
        
        Returns:
            Filtered list of test case dictionaries
        """
        filtered_cases = [c for c in cases if isinstance(c, dict)]
        
        # Get filters from CLI
        test_type_filter = self.config.getoption("--test-type")
        service_name_filter = self.config.getoption("--service-name")
        test_id_filter = self.config.getoption("--test-id")
        exclude_test_id_filter = self.config.getoption("--exclude-test-id")
        
        # Apply test_type filter
        if test_type_filter:
            filtered_cases = [c for c in filtered_cases if (
                isinstance(c.get('test_type'), list) and test_type_filter in c.get('test_type')
            ) or (
                isinstance(c.get('test_type'), str) and c.get('test_type') == test_type_filter
            )]
            logger.debug(f"After test_type filter: {len(filtered_cases)} cases")
        
        # Apply service_name filter
        if service_name_filter:
            filtered_cases = [c for c in filtered_cases if c.get('service_name') == service_name_filter]
            logger.debug(f"After service_name filter: {len(filtered_cases)} cases")
        
        # Apply test_id filter (supports comma-separated values)
        if test_id_filter:
            # Split by comma and strip whitespace
            test_ids = [tid.strip() for tid in test_id_filter.split(',')]
            filtered_cases = [c for c in filtered_cases if c.get('test_id') in test_ids]
            logger.debug(f"After test_id filter ({test_ids}): {len(filtered_cases)} cases")
        
        # Apply exclude_test_id filter (supports comma-separated values)
        if exclude_test_id_filter:
            # Split by comma and strip whitespace
            exclude_test_ids = [tid.strip() for tid in exclude_test_id_filter.split(',')]
            filtered_cases = [c for c in filtered_cases if c.get('test_id') not in exclude_test_ids]
            logger.debug(f"After exclude_test_id filter (excluded {exclude_test_ids}): {len(filtered_cases)} cases")
        
        return filtered_cases
    
    def _expand_with_test_data(self, cases: List[Dict]) -> List[Dict]:
        """
        Expand test cases with test_data rows if test_data_file is specified.
        Each row becomes a separate parametrized test case.
        
        If csv_row_index is specified, only that row is used.
        Otherwise, all rows are used (default behavior).
        
        Args:
            cases: List of test case dictionaries
        
        Returns:
            List of expanded test case dictionaries
        """
        param_cases = []
        
        for case in cases:
            test_data_file = case.get('test_data_file')
            
            if test_data_file:
                # Load test data and create a test case for each row
                # Normalize path separators for cross-platform compatibility
                test_data_path = normalize_path(test_data_file)
                if not os.path.isabs(test_data_path):
                    test_data_path = os.path.join('testdata', test_data_path)
                
                test_data_rows = TestDataLoader(test_data_path).load()
                
                if isinstance(test_data_rows, list) and test_data_rows:
                    # Check if csv_row_index is specified
                    csv_row_index = case.get('csv_row_index')
                    
                    if csv_row_index is not None:
                        # Use only the specified row
                        if isinstance(csv_row_index, int) and 0 <= csv_row_index < len(test_data_rows):
                            row = test_data_rows[csv_row_index]
                            param_case = case.copy()
                            param_case.update(row)
                            
                            # If loader returned error marker, set fail marker
                            if row.get("__testdata_error__"):
                                param_case["status"] = "FAIL"
                                param_case["reason"] = row.get("__error_message__", "Test data file error")
                            
                            param_cases.append(param_case)
                            logger.debug(f"Used csv_row_index={csv_row_index} for {case.get('test_id')}")
                        else:
                            logger.warning(f"csv_row_index={csv_row_index} out of range for {case.get('test_id')} (rows: {len(test_data_rows)})")
                    else:
                        # Use all rows (default behavior)
                        for row in test_data_rows:
                            param_case = case.copy()
                            param_case.update(row)
                            
                            # If loader returned error marker, set fail marker
                            if row.get("__testdata_error__"):
                                param_case["status"] = "FAIL"
                                param_case["reason"] = row.get("__error_message__", "Test data file error")
                            
                            param_cases.append(param_case)
                        
                        logger.debug(f"Expanded {case.get('test_id')} into {len(test_data_rows)} test cases (no csv_row_index)")
                else:
                    # If no matching rows, skip (don't add to param_cases)
                    logger.debug(f"No test data rows for {case.get('test_id')}, skipping")
            else:
                # Always add cases with no test_data_file
                param_cases.append(case)
        
        return param_cases
