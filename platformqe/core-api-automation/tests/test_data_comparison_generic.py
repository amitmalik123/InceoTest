"""
Generic Data Comparison Test Framework
===============================================================================
This framework compares data between MSSQL and PostgreSQL databases using
configuration files (JSON) to define tables, columns, and comparison rules.

Usage:
    pytest -sv tests/test_data_comparison_generic.py --testcase-file <json_file> --env <env>

JSON Configuration Format:
    - test_suite: Name of the test suite
    - description: Description of the comparison
    - source_database: "mssql" or "postgresql"
    - target_database: "mssql" or "postgresql"
    - source_table: Table name in source database
    - target_table: Table name in target database
    - columns_to_compare: Array of column configurations
    - column_mapping: Optional dictionary mapping source columns to target columns
"""

import pytest
import sys
import os
import glob
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import json
import time

# Add framework path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from framework.clients.db_client import DatabaseClientFactory
from framework.loaders.config_loader import ConfigManager
from framework.test_helpers.test_result_collector import get_result_collector


class TestGenericDataComparison:
    """Generic test class for comparing data between databases using JSON configuration"""

    def _get_service_name(self, test_case: Dict[str, Any]) -> str:
        source_file = str(test_case.get('source_file', '')).replace('\\', '/')
        parts = [part for part in source_file.split('/') if part]
        if 'testdata' in parts:
            testdata_index = parts.index('testdata')
            if testdata_index + 1 < len(parts):
                return parts[testdata_index + 1]
        return test_case.get('service_name', 'data_comparison')

    def _build_result_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        source_table = test_case.get('source_table', 'source')
        target_table = test_case.get('target_table', 'target')
        comparison_type = test_case.get('type', 'data_comparison')
        return {
            'test_id': test_case.get('id', test_case.get('name', '')),
            'test_name': test_case.get('name', test_case.get('id', '')),
            'service_name': self._get_service_name(test_case),
            'test_type': [comparison_type],
            'endpoint': f'{source_table} -> {target_table}',
            'method': 'COMPARE',
            'workflow_mode': 'sequential',
            'test_summary': f"{comparison_type} between {source_table} and {target_table}",
            'test_scenario': test_case.get('name', comparison_type)
        }

    def _create_result_entry(self, test_case: Dict[str, Any]):
        result_case = self._build_result_case(test_case)
        result_collector = get_result_collector()
        result_entry = result_collector.create_result_entry(
            result_case,
            f"{test_case.get('source_table', 'source')} -> {test_case.get('target_table', 'target')}",
            protocol='DB_COMPARE'
        )
        result_entry['start_time'] = datetime.now().isoformat()
        return result_collector, result_entry

    def _finalize_result_entry(
        self,
        result_collector,
        result_entry: Dict[str, Any],
        status: str,
        summary: str,
        elapsed_ms: float,
        stats: Optional[Dict[str, Dict[str, int]]] = None,
        details: Optional[Dict[str, List[Tuple[str, str]]]] = None
    ):
        result_entry['end_time'] = datetime.now().isoformat()
        result_collector.update_status(result_entry, status, summary)
        result_collector.update_validation(
            result_entry,
            custom='PASS' if status == 'PASS' else 'FAIL',
            data_comparison='PASS' if status == 'PASS' else 'FAIL'
        )
        result_collector.update_response_time(result_entry, int(elapsed_ms))

        for validator_type, metric in (stats or {}).items():
            result_collector.update_validation_stats(
                result_entry,
                validator_type,
                total=metric.get('total', 0),
                passed=metric.get('passed', 0),
                failed=metric.get('failed', 0)
            )

        for validator_type, validator_details in (details or {}).items():
            for validation_name, validation_status in validator_details:
                result_collector.add_validation_detail(
                    result_entry,
                    validator_type,
                    validation_name,
                    validation_status
                )

        result_collector.add_result(result_entry)

    def _resolve_testcase_files(self, pytest_config) -> List[str]:
        """
        Resolve data comparison testcase JSON files.

        Priority:
        1. Explicit `--testcase-file`
        2. Auto-discover by `--service-name` under testdata/<service>/testcases_database/
        """
        testcase_file = pytest_config.getoption("--testcase-file", None)
        if testcase_file:
            if os.path.exists(testcase_file):
                return [testcase_file]

            normalized = str(testcase_file).replace('\\', '/')
            if '/testcases/' in normalized:
                remapped = normalized.replace('/testcases/', '/testcases_database/', 1)
                remapped_path = remapped.replace('/', os.sep)
                if os.path.exists(remapped_path):
                    print(f"✓ Test case path remapped to new folder: {testcase_file} -> {remapped_path}")
                    return [remapped_path]

            pytest.skip(f"Test case file not found: {testcase_file}")

        service_name = pytest_config.getoption("--service-name", None)
        if service_name:
            pattern = os.path.join(
                'testdata',
                service_name,
                'testcases_database',
                'TestCase_data_comparison*.json'
            )
            matching_files = sorted(glob.glob(pattern))
            if matching_files:
                return matching_files
            pytest.skip(
                f"No data comparison testcase files found for service '{service_name}' matching: {pattern}"
            )

        pytest.skip(
            "No testcase source specified. Use --testcase-file <json_file> or --service-name <service>."
        )

    def _load_test_config(self, pytest_config) -> Dict[str, Any]:
        """
        Load and merge one or more data comparison testcase JSON files.
        """
        testcase_files = self._resolve_testcase_files(pytest_config)

        merged_config: Dict[str, Any] = {
            'test_suite': 'Merged Data Comparison Suite',
            'description': 'Merged data comparison configuration',
            'test_cases': []
        }

        for testcase_file in testcase_files:
            with open(testcase_file, 'r') as file_handle:
                config_data = json.load(file_handle)

            file_test_cases = config_data.get('test_cases', [])
            for test_case in file_test_cases:
                if isinstance(test_case, dict):
                    test_case['source_file'] = testcase_file
                    merged_config['test_cases'].append(test_case)

            if merged_config['test_suite'] == 'Merged Data Comparison Suite' and config_data.get('test_suite'):
                merged_config['test_suite'] = config_data['test_suite']
            if merged_config['description'] == 'Merged data comparison configuration' and config_data.get('description'):
                merged_config['description'] = config_data['description']

        return merged_config
    
    @classmethod
    def setup_class(cls):
        """Setup test class - load configuration and initialize database clients"""
        cls.config_manager = ConfigManager()
        cls.config = cls.config_manager.get_config()
        
        # Database clients will be initialized per test based on JSON config
        cls.db_clients = {}
        
        print("\n" + "="*80)
        print("Generic Data Comparison Test Framework")
        print("="*80)
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after all tests - close all database connections"""
        for client_name, client in cls.db_clients.items():
            try:
                client.close()
                print(f"✓ Closed connection: {client_name}")
            except Exception as e:
                print(f"✗ Error closing {client_name}: {e}")
    
    def get_db_client(self, db_type: str, connection_name: str):
        """
        Get or create a database client
        
        Args:
            db_type: 'mssql' or 'postgresql'
            connection_name: Connection name from config
            
        Returns:
            Database client instance
        """
        client_key = f"{db_type}_{connection_name}"
        
        if client_key not in self.db_clients:
            self.db_clients[client_key] = DatabaseClientFactory.get_client(
                db_type=db_type,
                connection_name=connection_name
            )
        
        return self.db_clients[client_key]
    
    def build_column_mapping(self, test_case: dict) -> dict:
        """
        Build column mapping from JSON test case configuration
        
        Args:
            test_case: Test case configuration dictionary
            
        Returns:
            Dictionary mapping source columns to target columns
        """
        # Check if explicit column_mapping is provided
        if 'column_mapping' in test_case and test_case['column_mapping']:
            return test_case['column_mapping']
        
        # Auto-generate mapping if columns_to_compare is provided
        if 'columns_to_compare' in test_case:
            columns = test_case['columns_to_compare']
            
            # If columns is a list of strings, create identity mapping with snake_case conversion
            if isinstance(columns[0], str):
                mapping = {}
                for col in columns:
                    # Try to convert MSSQL naming to PostgreSQL snake_case
                    target_col = self.convert_to_snake_case(col)
                    mapping[col] = target_col
                return mapping
            
            # If columns is a list of objects with source/target
            elif isinstance(columns[0], dict):
                mapping = {}
                for col_config in columns:
                    source_col = col_config.get('source', col_config.get('name'))
                    target_col = col_config.get('target', source_col)
                    mapping[source_col] = target_col
                return mapping
        
        return {}
    
    def convert_to_snake_case(self, column_name: str) -> str:
        """
        Convert column name to snake_case (simple heuristic)
        
        Examples:
            UserID -> user_id
            FName -> f_name
            SSOGUIDID -> sso_guid_id
        """
        result = []
        for i, char in enumerate(column_name):
            if i > 0 and char.isupper():
                # Add underscore before uppercase letter
                result.append('_')
            result.append(char.lower())
        return ''.join(result)
    
    def compare_records(
        self,
        source_record: dict,
        target_record: dict,
        column_mapping: dict,
        comparison_options: Optional[dict] = None
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Compare two database records field by field
        
        Args:
            source_record: Record from source database
            target_record: Record from target database
            column_mapping: Dictionary mapping source columns to target columns
            comparison_options: Optional comparison settings (trim_whitespace, ignore_case, etc.)
            
        Returns:
            tuple: (match: bool, differences: list)
        """
        if comparison_options is None:
            comparison_options = {}
        
        trim_whitespace = comparison_options.get('trim_whitespace', True)
        ignore_case = comparison_options.get('ignore_case', False)
        handle_boolean_mapping = comparison_options.get('handle_boolean_mapping', True)
        treat_null_strings_as_null = comparison_options.get('treat_null_strings_as_null', True)
        ignore_timezone_in_datetime = comparison_options.get('ignore_timezone_in_datetime', True)
        
        differences = []
        
        for source_column, target_column in column_mapping.items():
            source_value = source_record.get(source_column)
            target_value = target_record.get(target_column)
            
            # Handle NULL string representations (e.g., "[null]", "null", "NULL") as actual NULL
            if treat_null_strings_as_null:
                if isinstance(target_value, str) and target_value.lower() in ['null', '[null]', 'none']:
                    target_value = None
                if isinstance(source_value, str) and source_value.lower() in ['null', '[null]', 'none']:
                    source_value = None
            
            # Handle None/NULL values
            if source_value is None and target_value is None:
                continue
            
            # Handle datetime timezone differences
            if ignore_timezone_in_datetime:
                from datetime import datetime
                if isinstance(source_value, datetime) and isinstance(target_value, datetime):
                    # Normalize both to naive datetime (remove timezone info) for comparison
                    source_naive = source_value.replace(tzinfo=None) if source_value.tzinfo else source_value
                    target_naive = target_value.replace(tzinfo=None) if target_value.tzinfo else target_value
                    if source_naive == target_naive:
                        continue  # Datetimes match when timezone is ignored
            
            # Handle boolean mapping (MSSQL int 0/1 to PostgreSQL bool False/True)
            if handle_boolean_mapping:
                if isinstance(source_value, int) and isinstance(target_value, bool):
                    expected_bool = False if source_value == 0 else True
                    if target_value != expected_bool:
                        differences.append({
                            'column': source_column,
                            'target_column': target_column,
                            'source_value': source_value,
                            'target_value': target_value,
                            'source_type': type(source_value).__name__,
                            'target_type': type(target_value).__name__,
                            'note': f'Boolean mapping check: {source_value} should map to {expected_bool}'
                        })
                    continue  # Values match (0->False or 1->True)
            
            # Convert to string for comparison
            source_str = str(source_value) if source_value is not None else 'NULL'
            target_str = str(target_value) if target_value is not None else 'NULL'
            
            # Apply transformations
            if trim_whitespace:
                source_str = source_str.strip()
                target_str = target_str.strip()
            
            if ignore_case:
                source_str = source_str.lower()
                target_str = target_str.lower()
            
            # Compare values
            if source_str != target_str:
                differences.append({
                    'column': source_column,
                    'target_column': target_column,
                    'source_value': source_value,
                    'target_value': target_value,
                    'source_type': type(source_value).__name__,
                    'target_type': type(target_value).__name__
                })
        
        return len(differences) == 0, differences
    
    def print_comparison_result(
        self,
        identifier: str,
        match: bool,
        differences: List[Dict[str, Any]],
        source_record: Dict[str, Any],
        target_record: Dict[str, Any],
        limit_differences: int = 10
    ):
        """Print detailed comparison results"""
        print("\n" + "="*80)
        print(f"Comparison Result for Record: {identifier}")
        print("="*80)
        
        if match:
            print("✓ SUCCESS: All columns match!")
            print("\nMatching Record:")
            for key, value in list(source_record.items())[:10]:  # Show first 10 columns
                print(f"  {key:20} = {value}")
            if len(source_record) > 10:
                print(f"  ... and {len(source_record) - 10} more columns")
        else:
            print("✗ FAILURE: Mismatches found!")
            print(f"\nTotal Differences: {len(differences)}")
            
            displayed_diffs = differences[:limit_differences]
            print(f"\nShowing first {len(displayed_diffs)} difference(s):")
            print("-" * 80)
            
            for diff in displayed_diffs:
                print(f"\nColumn: {diff['column']} -> {diff.get('target_column', diff['column'])}")
                print(f"  Source:  {diff['source_value']} ({diff['source_type']})")
                print(f"  Target:  {diff['target_value']} ({diff['target_type']})")
                if 'note' in diff:
                    print(f"  Note:    {diff['note']}")
            
            if len(differences) > limit_differences:
                print(f"\n... and {len(differences) - limit_differences} more differences")
        
        print("="*80 + "\n")
    
    def get_test_cases_from_json(self, json_file: Optional[str] = None) -> List[dict]:
        """
        Load test cases from JSON file
        
        Args:
            json_file: Path to JSON test case file
            
        Returns:
            List of test case dictionaries
        """
        if json_file is not None:
            if not os.path.exists(json_file):
                pytest.skip(f"Test case file not found: {json_file}")
            with open(json_file, 'r') as file_handle:
                test_config = json.load(file_handle)
            return test_config.get('test_cases', [])

        pytest.skip(
            "Direct JSON loading without pytest config is not supported. Use the test_config fixture path instead."
        )
    
    @pytest.fixture
    def test_config(self, request):
        """Fixture to provide test configuration from JSON file"""
        return self._load_test_config(request.config)
    
    def test_compare_single_record(self, test_config):
        """
        Generic test to compare single record based on JSON configuration
        Looks for test case with type='data_comparison_single'
        """
        test_cases = [tc for tc in test_config.get('test_cases', []) 
                     if tc.get('type') == 'data_comparison_single' and tc.get('enabled', True)]
        
        if not test_cases:
            pytest.skip("No single record comparison test case found in JSON")
        
        for test_case in test_cases:
            self._execute_single_record_comparison(test_case)
    
    def _execute_single_record_comparison(self, test_case: dict):
        """Execute single record comparison based on test case configuration"""
        print(f"\n{'='*80}")
        print(f"TEST: {test_case.get('name', 'Single Record Comparison')}")
        print(f"{'='*80}")
        execution_start = time.perf_counter()
        
        # Get database clients
        source_db_type = test_case.get('source_database', 'mssql')
        target_db_type = test_case.get('target_database', 'postgresql')
        source_conn = test_case.get('source_connection')
        target_conn = test_case.get('target_connection')
        
        # Validate required connection names
        assert source_conn, "source_connection must be specified in test case JSON"
        assert target_conn, "target_connection must be specified in test case JSON"
        
        source_client = self.get_db_client(source_db_type, source_conn)
        target_client = self.get_db_client(target_db_type, target_conn)
        
        # Build column mapping
        column_mapping = self.build_column_mapping(test_case)
        source_columns = list(column_mapping.keys())
        target_columns = list(column_mapping.values())
        
        # Get identifier (userid, id, etc.)
        identifier_field = test_case.get('identifier_field', 'userid')
        identifier_value = test_case.get(identifier_field)
        
        # Find the source column name for the identifier
        # The identifier_field might be lowercase, find matching key in column_mapping
        identifier_source_col = None
        for src_col, tgt_col in column_mapping.items():
            if src_col.lower() == identifier_field.lower() or tgt_col.lower() == identifier_field.lower():
                identifier_source_col = src_col
                break
        
        if not identifier_source_col:
            # Fallback: use first column in mapping
            identifier_source_col = source_columns[0]
        
        # Build queries
        source_table = test_case.get('source_table')
        target_table = test_case.get('target_table')
        result_collector, result_entry = self._create_result_entry(test_case)
        
        source_query = f"""
        SELECT {', '.join(source_columns)}
        FROM {source_table}
        WHERE {identifier_source_col} = '{identifier_value}'
        """
        
        print(f"\nExecuting Source Query ({source_db_type})...")
        print(f"Query: {source_query.strip()}")
        source_results = source_client.query(source_query)

        if len(source_results) == 0:
            elapsed_ms = (time.perf_counter() - execution_start) * 1000
            summary = f"Record '{identifier_value}' not found in source {source_table}"
            self._finalize_result_entry(
                result_collector,
                result_entry,
                'FAIL',
                summary,
                elapsed_ms,
                stats={
                    'db_row_checks': {'total': 1, 'passed': 0, 'failed': 1},
                    'db_missing_source': {'total': 1, 'passed': 0, 'failed': 1},
                    'db_missing_target': {'total': 1, 'passed': 1, 'failed': 0},
                    'data_comparisons': {'total': 1, 'passed': 0, 'failed': 1},
                    'assertions': {'total': 1, 'passed': 0, 'failed': 1}
                },
                details={
                    'db_missing_source': [(f"Record {identifier_value}", 'FAIL')],
                    'assertions': [(summary, 'FAIL')]
                }
            )
            pytest.fail(summary)
        print(f"✓ Found {len(source_results)} record(s) in source")
        
        # Get the target identifier column
        identifier_target_col = column_mapping.get(identifier_source_col, identifier_source_col)
        
        target_query = f"""
        SELECT {', '.join(target_columns)}
        FROM {target_table}
        WHERE {identifier_target_col} = '{identifier_value}'
        """
        
        print(f"\nExecuting Target Query ({target_db_type})...")
        print(f"Query: {target_query.strip()}")
        target_results = target_client.query(target_query)

        if len(target_results) == 0:
            elapsed_ms = (time.perf_counter() - execution_start) * 1000
            summary = f"Record '{identifier_value}' not found in target {target_table}"
            self._finalize_result_entry(
                result_collector,
                result_entry,
                'FAIL',
                summary,
                elapsed_ms,
                stats={
                    'db_row_checks': {'total': 1, 'passed': 0, 'failed': 1},
                    'db_missing_source': {'total': 1, 'passed': 1, 'failed': 0},
                    'db_missing_target': {'total': 1, 'passed': 0, 'failed': 1},
                    'data_comparisons': {'total': 1, 'passed': 0, 'failed': 1},
                    'assertions': {'total': 1, 'passed': 0, 'failed': 1}
                },
                details={
                    'db_missing_target': [(f"Record {identifier_value}", 'FAIL')],
                    'assertions': [(summary, 'FAIL')]
                }
            )
            pytest.fail(summary)
        print(f"✓ Found {len(target_results)} record(s) in target")
        
        # Compare records
        source_record = source_results[0]
        target_record = target_results[0]
        
        comparison_options = test_case.get('comparison_options', {})
        match, differences = self.compare_records(
            source_record=source_record,
            target_record=target_record,
            column_mapping=column_mapping,
            comparison_options=comparison_options
        )
        
        # Print results
        self.print_comparison_result(identifier_value, match, differences, source_record, target_record)

        total_columns = len(column_mapping)
        failed_columns = len(differences)
        passed_columns = total_columns - failed_columns
        summary = (
            f"Record '{identifier_value}' matched across {total_columns} columns"
            if match else
            f"Data mismatch found for record '{identifier_value}' across {failed_columns} column(s)"
        )
        elapsed_ms = (time.perf_counter() - execution_start) * 1000
        self._finalize_result_entry(
            result_collector,
            result_entry,
            'PASS' if match else 'FAIL',
            summary,
            elapsed_ms,
            stats={
                'db_row_checks': {'total': 1, 'passed': 1 if match else 0, 'failed': 0 if match else 1},
                'db_column_checks': {'total': total_columns, 'passed': passed_columns, 'failed': failed_columns},
                'db_missing_source': {'total': 1, 'passed': 1, 'failed': 0},
                'db_missing_target': {'total': 1, 'passed': 1, 'failed': 0},
                'data_comparisons': {'total': 1, 'passed': 1 if match else 0, 'failed': 0 if match else 1},
                'assertions': {'total': 1, 'passed': 1 if match else 0, 'failed': 0 if match else 1}
            },
            details={
                'db_row_checks': [(f"Record {identifier_value}", 'PASS' if match else 'FAIL')],
                'db_column_checks': [
                    (diff['column'], 'FAIL') for diff in differences
                ] or [(f"{total_columns} mapped columns", 'PASS')],
                'assertions': [(summary, 'PASS' if match else 'FAIL')]
            }
        )

        if not match:
            pytest.fail(summary)
    
    def test_compare_all_records(self, test_config):
        """
        Generic test to compare all records based on JSON configuration
        Looks for test case with type='data_comparison_all'
        """
        test_cases = [tc for tc in test_config.get('test_cases', []) 
                     if tc.get('type') == 'data_comparison_all' and tc.get('enabled', True)]
        
        if not test_cases:
            pytest.skip("No all-records comparison test case found in JSON")
        
        for test_case in test_cases:
            self._execute_sample_comparison(test_case)
    
    def _execute_sample_comparison(self, test_case: dict):
        """Execute batched sample comparison based on test case configuration"""
        print(f"\n{'='*80}")
        print(f"TEST: {test_case.get('name', 'Sample Records Comparison')}")
        print(f"{'='*80}")
        execution_start = time.perf_counter()
        
        # Get database clients
        source_db_type = test_case.get('source_database', 'mssql')
        target_db_type = test_case.get('target_database', 'postgresql')
        source_conn = test_case.get('source_connection')
        target_conn = test_case.get('target_connection')
        
        # Validate required connection names
        assert source_conn, "source_connection must be specified in test case JSON"
        assert target_conn, "target_connection must be specified in test case JSON"
        
        source_client = self.get_db_client(source_db_type, source_conn)
        target_client = self.get_db_client(target_db_type, target_conn)
        
        # Build column mapping
        column_mapping = self.build_column_mapping(test_case)
        source_columns = list(column_mapping.keys())
        target_columns = list(column_mapping.values())
        
        # Get identifier column (usually UserID, ID, etc.)
        identifier_col = test_case.get('identifier_column', source_columns[1] if len(source_columns) > 1 else source_columns[0])
        identifier_col_target = column_mapping.get(identifier_col, identifier_col)
        
        # Get tables
        source_table = test_case.get('source_table')
        target_table = test_case.get('target_table')
        result_collector, result_entry = self._create_result_entry(test_case)
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total_records FROM {source_table}"
        print(f"\nGetting total record count from source...")
        count_results = source_client.query(count_query)
        total_count = count_results[0]['total_records']
        print(f"✓ Total records in source: {total_count}")
        
        # Define batch size
        batch_size = test_case.get('batch_size', 10000)
        total_batches = (total_count + batch_size - 1) // batch_size
        max_batches = test_case.get('max_batches')
        if max_batches:
            total_batches = min(total_batches, max_batches)
            print(f"✓ Processing in {total_batches} batches of {batch_size} records (limited by max_batches={max_batches})")
        else:
            print(f"✓ Processing in {total_batches} batches of {batch_size} records")
        
        all_mismatches = []
        total_compared = 0
        matching_records = 0
        missing_source_count = 0
        missing_target_count = 0
        total_column_checks = 0
        failed_column_checks = 0
        comparison_options = test_case.get('comparison_options', {})
        
        # Process in batches
        for batch_num in range(total_batches):
            offset = batch_num * batch_size
            
            print(f"\n--- Batch {batch_num + 1}/{total_batches} (records {offset + 1} to {min(offset + batch_size, total_count)}) ---")
            
            # Get batch of identifiers
            id_query = f"""
            SELECT {identifier_col}
            FROM {source_table}
            ORDER BY {identifier_col}
            OFFSET {offset} ROWS
            FETCH NEXT {batch_size} ROWS ONLY
            """
            
            id_results = source_client.query(id_query)
            batch_ids = [row[identifier_col] for row in id_results]
            
            if not batch_ids:
                print("  ⚠ No more records to process")
                break
            
            # Query source records for this batch
            escaped_ids = [str(record_id).replace("'", "''") for record_id in batch_ids]
            ids_list = "', '".join(escaped_ids)
            source_batch_query = f"""
            SELECT {', '.join(source_columns)}
            FROM {source_table}
            WHERE {identifier_col} IN ('{ids_list}')
            """
            
            source_batch_results = source_client.query(source_batch_query)
            
            # Query target records for this batch
            target_batch_query = f"""
            SELECT {', '.join(target_columns)}
            FROM {target_table}
            WHERE {identifier_col_target} IN ('{ids_list}')
            """
            
            target_batch_results = target_client.query(target_batch_query)
            
            # Create dictionaries for fast lookup
            source_dict = {row[identifier_col]: row for row in source_batch_results}
            target_dict = {row[identifier_col_target]: row for row in target_batch_results}
            
            # Compare records
            batch_mismatches = []
            for record_id in batch_ids:
                total_compared += 1
                
                if record_id not in source_dict:
                    missing_source_count += 1
                    batch_mismatches.append({
                        'id': record_id,
                        'error': 'Missing in source',
                        'differences': []
                    })
                    continue
                
                if record_id not in target_dict:
                    missing_target_count += 1
                    batch_mismatches.append({
                        'id': record_id,
                        'error': 'Missing in target',
                        'differences': []
                    })
                    continue
                
                match, differences = self.compare_records(
                    source_record=source_dict[record_id],
                    target_record=target_dict[record_id],
                    column_mapping=column_mapping,
                    comparison_options=comparison_options
                )

                total_column_checks += len(column_mapping)
                if not match:
                    failed_column_checks += len(differences)
                    batch_mismatches.append({
                        'id': record_id,
                        'differences': differences
                    })
                else:
                    matching_records += 1
            
            all_mismatches.extend(batch_mismatches)
            print(f"  ✓ Compared {len(batch_ids)} records - {len(batch_mismatches)} mismatches")
        
        # Print summary
        print(f"\n{'='*80}")
        print("COMPARISON SUMMARY")
        print(f"{'='*80}")
        print(f"Total Records Compared: {total_compared}")
        print(f"Total Mismatches Found: {len(all_mismatches)}")
        
        if all_mismatches:
            print(f"\n✗ FAILURE: Found {len(all_mismatches)} mismatches")
            print("\nFirst 10 mismatches:")
            for i, mismatch in enumerate(all_mismatches[:10], 1):
                print(f"\n{i}. Record ID: {mismatch['id']}")
                if 'error' in mismatch:
                    print(f"   Error: {mismatch['error']}")
                else:
                    print(f"   Differences: {len(mismatch['differences'])}")
                    for diff in mismatch['differences'][:3]:
                        print(f"     - {diff['column']}: {diff['source_value']} != {diff['target_value']}")
        else:
            print(f"\n✓ SUCCESS: All {total_compared} records match!")
        
        print(f"{'='*80}\n")

        failed_row_checks = len(all_mismatches)
        passed_row_checks = total_compared - failed_row_checks
        passed_column_checks = total_column_checks - failed_column_checks
        match = failed_row_checks == 0
        summary = (
            f"All {total_compared} sampled records matched across {total_column_checks} column checks"
            if match else
            f"Found {failed_row_checks} row mismatch(es), {failed_column_checks} failed column check(s), "
            f"missing source={missing_source_count}, missing target={missing_target_count}"
        )
        elapsed_ms = (time.perf_counter() - execution_start) * 1000
        detail_items = []
        for mismatch in all_mismatches[:10]:
            if 'error' in mismatch:
                detail_items.append((f"Record {mismatch['id']}: {mismatch['error']}", 'FAIL'))
            else:
                detail_items.append((f"Record {mismatch['id']}: {len(mismatch['differences'])} difference(s)", 'FAIL'))

        self._finalize_result_entry(
            result_collector,
            result_entry,
            'PASS' if match else 'FAIL',
            summary,
            elapsed_ms,
            stats={
                'db_row_checks': {'total': total_compared, 'passed': passed_row_checks, 'failed': failed_row_checks},
                'db_column_checks': {'total': total_column_checks, 'passed': passed_column_checks, 'failed': failed_column_checks},
                'db_missing_source': {'total': total_compared, 'passed': total_compared - missing_source_count, 'failed': missing_source_count},
                'db_missing_target': {'total': total_compared, 'passed': total_compared - missing_target_count, 'failed': missing_target_count},
                'data_comparisons': {'total': total_compared, 'passed': matching_records, 'failed': failed_row_checks},
                'assertions': {'total': 1, 'passed': 1 if match else 0, 'failed': 0 if match else 1}
            },
            details={
                'db_row_checks': [(f"{passed_row_checks}/{total_compared} sampled rows matched", 'PASS' if match else 'FAIL')],
                'db_column_checks': [(f"{failed_column_checks} column mismatch(es)", 'PASS' if failed_column_checks == 0 else 'FAIL')],
                'db_missing_source': [(f"Missing in source: {missing_source_count}", 'PASS' if missing_source_count == 0 else 'FAIL')],
                'db_missing_target': [(f"Missing in target: {missing_target_count}", 'PASS' if missing_target_count == 0 else 'FAIL')],
                'assertions': [(summary, 'PASS' if match else 'FAIL')] + detail_items
            }
        )

        if not match:
            pytest.fail(f"Found {len(all_mismatches)} mismatches. See details above.")
    
    def test_compare_counts(self, test_config):
        """
        Generic test to compare counts between databases based on JSON configuration
        Looks for test case with type='data_count_comparison'
        """
        test_cases = [tc for tc in test_config.get('test_cases', []) 
                     if tc.get('type') == 'data_count_comparison' and tc.get('enabled', True)]
        
        if not test_cases:
            pytest.skip("No count comparison test case found in JSON")
        
        for test_case in test_cases:
            self._execute_count_comparison(test_case)
    
    def _execute_count_comparison(self, test_case: dict):
        """Execute count comparison based on test case configuration"""
        print(f"\n{'='*80}")
        print(f"TEST: {test_case.get('name', 'Count Comparison')}")
        print(f"{'='*80}")
        execution_start = time.perf_counter()
        
        # Get database clients
        source_db_type = test_case.get('source_database', 'mssql')
        target_db_type = test_case.get('target_database', 'postgresql')
        source_conn = test_case.get('source_connection')
        target_conn = test_case.get('target_connection')
        
        # Validate required connection names
        assert source_conn, "source_connection must be specified in test case JSON"
        assert target_conn, "target_connection must be specified in test case JSON"
        
        source_client = self.get_db_client(source_db_type, source_conn)
        target_client = self.get_db_client(target_db_type, target_conn)
        
        # Get tables
        source_table = test_case.get('source_table')
        target_table = test_case.get('target_table')
        result_collector, result_entry = self._create_result_entry(test_case)
        
        # Get counts
        source_count_query = f"SELECT COUNT(*) as total FROM {source_table}"
        target_count_query = f"SELECT COUNT(*) as total FROM {target_table}"
        
        print(f"\nCounting records in source {source_table}...")
        source_result = source_client.query(source_count_query)
        source_count = source_result[0]['total']
        print(f"✓ Source count: {source_count:,}")
        
        print(f"\nCounting records in target {target_table}...")
        target_result = target_client.query(target_count_query)
        target_count = target_result[0]['total']
        print(f"✓ Target count: {target_count:,}")
        
        # Compare counts
        match = source_count == target_count
        
        print(f"\n{'='*80}")
        if match:
            print(f"✓ SUCCESS: Counts match ({source_count:,} = {target_count:,})")
        else:
            difference = abs(source_count - target_count)
            print(f"✗ FAILURE: Count mismatch!")
            print(f"  Source: {source_count:,}")
            print(f"  Target: {target_count:,}")
            print(f"  Difference: {difference:,}")
        print(f"{'='*80}\n")

        difference = abs(source_count - target_count)
        summary = (
            f"Counts match for {source_table} and {target_table}: {source_count:,}"
            if match else
            f"Count mismatch for {source_table} and {target_table}: source={source_count:,}, target={target_count:,}, difference={difference:,}"
        )
        elapsed_ms = (time.perf_counter() - execution_start) * 1000
        self._finalize_result_entry(
            result_collector,
            result_entry,
            'PASS' if match else 'FAIL',
            summary,
            elapsed_ms,
            stats={
                'db_count_checks': {'total': 1, 'passed': 1 if match else 0, 'failed': 0 if match else 1},
                'assertions': {'total': 1, 'passed': 1 if match else 0, 'failed': 0 if match else 1}
            },
            details={
                'db_count_checks': [(f"Source={source_count:,}, Target={target_count:,}, Delta={difference:,}", 'PASS' if match else 'FAIL')],
                'assertions': [(summary, 'PASS' if match else 'FAIL')]
            }
        )

        if not match:
            pytest.fail(f"Count mismatch: source has {source_count:,} records but target has {target_count:,} records")
