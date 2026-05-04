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


def _log_request_info(case, method, endpoint, payload, base_url, json_module):
    """Log request information to console for visibility."""
    print(f"\n{'='*80}\nTest: {case.get('test_name', case.get('test_id'))}\nMethod: {method}\nBase URL: {base_url}\nEndpoint: {endpoint}")
    print(f"Payload: {json_module.dumps(payload, indent=2) if isinstance(payload, dict) and payload else 'None (GET request - no body)'}")
    print(f"{'='*80}\n")


def _log_response_info(response, json_module, logger):
    """Log response information to console only (detailed logging is in api_client/soap_client)."""
    # Only print to console for user visibility, detailed logging happens in client layer
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
    
    # Capture test start time
    from datetime import datetime
    result_entry['start_time'] = datetime.now().isoformat()
    
    # ========== PHASE 1: SETUP AND CONTEXT CREATION ==========
    # Create execution context with all variables (includes test_data, api_defs, and global extracted values)
    context = context_manager.create_context(case, test_data, api_defs)
    
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
    
    # Store api_request in context for data comparison
    # For GET/DELETE requests with no payload, store the data-driven variables from context as api_request
    if payload is None and method.upper() in ['GET', 'DELETE']:
        # Extract data-driven variables (those loaded from test_data_file CSV)
        # These are the variables that were used in the request (endpoint, query params, etc.)
        data_driven_vars = {k: v for k, v in context.items() 
                           if k not in ['test_id', 'service_name', 'workflow_mode', 'test_name', 'protocol', 
                                       'test_type', 'mainURL', 'endpoint', 'method', 'rpc_method', 'graphql_query',
                                       'graphql_variables', 'soap_action', 'soap_envelope', 'headers_additional',
                                       'payload', 'expected_status', 'expected_response_schema', 'expected_response',
                                       'extract_values', 'validate', 'test_data_file', 'db_query', 'db_type',
                                       'db_connection_name', 'test_summary', 'resolved_base_url', 'api_request',
                                       'api_response', 'db_result', 'db_results']}
        context['api_request'] = data_driven_vars
    else:
        context['api_request'] = payload
    
    # Console output for visibility
    _log_request_info(case, method, endpoint, payload, case.get('resolved_base_url', ''), json_module)
    
    # ========== PHASE 3: DATABASE QUERY (BEFORE API) ==========
    db_result = None
    db_results = {}
    if db_manager.should_execute_before(case, protocol):
        logger.info("Executing DB query/queries BEFORE API call")
        db_results = db_manager.execute_queries(case, context)
        
        if db_results:
            # Store results in context
            context['db_results'] = db_results
            logger.debug(f"DB queries executed. Available queries: {list(db_results.keys())}")
            # For backward compatibility, also set db_result to 'default' query result
            db_result = db_results.get('default')
            if db_result is not None:
                context['db_result'] = db_result
            
            # Extract values from db_result(s) if extract_values configured
            extract_config = case.get('extract_values', [])
            if extract_config and isinstance(extract_config, list):
                context_manager.extract_values_batch(extract_config, response=None, db_result=db_result, context=context)
        else:
            # DB query was configured but all queries failed
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

    # Store any DYNAMIC_UUID4-generated header values in context so extract_values
    # can capture them via from: "request_header" (e.g. for AC4/AC5 idempotency replay)
    if hasattr(client, 'last_generated_headers') and client.last_generated_headers:
        context['_last_generated_headers'] = client.last_generated_headers
        logger.debug(f"Stored generated headers in context: {list(client.last_generated_headers.keys())}")

    # ========== PHASE 4.5: SCRIPT EXECUTION (AFTER API, BEFORE VALUE EXTRACTION) ==========
    # Execute custom validator scripts if configured
    scripts = case.get('scripts')
    if scripts:
        logger.info(f"Executing custom script(s): {scripts}")
        config = request.getfixturevalue('config')
        script_result = validation_manager.execute_custom_scripts(
            case=case,
            response=response,
            db_results=db_results,  # Pass full dict with named queries for multi-query support
            extracted_vars=context,
            config=config
        )
        if script_result:
            # Store script_result in context for extract_values to use
            context['script_result'] = script_result
            logger.info(f"Script execution completed. Success: {script_result.get('success', False)}")
            if script_result.get('extracted_values'):
                logger.info(f"  Extracted values from script: {list(script_result['extracted_values'].keys())}")
            # Log script_result as JSON for debugging
            try:
                import json
                logger.info(f"Script execution result (JSON):\n{json.dumps(script_result, indent=2, default=str)}")
            except Exception as e:
                logger.warning(f"Could not serialize script_result to JSON: {e}")
    
    # ========== PHASE 5: VALUE EXTRACTION (AFTER API) ==========
    extract_config = case.get('extract_values', [])
    if extract_config and isinstance(extract_config, list):
        extracted_vars = context_manager.extract_values_batch(extract_config, response=response, db_result=db_result, context=context)
        # Update context with newly extracted variables for use in DB queries
        context.update(extracted_vars)
        # Also update from global variables to ensure all extracted values are available
        context.update(context_manager._global_variables)
    
    # ========== PHASE 6: DATABASE QUERY (AFTER API) ==========
    if db_manager.should_execute_after(case, protocol):
        logger.info("Executing DB query/queries AFTER API call and value extraction")
        db_results = db_manager.execute_queries(case, context)
        
        if db_results:
            # Store results in context
            context['db_results'] = db_results
            logger.info(f"DB queries executed. Available queries: {list(db_results.keys())}")
            # For backward compatibility, also set db_result to 'default' query result
            db_result = db_results.get('default')
            if db_result is not None:
                context['db_result'] = db_result
            
            # Extract values from DB result
            if extract_config and isinstance(extract_config, list):
                db_extracted_vars = context_manager.extract_values_batch(extract_config, response=None, db_result=db_result, context=context)
                context.update(db_extracted_vars)
                context.update(context_manager._global_variables)
                logger.info(f"Extracted {len(db_extracted_vars)} variables from DB result")
            
            # Perform data comparison validation if configured
            validate_cfg = case.get('validate', {})
            data_cmp_cfg = validate_cfg.get('data_comparison')
            if data_cmp_cfg:
                # Get comparison names for details
                comparison_names = []
                if isinstance(data_cmp_cfg, list):
                    # Array format - get comparison_name from each
                    for cmp in data_cmp_cfg:
                        comparison_names.append(cmp.get('comparison_name', 'Data comparison'))
                else:
                    # Single dict format
                    comparison_names.append(data_cmp_cfg.get('comparison_name', 'Data comparison'))
                
                # New approach: pass validate_cfg to support both array and single format
                # The db_manager will handle backward compatibility
                is_valid, errors = db_manager.perform_comparison_validation(response, db_result, validate_cfg, context)
                if not is_valid:
                    result_collector.update_validation_stats(result_entry, "data_comparisons", total=len(comparison_names), passed=0, failed=len(comparison_names))
                    # Add individual comparison details as FAIL
                    for comp_name in comparison_names:
                        result_collector.add_validation_detail(
                            result_entry,
                            "data_comparisons",
                            comp_name,
                            "FAIL"
                        )
                    result_collector.update_status(result_entry, "FAIL", f"Data comparison validation failed: {errors}")
                    result_collector.update_validation(result_entry, None, None, None, "FAIL")
                    result_collector.add_result(result_entry)
                    logger.error(f"[FAIL] Data Comparisons: FAIL (0/{len(comparison_names)})")
                    pytest.fail(f"Data comparison validation failed: {errors}")
                else:
                    result_collector.update_validation_stats(result_entry, "data_comparisons", total=len(comparison_names), passed=len(comparison_names), failed=0)
                    # Add individual comparison details as PASS
                    for comp_name in comparison_names:
                        result_collector.add_validation_detail(
                            result_entry,
                            "data_comparisons",
                            comp_name,
                            "PASS"
                        )
                    result_collector.update_validation(result_entry, None, None, None, "PASS")
                    logger.info(f"[PASS] Data Comparisons: PASS ({len(comparison_names)}/{len(comparison_names)})")
        else:
            # DB query was configured but all queries failed
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
            # Track successful status code validation
            result_collector.update_validation_stats(result_entry, "status_code_checks", total=1, passed=1, failed=0)
            result_entry["status_code"] = expected_status  # Track for dashboard
            logger.info(f"[PASS] Status Code Validation: PASS (Expected: {expected_status}, Got: {response.status_code})")
        except AssertionError as e:
            # Track failed status code validation
            result_collector.update_validation_stats(result_entry, "status_code_checks", total=1, passed=0, failed=1)
            result_entry["status_code"] = expected_status  # Track for dashboard
            result_collector.update_status(result_entry, "FAIL", str(e))
            result_collector.add_result(result_entry)
            logger.error(f"[FAIL] Status Code Validation: FAIL (Expected: {expected_status}, Got: {response.status_code})")
            raise
    result_entry["status"] = "PASS"
    
    # Performance validation
    try:
        validation_manager.validate_performance(result_entry["response_time"], case)
        # Track successful performance validation
        validate_cfg = case.get('validate', {})
        performance_cfg = validate_cfg.get('performance', {})
        if performance_cfg.get('max_response_time_ms'):
            result_collector.update_validation_stats(result_entry, "performance_checks", total=1, passed=1, failed=0)
            result_collector.add_validation_detail(
                result_entry,
                "performance_checks",
                f"Response time <= {performance_cfg.get('max_response_time_ms')}ms",
                "PASS"
            )
    except AssertionError as e:
        # Track failed performance validation
        validate_cfg = case.get('validate', {})
        performance_cfg = validate_cfg.get('performance', {})
        result_collector.update_validation_stats(result_entry, "performance_checks", total=1, passed=0, failed=1)
        result_collector.add_validation_detail(
            result_entry,
            "performance_checks",
            f"Response time <= {performance_cfg.get('max_response_time_ms', 'N/A')}ms",
            "FAIL"
        )
        result_collector.update_status(result_entry, "FAIL", str(e))
        result_collector.add_result(result_entry)
        logger.error(f"[FAIL] Performance Validation: FAIL - {str(e)}")
        raise
    
    # Security validation
    security_check_count = 0
    try:
        # Count security checks in config
        validate_cfg = case.get('validate', {})
        security_cfg = validate_cfg.get('security', {})
        security_checks = security_cfg.get('checks', [])
        security_check_count = len(security_checks) if security_checks else 0
        
        validation_manager.validate_security(response, payload, case)
        
        if security_check_count > 0:
            result_collector.update_validation_stats(result_entry, "security_checks", total=security_check_count, passed=security_check_count, failed=0)
            # Add individual security check details
            for check in security_checks:
                result_collector.add_validation_detail(
                    result_entry,
                    "security_checks",
                    check,
                    "PASS"
                )
            logger.info(f"[PASS] Security Checks: PASS ({security_check_count}/{security_check_count})")
    except AssertionError as e:
        result_collector.update_validation_stats(result_entry, "security_checks", total=security_check_count, passed=0, failed=security_check_count)
        # Add individual security check details as FAIL
        for check in security_checks:
            result_collector.add_validation_detail(
                result_entry,
                "security_checks",
                check,
                "FAIL"
            )
        result_collector.update_status(result_entry, "FAIL", str(e))
        result_collector.update_validation(result_entry, None, "FAIL", None)
        result_collector.add_result(result_entry)
        logger.error(f"[FAIL] Security Checks: FAIL (0/{security_check_count})")
        raise
    
    # Prepare expected config for validation
    expected = validation_manager.prepare_expected(case, context)
    
    # Field validation using Validators
    validation_errors = validation_manager.validate_response_fields(response, expected, case)
    if validation_errors:
        result_collector.update_validation_stats(result_entry, "contract_checks", total=1, passed=0, failed=1)
        result_collector.add_validation_detail(
            result_entry,
            "contract_checks",
            "Response field validation",
            "FAIL"
        )
        result_collector.update_status(result_entry, "FAIL", f"Field validation errors: {validation_errors}")
        result_collector.update_validation(result_entry, "FAIL", None, None)
        result_collector.add_result(result_entry)
        logger.error(f"[FAIL] Contract Check: FAIL (0/1)")
        assert False, f"Field validation errors: {validation_errors}"
    
    result_collector.update_validation_stats(result_entry, "contract_checks", total=1, passed=1, failed=0)
    result_collector.add_validation_detail(
        result_entry,
        "contract_checks",
        "Response field validation",
        "PASS"
    )
    result_collector.update_validation(result_entry, "PASS", None, None)
    logger.info(f"[PASS] Contract Check: PASS (1/1)")
    
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
    
    # Schema validation (SOAP uses XSD validation internally in SOAP client)
    expected_response_schema = case.get('expected_response_schema')
    if expected_response_schema and protocol != 'SOAP' and case.get('method', '').upper() != 'SOAP':
        try:
            validation_manager.validate_schema(response, expected_response_schema)
        except (FileNotFoundError, AssertionError) as e:
            result_collector.update_status(result_entry, "FAIL", str(e))
            result_collector.add_result(result_entry)
            raise
    
    # Note: SOAP validation happens automatically inside SoapClient.call() method
    # No additional validation needed here - follows same pattern as REST/GraphQL/gRPC clients
    
    # Data comparison validation (for non-DB comparisons like api_request vs api_response)
    # This handles comparisons that don't require DB queries
    validate_cfg = case.get('validate', {})
    data_cmp_cfg = validate_cfg.get('data_comparison')
    if data_cmp_cfg and not db_manager.should_execute_after(case, protocol):
        # Only execute here if DB query was not executed after API
        # (to avoid duplicate execution)
        is_valid, errors = db_manager.perform_comparison_validation(response, db_result, validate_cfg, context)
        if not is_valid:
            result_collector.update_validation_stats(result_entry, "data_comparisons", total=1, passed=0, failed=1)
            result_collector.update_status(result_entry, "FAIL", f"Data comparison validation failed: {errors}")
            result_collector.update_validation(result_entry, None, None, None, "FAIL")
            result_collector.add_result(result_entry)
            logger.error(f"[FAIL] Data Comparisons: FAIL (0/1)")
            pytest.fail(f"Data comparison validation failed: {errors}")
        else:
            result_collector.update_validation_stats(result_entry, "data_comparisons", total=1, passed=1, failed=0)
            result_collector.update_validation(result_entry, None, None, None, "PASS")
            logger.info(f"[PASS] Data Comparisons: PASS (1/1)")
    
    # Custom assertions validation
    assertion_stats = {"total": 0, "passed": 0, "failed": 0, "details": []}
    try:
        assertion_stats = validation_manager.validate_assertions(case, context)
        # Update detailed stats in result collector
        result_collector.update_validation_stats(
            result_entry, 
            "assertions",
            total=assertion_stats["total"],
            passed=assertion_stats["passed"],
            failed=assertion_stats["failed"]
        )
        
        # Store individual assertion details for UI display
        if "details" in assertion_stats:
            for detail in assertion_stats["details"]:
                result_collector.add_validation_detail(
                    result_entry,
                    "assertions",
                    detail["message"],
                    detail["status"]
                )
        
        # If assertions exist and pass, update the custom_validations status
        validate_cfg = case.get("validate", {})
        assertions = validate_cfg.get("assertions", [])
        if assertions:
            result_collector.update_validation(result_entry, custom="PASS")
            logger.info(f"[PASS] Assertions: PASS ({assertion_stats['passed']}/{assertion_stats['total']})")
    except AssertionError as e:
        # Get the actual assertion count from test case config
        validate_cfg = case.get("validate", {})
        assertions = validate_cfg.get("assertions", [])
        total_assertions = len(assertions)
        
        # Update stats with actual counts
        if assertion_stats.get("total", 0) == 0:
            assertion_stats["total"] = total_assertions
        assertion_stats["failed"] = assertion_stats["total"] - assertion_stats.get("passed", 0)
        
        result_collector.update_validation_stats(
            result_entry,
            "assertions",
            total=assertion_stats["total"],
            passed=assertion_stats["passed"],
            failed=assertion_stats["failed"]
        )
        result_collector.update_status(result_entry, "FAIL", f"Custom assertion failed: {str(e)}")
        result_collector.update_validation(result_entry, custom="FAIL")
        result_collector.add_result(result_entry)
        logger.error(f"[FAIL] Assertions: FAIL ({assertion_stats['passed']}/{assertion_stats['total']})")
        
        # Show validation summary even on failure
        stats = result_entry.get("validation_stats", {})
        logger.info("\n" + "="*80)
        logger.info("VALIDATION SUMMARY:")
        logger.info("="*80)
        
        # Contract Checks
        contract_stats = stats.get("contract_checks", {"total": 0, "passed": 0, "failed": 0})
        contract_status = result_entry.get("contract_check", "N/A")
        if contract_stats["total"] > 0 or contract_status != "N/A":
            logger.info(f"  Contract Check: {contract_status} ({contract_stats['passed']}/{contract_stats['total']})")
        
        # Security Checks
        security_stats = stats.get("security_checks", {"total": 0, "passed": 0, "failed": 0})
        security_status = result_entry.get("security_checks", "N/A")
        if security_stats["total"] > 0 or security_status != "N/A":
            logger.info(f"  Security Checks: {security_status} ({security_stats['passed']}/{security_stats['total']})")
        
        # Custom Assertions (use local assertion_stats for accurate counts)
        assertion_status = "FAIL"
        if assertion_stats["total"] > 0:
            logger.info(f"  Custom Assertions: {assertion_status} ({assertion_stats['passed']}/{assertion_stats['total']})")
        
        # Data Comparisons
        comparison_stats = stats.get("data_comparisons", {"total": 0, "passed": 0, "failed": 0})
        comparison_status = result_entry.get("data_comparison", "N/A")
        if comparison_stats["total"] > 0 or comparison_status != "N/A":
            logger.info(f"  Data Comparisons: {comparison_status} ({comparison_stats['passed']}/{comparison_stats['total']})")
        
        logger.info("="*80 + "\n")
        
        raise
    
    # ========== PHASE 8: COLLECT RESULTS ==========
    if result_entry["status"] == "PASS":
        result_entry["summary"] = result_entry.get("summary") or "All checks passed."
        
        # Log comprehensive validation statistics
        stats = result_entry.get("validation_stats", {})
        logger.info("\n" + "="*80)
        logger.info("VALIDATION SUMMARY:")
        logger.info("="*80)
        
        # Contract Checks
        contract_stats = stats.get("contract_checks", {"total": 0, "passed": 0, "failed": 0})
        contract_status = result_entry.get("contract_check", "N/A")
        if contract_stats["total"] > 0 or contract_status != "N/A":
            logger.info(f"  Contract Check: {contract_status} ({contract_stats['passed']}/{contract_stats['total']})")
        
        # Security Checks
        security_stats = stats.get("security_checks", {"total": 0, "passed": 0, "failed": 0})
        security_status = result_entry.get("security_checks", "N/A")
        if security_stats["total"] > 0 or security_status != "N/A":
            logger.info(f"  Security Checks: {security_status} ({security_stats['passed']}/{security_stats['total']})")
        
        # Custom Assertions
        assertion_stats_final = stats.get("assertions", {"total": 0, "passed": 0, "failed": 0})
        assertion_status = result_entry.get("custom_validations", "N/A")
        if assertion_stats_final["total"] > 0:
            logger.info(f"  Custom Assertions: {assertion_status} ({assertion_stats_final['passed']}/{assertion_stats_final['total']})")
        
        # Data Comparisons
        comparison_stats = stats.get("data_comparisons", {"total": 0, "passed": 0, "failed": 0})
        comparison_status = result_entry.get("data_comparison", "N/A")
        if comparison_stats["total"] > 0 or comparison_status != "N/A":
            logger.info(f"  Data Comparisons: {comparison_status} ({comparison_stats['passed']}/{comparison_stats['total']})")
        
        logger.info("="*80 + "\n")
        
        # Capture test end time
        result_entry['end_time'] = datetime.now().isoformat()
        result_collector.add_result(result_entry)


# Note: HTML report generation is now handled by pytest_sessionfinish hook in conftest.py
