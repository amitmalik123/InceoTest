"""
Pytest Configuration and Hooks
===============================
This file contains all pytest configuration, command-line options, fixtures, and hooks.

Sections:
- Command-line options (pytest_addoption)
- Early configuration (pytest_configure)
- pytest-html report customization (title, summary, table)
- Test collection and filtering
- Session lifecycle hooks (sessionstart, sessionfinish)
- Test execution hooks (runtest_makereport)
"""

import pytest
import os
import base64
from pathlib import Path
from framework.common.logger import get_logger
import time
from tabulate import tabulate
from datetime import datetime
from framework.reporter.reporter import Reporter
import yaml
from dotenv import load_dotenv

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _encode_banner_image():
    """Encode the API Test Banner image as base64 for embedding in HTML reports"""
    try:
        banner_path = os.path.join('framework', 'resources', 'APITestBanner.png')
        if os.path.exists(banner_path):
            with open(banner_path, 'rb') as img_file:
                encoded = base64.b64encode(img_file.read()).decode('utf-8')
                return f'data:image/png;base64,{encoded}'
        else:
            get_logger(__name__).warning(f"Banner image not found at: {banner_path}")
            return None
    except Exception as e:
        get_logger(__name__).warning(f"Failed to encode banner image: {e}")
        return None


# ============================================================================
# COMMAND-LINE OPTIONS
# ============================================================================

def pytest_addoption(parser):
    parser.addoption(
        "--custom-report-path",
        action="store",
        default=None,
        help="Custom path for the test report file."
    )
    parser.addoption(
        "--test-type",
        action="store",
        default=None,
        help="Run only test cases with this test_type value."
    )
    parser.addoption(
        "--service-name",
        action="store",
        default=None,
        help="Run only test cases with this service_name value."
    )
    parser.addoption(
        "--test-id",
        action="store",
        default=None,
        help="Run only test cases with this test_id value (comma-separated for multiple IDs)."
    )
    parser.addoption(
        "--exclude-test-id",
        action="store",
        default=None,
        help="Exclude test cases with these test_id values (comma-separated for multiple IDs)."
    )
    parser.addoption(
        "--testcase-file",
        action="store",
        default=None,
        help="Path to a specific test case JSON file."
    )
    parser.addoption(
        "--env",
        action="store",
        default=None,
        help="Environment name (e.g., TSADEV, T10, T11, T12). Overrides ENV_NAME from .env file."
    )


# ============================================================================
# EARLY CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """
    Called early in pytest lifecycle to set environment variables from CLI.
    This ensures --env parameter takes precedence over .env file.
    
    Also auto-fixes UTF-8 BOM in testcase files to prevent collection failures.
    """
    import os
    from framework.common.bom_utils import fix_testcase_file
    
    # Auto-fix UTF-8 BOM in testcase files
    testcase_file = config.getoption('--testcase-file', default=None)
    fix_testcase_file(testcase_file)
    
    env_name = config.getoption("--env")
    if env_name:
        os.environ['ENV_NAME'] = env_name
        logger = get_logger(__name__)
        logger.info(f"ENV_NAME set to '{env_name}' from CLI argument (--env)")
    
    # Configure HTML report with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_dir = Path("reports") / timestamp
    
    # Ensure directory exists before pytest-html tries to write
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Set HTML report path if not already specified
    if not config.getoption("--html", default=None):
        html_report_path = reports_dir / f"pytest_report_{timestamp}.html"
        config.option.htmlpath = str(html_report_path)
    
    logger = get_logger(__name__)
    logger.info('Test session is starting')
    logger.info(f'HTML report will be generated at: {reports_dir}')


# ============================================================================
# PYTEST-HTML REPORT CUSTOMIZATION
# ============================================================================

def pytest_html_report_title(report):
    """Customize the report title"""
    report.title = ""


def pytest_metadata(metadata):
    """Remove metadata section (Environment details) from pytest-html report"""
    # Clear all metadata to hide the Environment section
    metadata.clear()


def pytest_html_results_summary(prefix, summary, postfix, session):
    """Add custom leadership dashboard-style summary with accurate test counts"""
    from html import escape
    from datetime import datetime
    
    # Get accurate test counts from pytest session stats
    terminalreporter = session.config.pluginmanager.get_plugin('terminalreporter')
    
    # Extract counts from terminalreporter stats
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    errors = len(terminalreporter.stats.get('error', []))
    xfailed = len(terminalreporter.stats.get('xfailed', []))
    xpassed = len(terminalreporter.stats.get('xpassed', []))
    
    total = passed + failed + skipped + errors + xfailed + xpassed
    
    if total > 0:
        pass_percent = (passed / total) * 100
        fail_percent = (failed / total) * 100
        skip_percent = (skipped / total) * 100
    else:
        pass_percent = fail_percent = skip_percent = 0
    
    # Get environment and execution time
    env_name = escape(os.environ.get('ENV_NAME', 'N/A'))
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Determine status badge color and text
    if failed == 0 and errors == 0:
        status_badge = '<span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9em;">✓ ALL TESTS PASSED</span>'
        border_color = "#10b981"
    elif pass_percent >= 80:
        status_badge = '<span style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9em;">⚠ SOME FAILURES</span>'
        border_color = "#f59e0b"
    else:
        status_badge = '<span style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9em;">✗ CRITICAL FAILURES</span>'
        border_color = "#ef4444"
    
    # Get banner image as base64
    banner_data = _encode_banner_image()
    banner_html = ''
    if banner_data:
        banner_html = f'''
        <!-- Banner Image -->
        <div style="width: 100%; margin: 0 0 25px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden;">
            <img src="{banner_data}" alt="API Test Automation Banner" style="width: 100%; height: auto; display: block;"/>
        </div>
        '''
    
    # Create professional leadership dashboard-style summary
    custom_summary = f'''
    {banner_html}
    <div style="margin: 25px 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden;">
        <!-- Header Section -->
        <div style="background: rgba(255,255,255,0.95); padding: 20px 30px; border-bottom: 3px solid {border_color};">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h2 style="margin: 0 0 5px 0; color: #1f2937; font-size: 1.8em; font-weight: 700;">
                        📊 Test Execution Dashboard
                    </h2>
                    <p style="margin: 0; color: #6b7280; font-size: 0.95em;">
                        <strong>Environment:</strong> {env_name} | <strong>Executed:</strong> {current_time}
                    </p>
                </div>
                <div style="text-align: right;">
                    {status_badge}
                </div>
            </div>
        </div>
        
        <!-- KPI Cards Section -->
        <div style="background: rgba(255,255,255,0.98); padding: 25px 30px;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px;">
                
                <!-- Total Tests Card -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; box-shadow: 0 4px 15px rgba(102,126,234,0.3); text-align: center;">
                    <div style="color: rgba(255,255,255,0.9); font-size: 0.85em; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Total Tests</div>
                    <div style="color: white; font-size: 2.5em; font-weight: 800; margin: 10px 0;">{total}</div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.9em;">Test Cases</div>
                </div>
                
                <!-- Passed Tests Card -->
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 20px; border-radius: 10px; box-shadow: 0 4px 15px rgba(16,185,129,0.3); text-align: center;">
                    <div style="color: rgba(255,255,255,0.9); font-size: 0.85em; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">✓ Passed</div>
                    <div style="color: white; font-size: 2.5em; font-weight: 800; margin: 10px 0;">{passed}</div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.9em;">{pass_percent:.1f}% Success Rate</div>
                </div>
                
                <!-- Failed Tests Card -->
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); padding: 20px; border-radius: 10px; box-shadow: 0 4px 15px rgba(239,68,68,0.3); text-align: center;">
                    <div style="color: rgba(255,255,255,0.9); font-size: 0.85em; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">✗ Failed</div>
                    <div style="color: white; font-size: 2.5em; font-weight: 800; margin: 10px 0;">{failed}</div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.9em;">{fail_percent:.1f}% Failure Rate</div>
                </div>
                
                <!-- Skipped Tests Card -->
                <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 20px; border-radius: 10px; box-shadow: 0 4px 15px rgba(245,158,11,0.3); text-align: center;">
                    <div style="color: rgba(255,255,255,0.9); font-size: 0.85em; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">⊘ Skipped</div>
                    <div style="color: white; font-size: 2.5em; font-weight: 800; margin: 10px 0;">{skipped}</div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.9em;">{skip_percent:.1f}% Skip Rate</div>
                </div>
                
            </div>
            
            <!-- Success Rate Bar -->
            <div style="margin-top: 20px; padding: 15px; background: #f9fafb; border-radius: 8px; border-left: 4px solid {border_color};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-weight: 700; color: #1f2937; font-size: 1.1em;">Overall Success Rate</span>
                    <span style="font-weight: 800; color: {border_color}; font-size: 1.3em;">{pass_percent:.2f}%</span>
                </div>
                <div style="background: #e5e7eb; border-radius: 10px; height: 20px; overflow: hidden; position: relative;">
                    <div style="background: linear-gradient(90deg, #10b981 0%, #059669 100%); height: 100%; width: {pass_percent}%; border-radius: 10px; transition: width 0.3s ease;"></div>
                    {f'<div style="background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%); height: 100%; width: {fail_percent}%; position: absolute; left: {pass_percent}%; border-radius: 10px;"></div>' if failed > 0 else ''}
                </div>
            </div>
            
        </div>
    </div>
    
    <style>
        /* Hide the default Environment header and Summary header generated by pytest-html */
        #environment-header {{
            display: none !important;
        }}
        .summary__data > h2 {{
            display: none !important;
        }}        
    </style>
    '''
    
    # Replace the default summary with custom dashboard
    prefix.clear()
    prefix.extend([custom_summary])


# pytest-html hooks to add custom columns for test case metadata
def pytest_html_results_table_header(cells):
    """Add custom column headers to pytest-html report"""
    cells.insert(1, '<th>Test ID</th>')
    cells.insert(2, '<th>Service Name</th>')
    cells.insert(3, '<th>Environment</th>')
    cells.insert(4, '<th>Test Type</th>')
    cells.insert(5, '<th>Iteration</th>')
    cells.insert(6, '<th>Method</th>')
    cells.insert(7, '<th>Base URL</th>')
    cells.insert(8, '<th>Endpoint</th>')
    cells.insert(9, '<th>Validations</th>')
    cells.insert(10, '<th>Test Summary</th>')


def pytest_html_results_table_row(report, cells):
    """Add custom column values to pytest-html report"""
    try:
        # Extract metadata from test item
        test_case = getattr(report, 'test_case', {})
        
        test_id = test_case.get('test_id', 'N/A')
        service_name = test_case.get('service_name', 'N/A')
        
        # Get ENV_NAME from environment variable
        import os
        env_name = os.environ.get('ENV_NAME', 'N/A')
        
        test_type = test_case.get('test_type', 'N/A')
        if isinstance(test_type, list):
            test_type = ', '.join(test_type)
        iteration = test_case.get('iteration', 1)
        method = test_case.get('method', 'N/A')
        endpoint = test_case.get('endpoint', 'N/A')
        
        # Get base URL - prefer resolved_base_url (set during test execution)
        base_url = test_case.get('resolved_base_url', test_case.get('base_url', test_case.get('mainURL', 'N/A')))
        
        test_summary = test_case.get('test_summary', 'N/A')
        
        # Format validations from validate field
        validate = test_case.get('validate', {})
        validations_html = '<ul style="text-align:left; margin:5px; padding-left:20px; font-size:0.9em;">'
        validation_count = 0
        
        # Expected status
        if test_case.get('expected_status'):
            validations_html += f'<li><b>Status Code:</b> {test_case.get("expected_status")}</li>'
            validation_count += 1
        
        # Performance validation
        if validate.get('performance', {}).get('max_response_time_ms'):
            max_time = validate['performance']['max_response_time_ms']
            validations_html += f'<li><b>Response Time:</b> &lt; {max_time}ms</li>'
            validation_count += 1
        
        # Security checks
        if validate.get('security', {}).get('checks'):
            checks = validate['security']['checks']
            validations_html += f'<li><b>Security:</b> {", ".join(checks)}</li>'
            validation_count += 1
        
        # Schema validation
        if test_case.get('expected_response_schema'):
            schema = test_case['expected_response_schema'].split('\\')[-1] if '\\' in test_case['expected_response_schema'] else test_case['expected_response_schema']
            validations_html += f'<li><b>Schema:</b> {schema}</li>'
            validation_count += 1
        
        # Data comparison - support both array and single dict format
        data_comp = validate.get('data_comparison')
        if data_comp:
            if isinstance(data_comp, list):
                # Array format - show count of comparisons
                validations_html += f'<li><b>Data Compare:</b> {len(data_comp)} comparison(s)</li>'
                validation_count += 1
            elif isinstance(data_comp, dict) and data_comp.get('source'):
                # Legacy single dict format
                validations_html += f'<li><b>Data Compare:</b> {data_comp.get("source")} vs {data_comp.get("target")}</li>'
                validation_count += 1
        
        validations_html += '</ul>'
        
        if validation_count == 0:
            validations_html = 'N/A'
        
        # Insert custom cells (swapped base_url and endpoint order)
        cells.insert(1, f'<td>{test_id}</td>')
        cells.insert(2, f'<td>{service_name}</td>')
        cells.insert(3, f'<td><b>{env_name}</b></td>')
        cells.insert(4, f'<td>{test_type}</td>')
        cells.insert(5, f'<td>{iteration}</td>')
        cells.insert(6, f'<td><b>{method}</b></td>')
        cells.insert(7, f'<td style="font-size:0.85em;">{base_url}</td>')
        cells.insert(8, f'<td style="font-family:monospace; font-size:0.9em;">{endpoint}</td>')
        cells.insert(9, f'<td style="max-width:300px; overflow:auto;">{validations_html}</td>')
        cells.insert(10, f'<td class="col-summary">{test_summary}</td>')
    except Exception as e:
        # Fallback if metadata not available
        import os
        env_name = os.environ.get('ENV_NAME', 'N/A')
        cells.insert(1, '<td>N/A</td>')
        cells.insert(2, '<td>N/A</td>')
        cells.insert(3, f'<td>{env_name}</td>')
        cells.insert(4, '<td>N/A</td>')
        cells.insert(5, '<td>N/A</td>')
        cells.insert(6, '<td>N/A</td>')
        cells.insert(7, '<td>N/A</td>')
        cells.insert(8, '<td>N/A</td>')
        cells.insert(9, '<td>N/A</td>')
        cells.insert(10, f'<td>Error: {str(e)}</td>')


def _filter_log_content(log_content, outcome):
    """
    Filter log content to show only critical test outcomes and key actions.
    For PASSED tests: Show test info, API calls, and final results only
    For FAILED tests: Show error context with more surrounding lines
    """
    if not log_content:
        return log_content
    
    lines = log_content.split('\n')
    
    # Enhanced keywords to capture request/response details along with outcomes
    if outcome.lower() == 'passed':
        important_keywords = [
            '--- Test Case:',  # Test header
            'Request: GET', 'Request: POST', 'Request: PUT', 'Request: DELETE',  # REST API requests
            'SOAP Request', 'REST Request',  # SOAP/REST request indicators
            'Request URL:', 'Request Headers:', 'Request Body:',  # Request details
            'SOAP Envelope:',  # SOAP request body
            'Response Status:', 'Response: ',  # Response status codes
            'SOAP Response:', 'REST Response:',  # Response indicators
            'Response Body:', 'Response Headers:',  # Response details
            'comparison PASSED', 'validation PASSED',  # Only final validation results
            'Data comparison validation PASSED',
            'Status code validation PASSED',
            'Field validation PASSED',
            'Response match validation PASSED',
            'Schema validation PASSED',
            'Status code 200 matched', 'Status code 201 matched',  # Status validations
            'Validation passed with no errors',
            'Added result for test_id'  # Final result
        ]
        context_lines = 2  # Base context
        # For multi-line blocks (XML, JSON), extend context significantly
        block_context = 20  # Extended context for XML/JSON blocks
    else:
        # For failed tests, show more context and error details
        important_keywords = [
            '--- Test Case:',
            'FAILED', 'ERROR', 'CRITICAL', 'WARNING',
            'Request:', 'Response:',
            'SOAP Request', 'REST Request', 'SOAP Response:', 'REST Response:',
            'Request URL:', 'Request Headers:', 'Request Body:',
            'Response Status:', 'Response Body:', 'Response Headers:',
            'SOAP Envelope:',
            'comparison FAILED', 'validation FAILED',
            'Exception', 'Traceback', 'AssertionError',
            'Mismatch', 'does not match',
            'Status code', 'did not match',
            'Expected', 'Actual',
            'Added result for test_id'
        ]
        context_lines = 5
        block_context = 30  # More context for failed tests
    
    # Keywords that indicate start of multi-line blocks (need more context)
    block_keywords = ['SOAP Envelope:', 'SOAP Response:', 'Request Body:', 'Response Body:']
    
    important_indices = []
    for i, line in enumerate(lines):
        # Check if line contains important keywords
        if any(keyword in line for keyword in important_keywords):
            important_indices.append(i)
    
    if not important_indices:
        # For setup/teardown with no important content, show minimal
        if len(lines) <= 5:
            return log_content
        return '\n'.join(lines[:2] + ['... (log truncated) ...'] + lines[-2:])
    
    # Collect lines around important indices with context
    lines_to_keep = set()
    for idx in important_indices:
        line = lines[idx]
        # Use extended context for multi-line blocks (XML, JSON payloads)
        if any(block_key in line for block_key in block_keywords):
            start = max(0, idx - context_lines)
            end = min(len(lines), idx + block_context + 1)
        else:
            start = max(0, idx - context_lines)
            end = min(len(lines), idx + context_lines + 1)
        lines_to_keep.update(range(start, end))
    
    # Build filtered content with separation markers
    filtered_lines = []
    sorted_indices = sorted(lines_to_keep)
    
    last_idx = -2
    for idx in sorted_indices:
        if idx > last_idx + 1:
            filtered_lines.append('... (log truncated) ...')
        filtered_lines.append(lines[idx])
        last_idx = idx
    
    return '\n'.join(filtered_lines)


@pytest.fixture(scope="session")
def config(request):
    """
    Centralized config loader using ConfigManager.
    Loads config YAML based on ENV_NAME from .env, CLI argument, or environment variable.
    Falls back to config.yaml if specific config not found.
    """
    from framework.loaders.config_loader import get_config
    load_dotenv()  # Loads .env file if present
    # ENV_NAME is already set in pytest_configure if --env was provided
    return get_config()


@pytest.fixture(scope="function")
def client(config, case=None):
    """
    Enhanced API client fixture that supports multiple API endpoints
    
    Gets the appropriate API client based on:
    1. service_name from test case
    2. api_base_url from config (legacy)
    """
    from framework.clients.api_client import ApiClientFactory, ApiClient
    
    logger = get_logger(__name__)
    
    # Try to get service name from case if available
    service_name = None
    if case and isinstance(case, dict):
        service_name = case.get('service_name')
    
    # If service_name is provided, use the factory to get the client
    if service_name:
        try:
            return ApiClientFactory.get_client(service_name)
        except Exception as e:
            logger.warning(f"Failed to get API client for service '{service_name}': {e}")
            # Fall through to legacy approach
    
    # Legacy approach: use api_base_url from config
    api_base_url = config.get('api_base_url')
    auth_token = config.get('auth_token')
    
    if api_base_url:
        return ApiClient(api_base_url, auth_token)
    
    # If no configuration found, try to get default client from factory
    try:
        return ApiClientFactory.get_client()
    except Exception as e:
        logger.error(f"Failed to create API client: {e}")
        raise


TABLE_HEADER = ["Test Case", "Outcome", "Duration (s)", "Markers", "Parameters", "Phase", "Reason/Error"]
results = []
summary = {"passed": 0, "failed": 0, "skipped": 0, "xfailed": 0, "xpassed": 0}
pytest_results = []

# --- Helper Functions ---
def extract_test_info(item, rep):
    """Extracts test_id and summary from test case param if available."""
    test_id = ''
    summary_txt = ''
    case = item.funcargs.get('case', {})
    if isinstance(case, dict):
        test_id = case.get('test_id', '')
        summary_txt = case.get('test_summary', '') or case.get('summary', '')
    return test_id, summary_txt

def get_markers(item, rep):
    # Prefer item.iter_markers() if available, fallback to rep.keywords
    if hasattr(item, 'iter_markers'):
        return ','.join([m.name for m in item.iter_markers()])
    return ','.join([m.name for m in getattr(rep, 'keywords', {}).values() if hasattr(m, 'name')])

def get_params(rep):
    params = getattr(rep, 'params', None)
    return str(params) if params else ''

def update_summary_and_outcome(rep):
    # Returns outcome string and updates summary dict
    if rep.skipped:
        if hasattr(rep, 'wasxfail') and rep.wasxfail:
            summary["xfailed"] += 1
            return 'XFAILED'
        summary["skipped"] += 1
        return 'SKIPPED'
    elif hasattr(rep, 'wasxfail') and rep.passed:
        summary["xpassed"] += 1
        return 'XPASSED'
    elif rep.failed:
        summary["failed"] += 1
        return 'FAIL'
    elif rep.passed:
        summary["passed"] += 1
        return 'PASS'
    else:
        return rep.outcome.upper()

def get_report_path(config):
    custom_path = config.getoption("custom_report_path")
    if custom_path:
        return custom_path
    # Use absolute path to ensure reports go to project root
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(reports_dir, f"custom_report_{timestamp}.txt")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item):
    logger = get_logger(__name__)
    logger.info(f'Setup for test: {item.name}')
    yield

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item, nextitem):
    yield
    logger = get_logger(__name__)
    logger.info(f'Teardown for test: {item.name}')

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    logger = get_logger(__name__)
    logger.info(f'Running test: {item.name}')
    yield

def pytest_exception_interact(node, call, report):
    # Only log genuine test exceptions, suppress misleading HTML report errors
    if call.excinfo and 'html' not in str(call.excinfo).lower():
        logger = get_logger(__name__)
        logger.error(f'Exception in {node.name}: {call.excinfo}')

def archive_pytest_session_log():
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    archive_dir = os.path.join(reports_dir, 'archive')
    os.makedirs(archive_dir, exist_ok=True)
    session_log = os.path.join(reports_dir, 'pytest_session.log')
    if os.path.exists(session_log):
        import shutil
        shutil.move(session_log, os.path.join(archive_dir, 'pytest_session.log'))


# ============================================================================
# TEST EXECUTION LIFECYCLE HOOKS
# ============================================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    # Attach test case metadata to report object for pytest-html
    if hasattr(item, 'funcargs') and 'case' in item.funcargs:
        rep.test_case = item.funcargs['case']
    elif hasattr(item, 'callspec') and hasattr(item.callspec, 'params') and 'case' in item.callspec.params:
        rep.test_case = item.callspec.params['case']
    else:
        rep.test_case = {}
    
    # Filter captured logs and add expand/collapse button for HTML report
    if hasattr(rep, 'sections'):
        filtered_sections = []
        for section_name, section_content in rep.sections:
            if 'log' in section_name.lower():
                # Filter log content to show only important lines
                filtered_content = _filter_log_content(section_content, rep.outcome)
                # Create collapsible HTML with expand button
                html_log = f"""
                <div style="margin: 10px 0;">
                    <button onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display=='none'?'block':'none'; this.textContent=this.textContent=='+'?'-':'+';"
                            style="background-color: {'#d4edda' if rep.outcome == 'passed' else '#f8d7da'}; 
                                   border: 1px solid {'#c3e6cb' if rep.outcome == 'passed' else '#f5c6cb'}; 
                                   padding: 5px 10px; cursor: pointer; border-radius: 3px;">+</button>
                    <pre style="display: none; margin-top: 5px; padding: 10px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 3px;">{filtered_content}</pre>
                </div>
                """
                filtered_sections.append((section_name, html_log))
            else:
                # Keep non-log sections as-is
                filtered_sections.append((section_name, section_content))
        rep.sections = filtered_sections
    
    # Record all phases (setup, call, teardown) for the custom report
    test_id, summary_txt = extract_test_info(item, rep)
    pytest_results.append({
        'test_id': test_id,
        'summary': summary_txt,
        'outcome': rep.outcome.upper(),
        'duration': f"{getattr(rep, 'duration', 0):.2f}",
        'markers': get_markers(item, rep),
        'phase': rep.when,
        'reason': str(rep.longrepr) if rep.failed else '',
    })
    outcome_str = update_summary_and_outcome(rep)
    row = [
        getattr(item, 'nodeid', ''),
        outcome_str,
        f"{getattr(rep, 'duration', 0):.2f}",
        get_markers(item, rep),
        get_params(rep),
        rep.when,
        str(getattr(rep, 'longreprtext', '')) if rep.failed else ''
    ]
    results.append(row)


# ============================================================================
# SESSION LIFECYCLE AND REPORTING
# ============================================================================

reporter_instance = None

def pytest_sessionstart(session):
    global reporter_instance
    if reporter_instance is None:
        reporter_instance = Reporter()

def pytest_sessionfinish(session, exitstatus):
    global reporter_instance
    # Archive previous pytest_session.log
    archive_pytest_session_log()
    
    # Close all database connections
    try:
        from framework.clients.db_client import DatabaseClientFactory
        DatabaseClientFactory.close_all()
        logger = get_logger(__name__)
        logger.info("All database connections closed successfully")
    except Exception as e:
        logger = get_logger(__name__)
        logger.warning(f"Failed to close database connections: {e}")
    
    # Write all reports at the end of the session (from tests/conftest.py)
    if reporter_instance is None:
        reporter_instance = Reporter()
    reporter_instance.write_custom(pytest_results, timestamped=True)
    reporter_instance.write_json(pytest_results, timestamped=True)
    reporter_instance.write_junit_xml(pytest_results, timestamped=True)
    reporter_instance.write_allure(pytest_results)
    
    # Generate HTML report - convert pytest_results to expected format
    # Collect test results from result collector singleton
    try:
        from framework.test_helpers import get_result_collector
        result_collector = get_result_collector()
        test_results = result_collector.get_results()
        
        # Extract testcases from pytest_results (basic format for HTML report)
        testcases = []
        for result in pytest_results:
            testcases.append({
                'test_id': result.get('test_id', ''),
                'test_name': result.get('test_id', ''),
                'test_summary': result.get('summary', '')
            })
        
        # Write HTML report with collected results
        if test_results:
            reporter_instance.write_html_report(testcases, test_results, timestamped=True)
            logger = get_logger(__name__)
            logger.info(f"HTML report generated with {len(test_results)} test results")
    except Exception as e:
        logger = get_logger(__name__)
        logger.warning(f"Failed to generate HTML report: {e}")
    
    # Push results to InfluxDB (only if enabled in config)
    try:
        from framework.loaders.config_loader import get_config
        config = get_config()
        influxdb_enabled = config.get('db_connections', {}).get('influxdb', {}).get('default', {}).get('enabled', False)
        
        if influxdb_enabled:
            from framework.reporter.influx_reporter import push_to_infux
            logger = get_logger(__name__)
            
            # Extract summary for logging
            summary_info = result_collector.get_summary_stats()
            total = summary_info.get('total', 0)
            passed = summary_info.get('passed', 0)
            failed = summary_info.get('failed', 0)
            skipped = summary_info.get('skipped', 0)
            xfailed = summary_info.get('xfailed', 0)
            xpassed = summary_info.get('xpassed', 0)
            
            logger.info(f"[InfluxDB] Pushing test results | Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped} | XFailed: {xfailed} | XPassed: {xpassed}")
            success = push_to_infux()
            if not success:
                logger.warning("[InfluxDB] Push completed with warnings or no data pushed")
        else:
            logger = get_logger(__name__)
            logger.info("[InfluxDB] Push disabled in configuration. Skipping InfluxDB push.")
    except ImportError:
        logger = get_logger(__name__)
        logger.warning("InfluxDB client not available. Skipping InfluxDB push.")
    except Exception as e:
        logger = get_logger(__name__)
        logger.warning(f"Failed to push results to InfluxDB: {e}")

    # Ensure all log handlers are closed to release file locks (fixes PermissionError on Windows)
    import logging
    logging.shutdown()
    
    # All report writing is now handled by Reporter instance, which writes only to the timestamped directory.
