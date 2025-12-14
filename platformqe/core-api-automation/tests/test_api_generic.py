"""
Generic API Test Framework

Refactored test file using modular helper managers for:
- Context management
- Payload handling
- Database operations
- Client management
- Validation orchestration
- Result collection
"""

import pytest
import json
import os
import sys
import time
from framework.common.logger import get_logger
from framework.loaders.api_definitions_loader import ApiDefinitionsLoader
from framework.loaders.testdata_loader import TestDataLoader
from framework.common.template_utils import render_hybrid, render_template
from framework.common.common_functions import extract_value
from framework.reporter.reporter import Reporter
from framework.validators.validators import Validators

# Import helper managers
from framework.test_helpers import (
    get_result_collector,
    get_context_manager,
    get_client_manager,
    get_payload_manager,
    get_db_manager,
    get_validation_manager,
    TestCaseLoader
)

logger = get_logger(__name__)

# Note: pytest_html_results_table_row hook is defined in conftest.py

@pytest.fixture(scope="module")
def api_defs():
    return ApiDefinitionsLoader().load()


@pytest.fixture(scope="module")
def test_cases(request):
    testcase_file = request.config.getoption('--testcase-file')
    if testcase_file:
        with open(testcase_file, 'r') as f:
            return json.load(f)
    # No default file - require explicit testcase file
    pytest.skip("No testcase file specified. Use --testcase-file=<path> to specify a test case file.")
    return []

@pytest.fixture(scope="function")
def test_data(request):
    """Load test data for each test case"""
    case = getattr(request, 'param', None)
    test_data_file = None
    
    if case and isinstance(case, dict):
        test_data_file = case.get('test_data_file')
    
    if test_data_file:
        test_data_path = test_data_file.replace('\\', os.sep).replace('/', os.sep)
        if not os.path.isabs(test_data_path):
            test_data_path = os.path.join('testdata', test_data_path)
        
        if os.path.exists(test_data_path):
            return TestDataLoader(test_data_path).load()
        else:
            return []
    
    # Fallback: load all testdata
    return TestDataLoader().load()

def _resolve_template(value, context):
    """
    Resolve simple {{var}} templates using context.
    Leaves non-template values as-is.
    """
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
        var_name = value[2:-2]
        return context.get(var_name)
    return value


def _apply_custom_assertions(case, context):
    """
    Execute custom assertions defined in case['validate']['assertions'].
    Each assertion supports:
      - actual: value or {{var}}
      - expected: value or {{var}}
      - operator: ==, !=, >, <
      - message: failure message
    """
    validate_cfg = case.get("validate", {}) or {}
    assertions = validate_cfg.get("assertions", []) or []

    for a in assertions:
        actual_raw = a.get("actual")
        expected_raw = a.get("expected")
        operator = a.get("operator", "==")
        message = a.get("message", "Custom assertion failed")

        actual = _resolve_template(actual_raw, context)
        expected = _resolve_template(expected_raw, context)

        # Try to coerce numbers if they look numeric
        def to_number_if_possible(v):
            if isinstance(v, (int, float)):
                return v
            if isinstance(v, str):
                try:
                    # handle ints and floats
                    if "." in v:
                        return float(v)
                    return int(v)
                except Exception:
                    return v
            return v

        actual_val = to_number_if_possible(actual)
        expected_val = to_number_if_possible(expected)

        if operator == "==":
            assert actual_val == expected_val, f"{message}: actual={actual_val}, expected={expected_val}"
        elif operator == "!=":
            assert actual_val != expected_val, f"{message}: actual={actual_val}, expected (different)={expected_val}"
        elif operator == ">":
            assert float(actual_val) > float(expected_val), f"{message}: actual={actual_val} <= expected={expected_val}"
        elif operator == "<":
            assert float(actual_val) < float(expected_val), f"{message}: actual={actual_val} >= expected={expected_val}"
        else:
            raise AssertionError(f"Unsupported operator '{operator}' in custom assertion")

def pytest_generate_tests(metafunc):
    """
    Parametrize tests using TestCaseLoader helper.
    Simplified from 95 lines to ~10 lines by delegating to TestCaseLoader.
    """
    if 'case' in metafunc.fixturenames:
        loader = TestCaseLoader(metafunc.config)
        param_cases = loader.load_and_filter_cases()
        metafunc.parametrize('case', param_cases)


def _handle_testdata_error(case: dict, config: dict):
    """
    Handle test data loading errors by creating failure result.
    
    Args:
        case: Test case with error markers
        config: Configuration dictionary
    
    Raises:
        pytest.fail with error message
    """
    # Try to get actual URL from service_name
    error_url = ""
    service_name = case.get('service_name')
    
    if service_name:
        try:
            from framework.clients.api_client import ApiClientFactory
            temp_client = ApiClientFactory.get_client(service_name)
            error_url = temp_client.base_url if hasattr(temp_client, 'base_url') else ""
        except:
            error_url = config.get('api_base_url', "")
    else:
        error_url = config.get('api_base_url', "")
    
    # Create failure result entry
    result_collector = get_result_collector()
    result_entry = result_collector.create_result_entry(case, error_url)
    result_collector.update_status(result_entry, "FAIL", 
                                   case.get("reason") or case.get("__error_message__", "Test data file error"))
    result_collector.update_validation(result_entry, "FAIL", "PASS", "PASS")
    result_collector.add_result(result_entry)
    
    pytest.fail(result_entry["summary"])


def _log_request_info(case, method, endpoint, payload, json_module):
    """Log request information to console for visibility."""
    print(f"\n{'='*80}\nTest: {case.get('test_name', case.get('test_id'))}\nMethod: {method}\nEndpoint: {endpoint}")
    print(f"Payload: {json_module.dumps(payload, indent=2) if isinstance(payload, dict) and payload else 'None (GET request - no body)'}")
    print(f"{'='*80}\n")


def _log_response_info(response, json_module, logger):
    """Log response information to console and debug log."""
    if logger.level == 10:
        try:
            logger.debug(f"Response JSON: {json_module.dumps(response.json(), indent=2)}")
        except:
            logger.debug(f"Response text: {response.text[:200] if hasattr(response, 'text') else 'N/A'}")
    else:
        print(f"\nResponse Status: {response.status_code}")
        try:
            print(f"Response Body: {json_module.dumps(response.json(), indent=2)}")
        except:
            print(f"Response Body: {response.text[:200] if hasattr(response, 'text') else 'N/A'}...")


def _log_request_info(case, method, endpoint, payload, json_module):
    """Log request information to console for visibility."""
    print(f"\n{'='*80}\nTest: {case.get('test_name', case.get('test_id'))}\nMethod: {method}\nEndpoint: {endpoint}")
    print(f"Payload: {json_module.dumps(payload, indent=2) if isinstance(payload, dict) and payload else 'None (GET request - no body)'}")
    print(f"{'='*80}\n")


def _log_response_info(response, json_module, logger):
    """Log response information to console and debug log."""
    if logger.level == 10:
        try:
            logger.debug(f"Response JSON: {json_module.dumps(response.json(), indent=2)}")
        except:
            logger.debug(f"Response text: {response.text[:200] if hasattr(response, 'text') else 'N/A'}")
    else:
        print(f"\nResponse Status: {response.status_code}")
        try:
            print(f"Response Body: {json_module.dumps(response.json(), indent=2)}")
        except:
            print(f"Response Body: {response.text[:200] if hasattr(response, 'text') else 'N/A'}...")


def test_api_case(case, request):
    """
    Main test function that executes individual API test cases.
    Orchestrates test execution using specialized helper managers for clean separation of concerns.
    
    Args:
        case: Test case dictionary containing test configuration
        request: Pytest request fixture
    """
    import json as json_module
    import time
    logger = get_logger(__name__)
    
    # Skip tests with blank test_id
    if not case.get("test_id"):
        logger.info("Skipping test execution for blank test_id.")
        return
    
    # Handle testdata errors (delegate to helper)
    if case.get("__testdata_error__") or case.get("status") == "FAIL":
        config = request.getfixturevalue('config')
        _handle_testdata_error(case, config)
    
    logger.info(f"--- Test Case: {case.get('test_name', case.get('test_id', 'N/A'))} ---")
    logger.info(f"Test Type: {case.get('test_type', 'N/A')}")
    logger.info(f"Service: {case.get('service_name', 'N/A')}")
    logger.info(f"API Name: {case.get('api_name', 'N/A')}")
    
    # Get helper managers (singletons)
    result_collector = get_result_collector()
    context_manager = get_context_manager()
    client_manager = get_client_manager()
    payload_manager = get_payload_manager()
    db_manager = get_db_manager()
    validation_manager = get_validation_manager()
    
    # Get fixtures
    api_defs = request.getfixturevalue('api_defs')
    test_data = request.getfixturevalue('test_data')
    config = request.getfixturevalue('config')
    
    # Determine protocol
    protocol = case.get('protocol', case.get('method', '')).upper()
    
    # Get client using client_manager (pass case, config, and fallback fixture)
    fallback_client = request.getfixturevalue('client')
    client = client_manager.get_client(case, config, fallback_client)
    
    # Determine actual URL for reporting
    if client and hasattr(client, 'base_url'):
        actual_url = client.base_url
    elif protocol == 'DB_ONLY':
        actual_url = "DB_ONLY (No HTTP URL)"
    else:
        actual_url = config.get('api_base_url', "")
    
    # Store resolved base_url in case for pytest-html report
    case['resolved_base_url'] = actual_url
    
    # Create result entry
    result_entry = result_collector.create_result_entry(case, actual_url)
    
    # ========== PHASE 1: SETUP AND CONTEXT CREATION ==========
    # Create execution context with all variables (includes test_data, api_defs, and global extracted values)
    context = context_manager.create_context(case, test_data, api_defs)
    
    # Debug logging for TC001
    if case.get('test_id') == 'TC001':
        logger.info(f"[DEBUG] Context before payload rendering for TC001: {context}")
    
    # Render endpoint and method with context
    api_name = case.get('api_name', 'UserService')
    api_def = api_defs.get(api_name, {})
    endpoint = render_hybrid(case.get('endpoint', api_def.get('endpoint', '/')), context)
    method = render_hybrid(case.get('method', api_def.get('method', 'GET')), context)
    
    # Render headers_additional with context for data-driven values
    # Headers must remain as strings (HTTP requirement), so convert any rendered values to strings
    if case.get('headers_additional'):
        headers_dict = case.get('headers_additional')
        rendered_headers = {}
        for key, value in headers_dict.items():
            # Render the value with context variables
            if isinstance(value, str):
                rendered_value = render_template(value, context)
            else:
                rendered_value = value
            # Ensure all header values are strings
            rendered_headers[key] = str(rendered_value)
        case['headers_additional'] = rendered_headers
    
    # Log headers/params in DEBUG mode
    if logger.level == 10:
        for param_type in ['query_params', 'path_params', 'headers']:
            if case.get(param_type):
                logger.debug(f"{param_type} for {case.get('test_id')}: {json_module.dumps(case.get(param_type), indent=2)}")
        if case.get('headers_additional'):
            logger.debug(f"headers_additional for {case.get('test_id')}: {json_module.dumps(case.get('headers_additional'), indent=2)}")
    
    # ========== PHASE 2: PAYLOAD LOADING ==========
    try:
        payload = payload_manager.load_payload(case, context, method, test_data)
        if payload and 'extra_param' in case:
            payload = payload_manager.merge_extra_params(payload, case)
    except (FileNotFoundError, IOError) as e:
        result_collector.update_status(result_entry, "FAIL", str(e))
        result_collector.add_result(result_entry)
        pytest.fail(str(e))
    
    # Log payload
    payload_str = json_module.dumps(payload, indent=2) if isinstance(payload, dict) else str(payload) if payload else f"None (method: {method})"
    (logger.debug if logger.level == 10 else logger.info)(f"Request payload: {payload_str}")
    
    # Console output for visibility
    _log_request_info(case, method, endpoint, payload, json_module)
    
    # ========== PHASE 3: DATABASE QUERY (BEFORE API) ==========
    db_result = None
    if db_manager.should_execute_before(case, protocol):
        logger.info("Executing DB query BEFORE API call")
        db_result = db_manager.execute_query(case, context)
        if db_result is not None:
            context['db_result'] = db_result
            # Extract values from db_result if extract_values configured
            extract_config = case.get('extract_values', [])
            if extract_config and isinstance(extract_config, list):
                context_manager.extract_values_batch(extract_config, response=None, db_result=db_result)
        else:
            # DB query was configured but failed to execute
            error_msg = f"Database query failed for {case.get('db_type', 'unknown')} ({case.get('db_connection_name', 'default')})"
            logger.error(error_msg)
            result_collector.update_status(result_entry, "FAIL", error_msg)
            result_collector.add_result(result_entry)
            pytest.fail(error_msg)
    
    # ========== PHASE 4: API REQUEST EXECUTION ==========
    start_time = time.time()
    response, response_time_ms = client_manager.execute_request(
        client, method, endpoint, payload, protocol, case
    )
    end_time = time.time()
    result_entry["response_time"] = int(response_time_ms) if response_time_ms is not None else int((end_time - start_time) * 1000)
    
    # Log response
    _log_response_info(response, json_module, logger)
    
    # ========== PHASE 5: VALUE EXTRACTION (AFTER API) ==========
    extract_config = case.get('extract_values', [])
    if extract_config and isinstance(extract_config, list):
        extracted_vars = context_manager.extract_values_batch(extract_config, response=response, db_result=db_result)
        # Update context with newly extracted variables for use in DB queries
        context.update(extracted_vars)
        # Also update from global variables to ensure all extracted values are available
        context.update(context_manager._global_variables)

     # ========== CUSTOM ASSERTIONS (BASED ON EXTRACTED VALUES) ==========
    # This will use values like models_count, response_filter_id, response_model_id
    _apply_custom_assertions(case, context)
    
    # ========== PHASE 6: DATABASE QUERY (AFTER API) ==========
    if db_manager.should_execute_after(case, protocol):
        logger.info("Executing DB query AFTER API call and value extraction")
        db_result = db_manager.execute_query(case, context)
        if db_result is not None:
            context['db_result'] = db_result
            # Perform DB comparison validation if configured
            validate_cfg = case.get('validate', {})
            data_cmp_cfg = validate_cfg.get('data_comparison', {})
            if data_cmp_cfg:
                # Pass the data_cmp_cfg directly (already extracted from validate_cfg)
                is_valid, errors = db_manager.perform_comparison_validation(response, db_result, validate_cfg, context)
                if not is_valid:
                    result_collector.update_status(result_entry, "FAIL", f"DB comparison validation failed: {errors}")
                    result_collector.update_validation(result_entry, "FAIL", "PASS", "FAIL")
                    result_collector.add_result(result_entry)
                    pytest.fail(f"DB comparison validation failed: {errors}")
                else:
                    result_collector.update_validation(result_entry, None, None, "PASS")
        else:
            # DB query was configured but failed to execute
            error_msg = f"Database query failed for {case.get('db_type', 'unknown')} ({case.get('db_connection_name', 'default')})"
            logger.error(error_msg)
            result_collector.update_status(result_entry, "FAIL", error_msg)
            result_collector.update_validation(result_entry, "FAIL", "PASS", "FAIL")
            result_collector.add_result(result_entry)
            pytest.fail(error_msg)
    
    # ========== PHASE 7: VALIDATION ==========
    # Status code validation
    if protocol != 'DB_ONLY':
        expected_status = int(case.get('expected_status', 200))
        try:
            validation_manager.validate_status_code(response, expected_status)
        except AssertionError as e:
            result_collector.update_status(result_entry, "FAIL", str(e))
            result_collector.add_result(result_entry)
            raise
    result_entry["status"] = "PASS"
    
    # Prepare expected config for validation
    expected = validation_manager.prepare_expected(case, context)
    
    # Field validation using Validators
    validation_errors = validation_manager.validate_response_fields(response, expected, case)
    if validation_errors:
        result_collector.update_status(result_entry, "FAIL", f"Field validation errors: {validation_errors}")
        result_collector.update_validation(result_entry, "FAIL", None, None)
        result_collector.add_result(result_entry)
        assert False, f"Field validation errors: {validation_errors}"
    result_collector.update_validation(result_entry, "PASS", None, None)
    
    # Response match validation
    expected_response = case.get('expected_response')
    if expected_response:
        try:
            ignore_fields = case.get('ignore_fields')
            validation_manager.validate_response_match(response, expected_response, ignore_fields, case)
        except AssertionError as e:
            result_collector.update_status(result_entry, "FAIL", str(e))
            result_collector.add_result(result_entry)
            raise
    
    # Schema validation
    expected_response_schema = case.get('expected_response_schema')
    if expected_response_schema:
        try:
            validation_manager.validate_schema(response, expected_response_schema)
        except (FileNotFoundError, AssertionError) as e:
            result_collector.update_status(result_entry, "FAIL", str(e))
            result_collector.add_result(result_entry)
            raise
    
    # ========== PHASE 8: COLLECT RESULTS ==========
    if result_entry["status"] == "PASS":
        result_entry["summary"] = result_entry.get("summary") or "All checks passed."
        result_collector.add_result(result_entry)


# Note: HTML report generation is now handled by pytest_sessionfinish hook in conftest.py
