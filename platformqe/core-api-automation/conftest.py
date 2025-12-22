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
    from framework.test_helpers.test_result_collector import TestResultCollector
    
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
    
    # Collect consolidated validation statistics from all test results
    result_collector = TestResultCollector()
    all_results = result_collector.get_results()
    
    # Initialize consolidated validation counters
    consolidated_validations = {
        'status_code': {'total': 0, 'passed': 0, 'failed': 0},
        'contract': {'total': 0, 'passed': 0, 'failed': 0},
        'security': {'total': 0, 'passed': 0, 'failed': 0},
        'performance': {'total': 0, 'passed': 0, 'failed': 0},
        'data_comparison': {'total': 0, 'passed': 0, 'failed': 0},
        'assertions': {'total': 0, 'passed': 0, 'failed': 0}
    }
    
    # Aggregate validation stats from all results
    for result in all_results:
        # Status code validation (use actual status_code_checks stats if available)
        validation_stats = result.get('validation_stats', {})
        status_code_stats = validation_stats.get('status_code_checks', {})
        
        if status_code_stats.get('total', 0) > 0:
            # Use actual status code validation stats
            consolidated_validations['status_code']['total'] += status_code_stats['total']
            consolidated_validations['status_code']['passed'] += status_code_stats['passed']
            consolidated_validations['status_code']['failed'] += status_code_stats['failed']
        elif result.get('status_code'):
            # Fallback: if status_code exists but no stats, assume it was validated
            consolidated_validations['status_code']['total'] += 1
            # Check if test passed overall as a best guess (only if no other validation failed)
            if result.get('status') == 'PASS':
                consolidated_validations['status_code']['passed'] += 1
            else:
                # Only count as failed if no specific validation stats indicate otherwise
                consolidated_validations['status_code']['failed'] += 1
        
        # Contract checks
        contract_stats = validation_stats.get('contract_checks', {})
        if contract_stats.get('total', 0) > 0:
            consolidated_validations['contract']['total'] += contract_stats['total']
            consolidated_validations['contract']['passed'] += contract_stats['passed']
            consolidated_validations['contract']['failed'] += contract_stats['failed']
        
        # Security checks
        security_stats = validation_stats.get('security_checks', {})
        if security_stats.get('total', 0) > 0:
            consolidated_validations['security']['total'] += security_stats['total']
            consolidated_validations['security']['passed'] += security_stats['passed']
            consolidated_validations['security']['failed'] += security_stats['failed']
        
        # Performance checks (use actual performance_checks stats if available)
        performance_stats = validation_stats.get('performance_checks', {})
        if performance_stats.get('total', 0) > 0:
            consolidated_validations['performance']['total'] += performance_stats['total']
            consolidated_validations['performance']['passed'] += performance_stats['passed']
            consolidated_validations['performance']['failed'] += performance_stats['failed']
        
        # Data comparisons
        comparison_stats = validation_stats.get('data_comparisons', {})
        if comparison_stats.get('total', 0) > 0:
            consolidated_validations['data_comparison']['total'] += comparison_stats['total']
            consolidated_validations['data_comparison']['passed'] += comparison_stats['passed']
            consolidated_validations['data_comparison']['failed'] += comparison_stats['failed']
        
        # Assertions
        assertion_stats = validation_stats.get('assertions', {})
        if assertion_stats.get('total', 0) > 0:
            consolidated_validations['assertions']['total'] += assertion_stats['total']
            consolidated_validations['assertions']['passed'] += assertion_stats['passed']
            consolidated_validations['assertions']['failed'] += assertion_stats['failed']
    
    # Calculate totals for all validations
    total_validations = sum(v['total'] for v in consolidated_validations.values())
    total_validations_passed = sum(v['passed'] for v in consolidated_validations.values())
    total_validations_failed = sum(v['failed'] for v in consolidated_validations.values())
    total_validations_skipped = 0  # Currently no skipped validations
    
    # Build service and endpoint level statistics
    service_stats = {}
    for result in all_results:
        service_name = result.get('service_name', 'Unknown')
        endpoint = result.get('endpoint', 'Unknown')
        method = result.get('method', 'GET')
        endpoint_key = f"{method} {endpoint}"
        
        # Initialize service if not exists
        if service_name not in service_stats:
            service_stats[service_name] = {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'endpoints': {}
            }
        
        # Initialize endpoint if not exists
        if endpoint_key not in service_stats[service_name]['endpoints']:
            service_stats[service_name]['endpoints'][endpoint_key] = {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'tests': []
            }
        
        # Update service stats
        service_stats[service_name]['total'] += 1
        if result.get('status') == 'PASS':
            service_stats[service_name]['passed'] += 1
        else:
            service_stats[service_name]['failed'] += 1
        
        # Update endpoint stats
        service_stats[service_name]['endpoints'][endpoint_key]['total'] += 1
        if result.get('status') == 'PASS':
            service_stats[service_name]['endpoints'][endpoint_key]['passed'] += 1
        else:
            service_stats[service_name]['endpoints'][endpoint_key]['failed'] += 1
        
        # Store test info
        service_stats[service_name]['endpoints'][endpoint_key]['tests'].append({
            'test_id': result.get('test_id', 'N/A'),
            'status': result.get('status', 'N/A'),
            'response_time_ms': result.get('response_time_ms', 0)
        })
    
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
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    {banner_html}
    <div style="margin: 15px 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; box-shadow: 0 6px 25px rgba(0,0,0,0.1); overflow: hidden;">
        <!-- Header Section -->
        <div style="background: rgba(255,255,255,0.95); padding: 12px 20px; border-bottom: 2px solid {border_color};">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h2 style="margin: 0 0 3px 0; color: #1f2937; font-size: 1.4em; font-weight: 700;">
                        📊 Test Execution Dashboard
                    </h2>
                    <p style="margin: 0; color: #6b7280; font-size: 0.85em;">
                        <strong>Environment:</strong> {env_name} | <strong>Executed:</strong> {current_time}
                    </p>
                </div>
                <div style="text-align: right;">
                    {status_badge}
                </div>
            </div>
        </div>
        
        <!-- Main Content Section -->
        <div style="background: rgba(255,255,255,0.98); padding: 15px 20px;">
            
            <!-- Main Dashboard Grid: Service Stats on Left, Summary Widgets on Right -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                
                <!-- LEFT COLUMN: Service & Endpoint Statistics (Moved Up) -->
                <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); border: 1px solid #e5e7eb;">
                    <h3 style="margin: 0 0 12px 0; color: #312e81; font-size: 1em; font-weight: 700; display: flex; align-items: center; padding-bottom: 8px; border-bottom: 2px solid #e5e7eb;">
                        <span style="margin-right: 8px; font-size: 0.9em;">🔧</span> Service & Endpoint Statistics
                    </h3>
                    <div style="max-height: 600px; overflow-y: auto; overflow-x: hidden;">
                        {{SERVICE_ENDPOINT_STATS_PLACEHOLDER}}
                    </div>
                </div>
                
                <!-- RIGHT COLUMN: Summary Widgets -->
                <div style="display: flex; flex-direction: column; gap: 15px;">
                    
                    <!-- TOP WIDGET: Test Execution Summary + Pie Chart -->
                    <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); border: 1px solid #e5e7eb;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            
                                    <!-- Test Execution Summary Table -->
                            <div>
                        <h3 style="margin: 0 0 12px 0; color: #312e81; font-size: 1em; font-weight: 700; display: flex; align-items: center; border-bottom: 2px solid #6366f1; padding-bottom: 8px;">
                            <span style="margin-right: 8px; font-size: 0.9em;">📈</span> Test Execution Summary
                        </h3>
                        <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden;">
                            <thead>
                                <tr style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white;">
                                    <th style="padding: 8px 10px; text-align: left; font-weight: 600; text-transform: uppercase; font-size: 0.7em; letter-spacing: 0.3px;">Status</th>
                                    <th style="padding: 8px 10px; text-align: center; font-weight: 600; text-transform: uppercase; font-size: 0.7em; letter-spacing: 0.3px;">Count</th>
                                    <th style="padding: 8px 10px; text-align: center; font-weight: 600; text-transform: uppercase; font-size: 0.7em; letter-spacing: 0.3px;">%</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="border-bottom: 2px solid #e5e7eb; background: linear-gradient(90deg, #f8fafc 0%, #f1f5f9 100%);">
                                    <td style="padding: 8px 10px; font-weight: 700; color: #1f2937; font-size: 0.85em;">📊 Total</td>
                                    <td style="padding: 8px 10px; text-align: center; font-weight: 800; color: #6366f1; font-size: 1em;">{total}</td>
                                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; color: #475569; background: #e0e7ff; border-radius: 4px; font-size: 0.85em;">100%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #d1fae5; background: #f0fdf4; transition: all 0.3s;">
                                    <td style="padding: 8px 10px; font-weight: 600; color: #166534; font-size: 0.85em;">✓ Passed</td>
                                    <td style="padding: 8px 10px; text-align: center; font-weight: 800; color: #10b981; font-size: 1em;">{passed}</td>
                                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; color: #059669; background: #d1fae5; border-radius: 4px; font-size: 0.85em;">{pass_percent:.1f}%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #fecaca; background: #fef2f2; transition: all 0.3s;">
                                    <td style="padding: 8px 10px; font-weight: 600; color: #991b1b; font-size: 0.85em;">✗ Failed</td>
                                    <td style="padding: 8px 10px; text-align: center; font-weight: 800; color: #ef4444; font-size: 1em;">{failed}</td>
                                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; color: #dc2626; background: #fecaca; border-radius: 4px; font-size: 0.85em;">{fail_percent:.1f}%</td>
                                </tr>
                                <tr style="background: #fffbeb; transition: all 0.3s;">
                                    <td style="padding: 8px 10px; font-weight: 600; color: #92400e; font-size: 0.85em;">⊘ Skipped</td>
                                    <td style="padding: 8px 10px; text-align: center; font-weight: 800; color: #f59e0b; font-size: 1em;">{skipped}</td>
                                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; color: #d97706; background: #fde68a; border-radius: 4px; font-size: 0.85em;">{skip_percent:.1f}%</td>
                                </tr>
                            </tbody>
                        </table>
                            </div>
                            
                            <!-- Pie Chart - Test Distribution -->
                            <div>
                        <h4 style="margin: 0 0 12px 0; color: #312e81; font-size: 1em; font-weight: 700; text-align: center; border-bottom: 2px solid #6366f1; padding-bottom: 8px;">
                            <span style="font-size: 0.9em;">📊</span> Test Distribution
                        </h4>
                        <div style="width: 100%; max-width: 200px; margin: auto;">
                            <canvas id="testPieChart"></canvas>
                        </div>
                            </div>
                            
                        </div>
                    </div>
                    
                    <!-- BOTTOM WIDGET: Validation Scenarios Summary + Bar Chart -->
                    <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); border: 1px solid #e5e7eb;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            
                            <!-- Validation Scenarios Summary Table -->
                            <div>
                        <h3 style="margin: 0 0 12px 0; color: #312e81; font-size: 1em; font-weight: 700; display: flex; align-items: center; border-bottom: 2px solid #f59e0b; padding-bottom: 8px;">
                            <span style="margin-right: 8px; font-size: 0.9em;">🔍</span> Validation Scenarios Summary
                        </h3>
                        
                        <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden;">
                            <thead>
                                <tr style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white;">
                                    <th style="padding: 8px 10px; text-align: left; font-weight: 600; text-transform: uppercase; font-size: 0.7em; letter-spacing: 0.3px;">Type</th>
                                    <th style="padding: 8px 8px; text-align: center; font-weight: 600; text-transform: uppercase; font-size: 0.7em; letter-spacing: 0.3px;">Total</th>
                                    <th style="padding: 8px 8px; text-align: center; font-weight: 600; text-transform: uppercase; font-size: 0.7em; letter-spacing: 0.3px;">Pass</th>
                                    <th style="padding: 8px 8px; text-align: center; font-weight: 600; text-transform: uppercase; font-size: 0.7em; letter-spacing: 0.3px;">Fail</th>
                                    <th style="padding: 8px 8px; text-align: center; font-weight: 600; text-transform: uppercase; font-size: 0.7em; letter-spacing: 0.3px;">%</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Status Code Row -->
                                <tr style="border-bottom: 1px solid #e5e7eb; transition: all 0.3s;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                    <td style="padding: 8px 10px; font-weight: 600; color: #1f2937; font-size: 0.85em;">🔢 Status</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #6366f1; font-size: 0.9em;">{consolidated_validations['status_code']['total']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #10b981; font-size: 0.9em;">{consolidated_validations['status_code']['passed']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #ef4444; font-size: 0.9em;">{consolidated_validations['status_code']['failed']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: {'#10b981' if consolidated_validations['status_code']['total'] > 0 and consolidated_validations['status_code']['failed'] == 0 else '#ef4444'}; font-size: 0.85em; background: {'#d1fae5' if consolidated_validations['status_code']['total'] > 0 and consolidated_validations['status_code']['failed'] == 0 else '#fecaca'}; border-radius: 4px;">
                                        {(consolidated_validations['status_code']['passed'] / consolidated_validations['status_code']['total'] * 100) if consolidated_validations['status_code']['total'] > 0 else 0:.0f}%
                                    </td>
                                </tr>
                                
                                <!-- Contract Row -->
                                <tr style="border-bottom: 1px solid #e5e7eb; transition: all 0.3s;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                    <td style="padding: 8px 10px; font-weight: 600; color: #1f2937; font-size: 0.85em;">📋 Contract</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #6366f1; font-size: 0.9em;">{consolidated_validations['contract']['total']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #10b981; font-size: 0.9em;">{consolidated_validations['contract']['passed']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #ef4444; font-size: 0.9em;">{consolidated_validations['contract']['failed']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: {'#10b981' if consolidated_validations['contract']['total'] > 0 and consolidated_validations['contract']['failed'] == 0 else '#ef4444'}; font-size: 0.85em; background: {'#d1fae5' if consolidated_validations['contract']['total'] > 0 and consolidated_validations['contract']['failed'] == 0 else '#fecaca'}; border-radius: 4px;">
                                        {(consolidated_validations['contract']['passed'] / consolidated_validations['contract']['total'] * 100) if consolidated_validations['contract']['total'] > 0 else 0:.0f}%
                                    </td>
                                </tr>
                                
                                <!-- Security Row -->
                                <tr style="border-bottom: 1px solid #e5e7eb; transition: all 0.3s;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                    <td style="padding: 8px 10px; font-weight: 600; color: #1f2937; font-size: 0.85em;">🔒 Security</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #6366f1; font-size: 0.9em;">{consolidated_validations['security']['total']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #10b981; font-size: 0.9em;">{consolidated_validations['security']['passed']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #ef4444; font-size: 0.9em;">{consolidated_validations['security']['failed']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: {'#10b981' if consolidated_validations['security']['total'] > 0 and consolidated_validations['security']['failed'] == 0 else '#ef4444'}; font-size: 0.85em; background: {'#d1fae5' if consolidated_validations['security']['total'] > 0 and consolidated_validations['security']['failed'] == 0 else '#fecaca'}; border-radius: 4px;">
                                        {(consolidated_validations['security']['passed'] / consolidated_validations['security']['total'] * 100) if consolidated_validations['security']['total'] > 0 else 0:.0f}%
                                    </td>
                                </tr>
                                
                                <!-- Performance Row -->
                                <tr style="border-bottom: 1px solid #e5e7eb; transition: all 0.3s;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                    <td style="padding: 8px 10px; font-weight: 600; color: #1f2937; font-size: 0.85em;">⚡ Perf</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #6366f1; font-size: 0.9em;">{consolidated_validations['performance']['total']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #10b981; font-size: 0.9em;">{consolidated_validations['performance']['passed']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #ef4444; font-size: 0.9em;">{consolidated_validations['performance']['failed']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: {'#10b981' if consolidated_validations['performance']['total'] > 0 and consolidated_validations['performance']['failed'] == 0 else '#ef4444'}; font-size: 0.85em; background: {'#d1fae5' if consolidated_validations['performance']['total'] > 0 and consolidated_validations['performance']['failed'] == 0 else '#fecaca'}; border-radius: 4px;">
                                        {(consolidated_validations['performance']['passed'] / consolidated_validations['performance']['total'] * 100) if consolidated_validations['performance']['total'] > 0 else 0:.0f}%
                                    </td>
                                </tr>
                                
                                <!-- Data Comparison Row -->
                                <tr style="border-bottom: 1px solid #e5e7eb; transition: all 0.3s;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                    <td style="padding: 8px 10px; font-weight: 600; color: #1f2937; font-size: 0.85em;">🔄 Data Asserts</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #6366f1; font-size: 0.9em;">{consolidated_validations['data_comparison']['total']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #10b981; font-size: 0.9em;">{consolidated_validations['data_comparison']['passed']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #ef4444; font-size: 0.9em;">{consolidated_validations['data_comparison']['failed']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: {'#10b981' if consolidated_validations['data_comparison']['total'] > 0 and consolidated_validations['data_comparison']['failed'] == 0 else '#ef4444'}; font-size: 0.85em; background: {'#d1fae5' if consolidated_validations['data_comparison']['total'] > 0 and consolidated_validations['data_comparison']['failed'] == 0 else '#fecaca'}; border-radius: 4px;">
                                        {(consolidated_validations['data_comparison']['passed'] / consolidated_validations['data_comparison']['total'] * 100) if consolidated_validations['data_comparison']['total'] > 0 else 0:.0f}%
                                    </td>
                                </tr>
                                
                                <!-- Assertions Row -->
                                <tr style="border-bottom: 2px solid #d1d5db; transition: all 0.3s;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                    <td style="padding: 8px 10px; font-weight: 600; color: #1f2937; font-size: 0.85em;">✓ Other Asserts</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #6366f1; font-size: 0.9em;">{consolidated_validations['assertions']['total']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #10b981; font-size: 0.9em;">{consolidated_validations['assertions']['passed']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: #ef4444; font-size: 0.9em;">{consolidated_validations['assertions']['failed']}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: 700; color: {'#10b981' if consolidated_validations['assertions']['total'] > 0 and consolidated_validations['assertions']['failed'] == 0 else '#ef4444'}; font-size: 0.85em; background: {'#d1fae5' if consolidated_validations['assertions']['total'] > 0 and consolidated_validations['assertions']['failed'] == 0 else '#fecaca'}; border-radius: 4px;">
                                        {(consolidated_validations['assertions']['passed'] / consolidated_validations['assertions']['total'] * 100) if consolidated_validations['assertions']['total'] > 0 else 0:.0f}%
                                    </td>
                                </tr>
                                
                                <!-- TOTAL Row -->
                                <tr style="background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); font-weight: 800; border-top: 3px solid #6366f1;">
                                    <td style="padding: 10px; color: #1f2937; font-size: 0.9em; font-weight: 700;">📊 TOTAL</td>
                                    <td style="padding: 10px 8px; text-align: center; color: #6366f1; font-size: 1.05em; font-weight: 900;">{total_validations}</td>
                                    <td style="padding: 10px 8px; text-align: center; color: #10b981; font-size: 1.05em; font-weight: 900;">{total_validations_passed}</td>
                                    <td style="padding: 10px 8px; text-align: center; color: #ef4444; font-size: 1.05em; font-weight: 900;">{total_validations_failed}</td>
                                    <td style="padding: 10px 8px; text-align: center; font-weight: 900; color: {'#10b981' if total_validations > 0 and total_validations_failed == 0 else '#ef4444'}; font-size: 0.95em; background: {'#d1fae5' if total_validations > 0 and total_validations_failed == 0 else '#fecaca'}; border-radius: 4px;">
                                        {(total_validations_passed / total_validations * 100) if total_validations > 0 else 0:.0f}%
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                            </div>
                            
                            <!-- Bar Chart - Validation Results -->
                            <div>
                        <h4 style="margin: 0 0 12px 0; color: #312e81; font-size: 1em; font-weight: 700; text-align: center; border-bottom: 2px solid #f59e0b; padding-bottom: 8px;">
                            <span style="font-size: 0.9em;">📊</span> Validation Distribution
                        </h4>
                        <div style="width: 100%; margin: auto;">
                            <canvas id="validationBarChart"></canvas>
                        </div>
                            </div>
                            
                        </div>
                    </div>
                    
                </div>
                
            </div>
            
            <script>
                // Pie Chart for Test Execution Status
                const ctx = document.getElementById('testPieChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'pie',
                    data: {{
                        labels: ['Passed', 'Failed', 'Skipped'],
                        datasets: [{{
                            data: [{passed}, {failed}, {skipped}],
                            backgroundColor: [
                                'rgba(16, 185, 129, 0.8)',
                                'rgba(239, 68, 68, 0.8)',
                                'rgba(245, 158, 11, 0.8)'
                            ],
                            borderColor: [
                                'rgba(16, 185, 129, 1)',
                                'rgba(239, 68, 68, 1)',
                                'rgba(245, 158, 11, 1)'
                            ],
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{
                                    padding: 15,
                                    font: {{
                                        size: 11,
                                        weight: 'bold'
                                    }}
                                }}
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        const label = context.label || '';
                                        const value = context.parsed || 0;
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = total > 0 ? ((value / total) * 100).toFixed(2) : 0;
                                        return label + ': ' + value + ' (' + percentage + '%)';
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
                
                // Bar Chart for Validation Scenarios
                const ctxBar = document.getElementById('validationBarChart').getContext('2d');
                new Chart(ctxBar, {{
                    type: 'bar',
                    data: {{
                        labels: ['Status Code', 'Contract', 'Security', 'Performance', 'Data Compare', 'Assertions'],
                        datasets: [
                            {{
                                label: 'Passed',
                                data: [
                                    {consolidated_validations['status_code']['passed']},
                                    {consolidated_validations['contract']['passed']},
                                    {consolidated_validations['security']['passed']},
                                    {consolidated_validations['performance']['passed']},
                                    {consolidated_validations['data_comparison']['passed']},
                                    {consolidated_validations['assertions']['passed']}
                                ],
                                backgroundColor: 'rgba(16, 185, 129, 0.8)',
                                borderColor: 'rgba(16, 185, 129, 1)',
                                borderWidth: 2
                            }},
                            {{
                                label: 'Failed',
                                data: [
                                    {consolidated_validations['status_code']['failed']},
                                    {consolidated_validations['contract']['failed']},
                                    {consolidated_validations['security']['failed']},
                                    {consolidated_validations['performance']['failed']},
                                    {consolidated_validations['data_comparison']['failed']},
                                    {consolidated_validations['assertions']['failed']}
                                ],
                                backgroundColor: 'rgba(239, 68, 68, 0.8)',
                                borderColor: 'rgba(239, 68, 68, 1)',
                                borderWidth: 2
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: true,
                        scales: {{
                            x: {{
                                stacked: false,
                                grid: {{
                                    display: false
                                }},
                                ticks: {{
                                    font: {{
                                        size: 10,
                                        weight: 'bold'
                                    }}
                                }}
                            }},
                            y: {{
                                stacked: false,
                                beginAtZero: true,
                                ticks: {{
                                    stepSize: 1,
                                    font: {{
                                        size: 10,
                                        weight: 'bold'
                                    }}
                                }},
                                grid: {{
                                    color: 'rgba(0, 0, 0, 0.05)'
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{
                                    padding: 10,
                                    font: {{
                                        size: 11,
                                        weight: 'bold'
                                    }},
                                    usePointStyle: true,
                                    pointStyle: 'rect'
                                }}
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        return context.dataset.label + ': ' + context.parsed.y;
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            </script>
            
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
        
        /* Make all table rows fixed height with scrollable cells - use more specific selector */
        #results-table-head {{
            display: table-header-group !important;
        }}
        
        #results-table tbody tr {{
            height: 30px !important;
            max-height: 30px !important;
        }}
        
        #results-table tbody tr td {{
            height: 30px !important;
            max-height: 30px !important;
            vertical-align: middle !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }}
        
        /* Fallback for tables without specific ID */
        table tbody tr td {{
            vertical-align: middle !important;
        }}        
    </style>
    '''
    
    # Helper function to build service/endpoint stats HTML
    def _build_service_endpoint_stats_html(service_stats):
        if not service_stats:
            return '<p style="color: #6b7280; font-style: italic;">No service data available</p>'
        
        html_parts = []
        service_index = 0
        for service_name, service_data in sorted(service_stats.items()):
            service_pass_rate = (service_data['passed'] / service_data['total'] * 100) if service_data['total'] > 0 else 0
            service_color = '#10b981' if service_data['failed'] == 0 else '#ef4444'
            service_id = f"service_{service_index}"
            
            # Service header (clickable to expand/collapse)
            html_parts.append(f'''
                <div style="margin-bottom: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                    <!-- Service Header (Clickable) -->
                    <div onclick="var el = document.getElementById('{service_id}'); var icon = document.getElementById('{service_id}_icon'); if(el.style.display === 'none') {{ el.style.display = 'block'; icon.textContent = '▼'; }} else {{ el.style.display = 'none'; icon.textContent = '▶'; }}" 
                         style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); padding: 12px 15px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; user-select: none;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span id="{service_id}_icon" style="color: white; font-size: 0.8em;">▼</span>
                            <div style="color: white; font-size: 1.1em; font-weight: 700;">
                                📦 {service_name}
                            </div>
                        </div>
                        <div style="display: flex; gap: 15px; align-items: center;">
                            <span style="color: rgba(255,255,255,0.9); font-size: 0.9em;">
                                Total: <strong>{service_data['total']}</strong>
                            </span>
                            <span style="color: rgba(255,255,255,0.9); font-size: 0.9em;">
                                ✓ <strong>{service_data['passed']}</strong>
                            </span>
                            <span style="color: rgba(255,255,255,0.9); font-size: 0.9em;">
                                ✗ <strong>{service_data['failed']}</strong>
                            </span>
                            <span style="background: white; color: {service_color}; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.85em;">
                                {service_pass_rate:.1f}%
                            </span>
                        </div>
                    </div>
                    
                    <!-- Endpoints (Collapsible) -->
                    <div id="{service_id}" style="padding: 15px; display: block;">
            ''')
            
            # Endpoint details
            for endpoint_key, endpoint_data in sorted(service_data['endpoints'].items()):
                endpoint_pass_rate = (endpoint_data['passed'] / endpoint_data['total'] * 100) if endpoint_data['total'] > 0 else 0
                endpoint_color = '#10b981' if endpoint_data['failed'] == 0 else '#ef4444'
                
                # Calculate average response time
                avg_response_time = sum(t['response_time_ms'] for t in endpoint_data['tests']) / len(endpoint_data['tests']) if endpoint_data['tests'] else 0
                
                html_parts.append(f'''
                    <div style="margin-bottom: 12px; padding: 10px; background: #f9fafb; border-radius: 6px; border-left: 3px solid {endpoint_color};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="font-weight: 600; color: #1f2937; font-size: 0.95em;">
                                {endpoint_key}
                            </div>
                            <div style="display: flex; gap: 10px; align-items: center;">
                                <span style="color: #6b7280; font-size: 0.85em;">
                                    Tests: <strong>{endpoint_data['total']}</strong>
                                </span>
                                <span style="color: #10b981; font-size: 0.85em;">
                                    ✓ <strong>{endpoint_data['passed']}</strong>
                                </span>
                                <span style="color: #ef4444; font-size: 0.85em;">
                                    ✗ <strong>{endpoint_data['failed']}</strong>
                                </span>
                                <span style="color: #6b7280; font-size: 0.85em;">
                                    ⏱ <strong>{avg_response_time:.0f}ms</strong>
                                </span>
                                <span style="background: {endpoint_color}; color: white; padding: 2px 8px; border-radius: 10px; font-weight: 700; font-size: 0.75em;">
                                    {endpoint_pass_rate:.1f}%
                                </span>
                            </div>
                        </div>
                        
                        <!-- Test IDs -->
                        <div style="color: #6b7280; font-size: 0.8em; padding-left: 10px;">
                            {''.join([f"<span style='display: inline-block; margin-right: 8px; padding: 2px 6px; background: {'#d1fae5' if t['status'] == 'PASS' else '#fee2e2'}; color: {'#065f46' if t['status'] == 'PASS' else '#991b1b'}; border-radius: 4px; font-size: 0.85em;'>{t['test_id']}</span>" for t in endpoint_data['tests']])}
                        </div>
                    </div>
                ''')
            
            html_parts.append('</div></div>')
            service_index += 1
        
        return ''.join(html_parts)
    
    # Replace the placeholder in custom_summary with actual service stats
    custom_summary = custom_summary.replace('{SERVICE_ENDPOINT_STATS_PLACEHOLDER}', _build_service_endpoint_stats_html(service_stats))
    
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
        
        # Get test summary and append failure reason if test failed
        test_summary = test_case.get('test_summary', 'N/A')
        
        # If test failed, append the failure reason/error to the summary
        if report.when == "call" and report.outcome == "failed":
            from framework.test_helpers.test_result_collector import TestResultCollector
            result_collector = TestResultCollector()
            
            # Find matching result entry for this test
            for result in result_collector.get_results():
                if result.get('test_id') == test_id:
                    error_msg = result.get('error') or result.get('reason')
                    if error_msg:
                        # Add error message to summary with visual separation
                        test_summary = f"{test_summary}<br><br><div style='background:#fee; border-left:3px solid #f00; padding:8px; margin-top:8px;'><b style='color:#c00;'>❌ Failure:</b><br>{error_msg}</div>"
                    break
        
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
        
        # Add validation statistics (for both passed and failed tests)
        if report.when == "call":
            from framework.test_helpers.test_result_collector import TestResultCollector
            result_collector = TestResultCollector()
            
            # Find matching result entry
            validation_stats = None
            for result in result_collector.get_results():
                if result.get('test_id') == test_id:
                    validation_stats = result.get('validation_stats', {})
                    break
            
            if validation_stats:
                # Add stats summary with clearer labels
                contract_stats = validation_stats.get('contract_checks', {'total': 0, 'passed': 0, 'failed': 0})
                security_stats = validation_stats.get('security_checks', {'total': 0, 'passed': 0, 'failed': 0})
                performance_stats = validation_stats.get('performance_checks', {'total': 0, 'passed': 0, 'failed': 0})
                assertion_stats = validation_stats.get('assertions', {'total': 0, 'passed': 0, 'failed': 0})
                comparison_stats = validation_stats.get('data_comparisons', {'total': 0, 'passed': 0, 'failed': 0})
                
                # Get detailed validation results
                validation_details = None
                for result in result_collector.get_results():
                    if result.get('test_id') == test_id:
                        validation_details = result.get('validation_details', {})
                        break
                
                # Build stats HTML with detailed table for each validator type
                stats_items = []
                
                # Helper function to create status icon
                def get_status_icon(status):
                    icons = {'PASS': '✅', 'FAIL': '❌', 'SKIP': '⚠️', 'NA': '➖'}
                    return icons.get(status, '❓')
                
                # Contract checks with details
                if contract_stats['total'] > 0:
                    status_icon = '✅' if contract_stats['failed'] == 0 else '❌'
                    stats_items.append(f"<li><b>Contract Results:</b> {status_icon} {contract_stats['passed']}/{contract_stats['total']}")
                    
                    if validation_details and validation_details.get('contract_checks'):
                        # Show table directly (expanded by default for visibility)
                        stats_items.append(f"<table style='margin-left:20px; margin-top:5px; border-collapse:collapse; font-size:0.85em; width:95%;'>")
                        stats_items.append("<tr style='background-color:#f0f0f0;'><th style='padding:3px 8px; text-align:left;'>Check</th><th style='padding:3px 8px;'>Status</th></tr>")
                        for detail in validation_details['contract_checks']:
                            check_name = detail.get('check_name', 'Unknown')
                            check_status = detail.get('status', 'NA')
                            icon = get_status_icon(check_status)
                            stats_items.append(f"<tr><td style='padding:3px 8px;'>{check_name}</td><td style='padding:3px 8px; text-align:center;'>{icon}</td></tr>")
                        stats_items.append("</table>")
                    
                    stats_items.append("</li>")
                    validation_count += 1
                
                # Security checks with details
                if security_stats['total'] > 0:
                    status_icon = '✅' if security_stats['failed'] == 0 else '❌'
                    stats_items.append(f"<li><b>Security Results:</b> {status_icon} {security_stats['passed']}/{security_stats['total']}")
                    
                    if validation_details and validation_details.get('security_checks'):
                        stats_items.append(f"<table style='margin-left:20px; margin-top:5px; border-collapse:collapse; font-size:0.85em; width:95%;'>")
                        stats_items.append("<tr style='background-color:#f0f0f0;'><th style='padding:3px 8px; text-align:left;'>Check</th><th style='padding:3px 8px;'>Status</th></tr>")
                        for detail in validation_details['security_checks']:
                            check_name = detail.get('check_name', 'Unknown')
                            check_status = detail.get('status', 'NA')
                            icon = get_status_icon(check_status)
                            stats_items.append(f"<tr><td style='padding:3px 8px;'>{check_name}</td><td style='padding:3px 8px; text-align:center;'>{icon}</td></tr>")
                        stats_items.append("</table>")
                    
                    stats_items.append("</li>")
                    validation_count += 1
                
                # Performance checks with details
                if performance_stats['total'] > 0:
                    status_icon = '✅' if performance_stats['failed'] == 0 else '❌'
                    stats_items.append(f"<li><b>Performance Results:</b> {status_icon} {performance_stats['passed']}/{performance_stats['total']}")
                    
                    if validation_details and validation_details.get('performance_checks'):
                        stats_items.append(f"<table style='margin-left:20px; margin-top:5px; border-collapse:collapse; font-size:0.85em; width:95%;'>")
                        stats_items.append("<tr style='background-color:#f0f0f0;'><th style='padding:3px 8px; text-align:left;'>Check</th><th style='padding:3px 8px;'>Status</th></tr>")
                        for detail in validation_details['performance_checks']:
                            check_name = detail.get('check_name', 'Unknown')
                            check_status = detail.get('status', 'NA')
                            icon = get_status_icon(check_status)
                            stats_items.append(f"<tr><td style='padding:3px 8px;'>{check_name}</td><td style='padding:3px 8px; text-align:center;'>{icon}</td></tr>")
                        stats_items.append("</table>")
                    
                    stats_items.append("</li>")
                    validation_count += 1
                
                # Assertions with details
                if assertion_stats['total'] > 0:
                    status_icon = '✅' if assertion_stats['failed'] == 0 else '❌'
                    stats_items.append(f"<li><b>Assertions Results:</b> {status_icon} {assertion_stats['passed']}/{assertion_stats['total']}")
                    
                    if validation_details and validation_details.get('assertions'):
                        stats_items.append(f"<table style='margin-left:20px; margin-top:5px; border-collapse:collapse; font-size:0.85em; width:95%;'>")
                        stats_items.append("<tr style='background-color:#f0f0f0;'><th style='padding:3px 8px; text-align:left;'>Assertion</th><th style='padding:3px 8px;'>Status</th></tr>")
                        for detail in validation_details['assertions']:
                            message = detail.get('message', 'Unknown assertion')
                            assertion_status = detail.get('status', 'NA')
                            icon = get_status_icon(assertion_status)
                            # Truncate long messages for display
                            display_message = message if len(message) <= 60 else message[:57] + '...'
                            stats_items.append(f"<tr><td style='padding:3px 8px;'>{display_message}</td><td style='padding:3px 8px; text-align:center;'>{icon}</td></tr>")
                        stats_items.append("</table>")
                    
                    stats_items.append("</li>")
                    validation_count += 1
                
                # Data comparisons with details
                if comparison_stats['total'] > 0:
                    status_icon = '✅' if comparison_stats['failed'] == 0 else '❌'
                    stats_items.append(f"<li><b>Data Compare Results:</b> {status_icon} {comparison_stats['passed']}/{comparison_stats['total']}")
                    
                    if validation_details and validation_details.get('data_comparisons'):
                        stats_items.append(f"<table style='margin-left:20px; margin-top:5px; border-collapse:collapse; font-size:0.85em; width:95%;'>")
                        stats_items.append("<tr style='background-color:#f0f0f0;'><th style='padding:3px 8px; text-align:left;'>Comparison</th><th style='padding:3px 8px;'>Status</th></tr>")
                        for detail in validation_details['data_comparisons']:
                            comparison_name = detail.get('comparison_name', 'Unknown comparison')
                            comparison_status = detail.get('status', 'NA')
                            icon = get_status_icon(comparison_status)
                            stats_items.append(f"<tr><td style='padding:3px 8px;'>{comparison_name}</td><td style='padding:3px 8px; text-align:center;'>{icon}</td></tr>")
                        stats_items.append("</table>")
                    
                    stats_items.append("</li>")
                    validation_count += 1
                
                # Insert stats before closing </ul>
                if stats_items:
                    validations_html = validations_html.replace('</ul>', ''.join(stats_items) + '</ul>')
        
        if validation_count == 0:
            validations_html = 'N/A'
        
        # Insert custom cells (swapped base_url and endpoint order)
        cells.insert(1, f'<td>{test_id}</td>')
        cells.insert(2, f'<td>{service_name}</td>')
        cells.insert(3, f'<td><b>{env_name}</b></td>')
        cells.insert(4, f'<td>{test_type}</td>')
        cells.insert(5, f'<td>{iteration}</td>')
        cells.insert(6, f'<td><b>{method}</b></td>')
        cells.insert(7, f'<td style="height: 30px !important; max-height: 30px !important; overflow-y: auto !important; overflow-x: hidden !important; word-wrap: break-word; padding: 8px;">{base_url}</td>')
        cells.insert(8, f'<td style="height: 30px !important; max-height: 30px !important; overflow-y: auto !important; overflow-x: hidden !important; word-wrap: break-word; padding: 8px;">{endpoint}</td>')
        cells.insert(9, f'<td style="width: 300px; height: 30px !important; max-height: 30px !important; overflow-y: auto !important; overflow-x: hidden !important; padding: 10px; background: linear-gradient(to bottom, #ffffff 0%, #f8f9fa 100%); box-shadow: inset 0 1px 3px rgba(0,0,0,0.05); word-wrap: break-word; white-space: normal;">{validations_html}</td>')
        cells.insert(10, f'<td class="col-summary" style="width: 400px; max-width: 400px; height: 30px !important; max-height: 30px !important; overflow-y: auto !important; word-wrap: break-word; white-space: normal; padding: 10px;">{test_summary}</td>')
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
