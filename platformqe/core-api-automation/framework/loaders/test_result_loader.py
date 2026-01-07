"""
Test Result Loader

Centralized utilities for loading persisted test results from JSON files.
Used by all reporters (email, InfluxDB, custom) and any component needing 
access to test execution data.

This module follows the loader pattern used throughout the framework:
- config_loader.py: Loads configuration
- path_loader.py: Loads/resolves paths  
- test_result_loader.py: Loads test results

Architecture:
    During test execution, TestResultCollector (in-memory singleton) collects
    results. At pytest_sessionfinish, results are persisted to test_summary.json.
    This loader reads those persisted results for use in reporters and other
    post-execution processes.
"""

import os
import glob
import json
from typing import Dict, List, Tuple, Optional
from framework.common.logger import get_logger

logger = get_logger(__name__)


def load_test_summary_from_json(reports_path: Optional[str] = None) -> Tuple[List[Dict], Dict]:
    """
    Load test results and summary from persisted JSON file.
    
    This is the CENTRALIZED function that all reporters and components should use
    to load test results. It handles file-based persistence needed for cross-process
    communication (e.g., email reporter running in separate process from pytest).
    
    Args:
        reports_path: Path to reports directory (e.g., 'reports/20231230_150928/')
                     If None, auto-detects the latest timestamped folder
    
    Returns:
        tuple: (test_results, test_summary)
            - test_results: List of test result dictionaries with validation_stats
            - test_summary: Summary statistics (total, passed, failed, skipped)
    
    Example:
        >>> # From email reporter or influx reporter
        >>> from framework.loaders.test_result_loader import load_test_summary_from_json
        >>> results, summary = load_test_summary_from_json('reports/20231230_150928/')
        >>> print(f"Total tests: {summary['total']}")
        >>> print(f"Test results: {len(results)}")
        
        >>> # Auto-detect latest folder
        >>> results, summary = load_test_summary_from_json()
    """
    test_results = []
    test_summary = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
    
    try:
        # Auto-detect latest reports folder if not specified
        if not reports_path:
            reports_dir = 'reports'
            if os.path.exists(reports_dir):
                # Find all timestamped folders
                folders = [
                    os.path.join(reports_dir, f) for f in os.listdir(reports_dir)
                    if os.path.isdir(os.path.join(reports_dir, f)) 
                    and f != 'archive' 
                    and not f.startswith('.')
                ]
                if folders:
                    # Get the latest folder by modification time
                    reports_path = max(folders, key=os.path.getmtime)
                    logger.info(f"Auto-detected reports path: {reports_path}")
                else:
                    logger.warning(f"No timestamped folders found in {reports_dir}")
                    return test_results, test_summary
            else:
                logger.error(f"Reports directory not found: {reports_dir}")
                return test_results, test_summary
        
        # Find test_summary.json (primary source with full validation stats)
        test_summary_pattern = os.path.join(reports_path, 'test_summary.json')
        summary_file = None
        
        if os.path.exists(test_summary_pattern):
            summary_file = test_summary_pattern
        else:
            # Try glob pattern in case there's a timestamp suffix
            summary_files = glob.glob(os.path.join(reports_path, 'test_summary*.json'))
            if summary_files:
                summary_file = max(summary_files, key=os.path.getmtime)
        
        if summary_file:
            logger.info(f"Loading test summary from: {summary_file}")
            
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
            
            # Extract results and summary
            if isinstance(summary_data, dict):
                test_results = summary_data.get('results', [])
                test_summary = summary_data.get('summary', test_summary)
                
                logger.info(f"Loaded {len(test_results)} test results from test_summary.json")
                return test_results, test_summary
        
        # Fallback: Try to load from json_report_*.json
        logger.warning("test_summary.json not found, falling back to json_report_*.json")
        json_pattern = os.path.join(reports_path, 'json_report_*.json')
        json_files = glob.glob(json_pattern)
        
        if not json_files:
            logger.warning(f"No JSON report files found in {reports_path}")
            return test_results, test_summary
        
        # Use the most recent JSON file
        json_file = max(json_files, key=os.path.getmtime)
        logger.info(f"Loading from fallback file: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract from json_report format
        if isinstance(data, dict):
            if 'results' in data:
                # Map pytest results to test result format
                for result in data['results']:
                    test_results.append({
                        'test_id': result.get('test_id', ''),
                        'test_name': result.get('test_id', ''),
                        'status': result.get('outcome', '').upper(),
                        'validation_stats': result.get('validation_stats', {})
                    })
            
            # Use summary from JSON report
            if 'summary' in data:
                json_summary = data['summary']
                test_summary = {
                    'total': json_summary.get('total', 0),
                    'passed': json_summary.get('passed', 0),
                    'failed': json_summary.get('failed', 0),
                    'skipped': json_summary.get('skipped', 0)
                }
        
        # Calculate summary from test_results if not loaded
        if test_results and test_summary['total'] == 0:
            test_summary = {
                'total': len(test_results),
                'passed': sum(1 for r in test_results if r.get('status') == 'PASS'),
                'failed': sum(1 for r in test_results if r.get('status') == 'FAIL'),
                'skipped': sum(1 for r in test_results if r.get('status') == 'SKIPPED')
            }
        
        logger.info(f"Loaded {len(test_results)} test results. Summary: {test_summary}")
        
    except Exception as e:
        logger.error(f"Failed to load test results from JSON: {e}")
        import traceback
        traceback.print_exc()
    
    return test_results, test_summary


def aggregate_validation_stats(test_results: List[Dict]) -> Dict[str, Dict[str, int]]:
    """
    Aggregate validation statistics from test results list.
    
    This is the CENTRALIZED function for aggregating validation stats from
    loaded test results. Works independently of TestResultCollector instance,
    making it suitable for use in separate processes (reporters, analyzers, etc.).
    
    Args:
        test_results: List of test result dictionaries (from load_test_summary_from_json)
    
    Returns:
        Dictionary with aggregated validation statistics by type:
            - status_code: Status code validation counts
            - contract: Contract validation counts
            - security: Security validation counts
            - performance: Performance validation counts
            - assertions: Assertion validation counts
            - data_comparison: Data comparison validation counts
    
    Example:
        >>> from framework.loaders.test_result_loader import (
        ...     load_test_summary_from_json,
        ...     aggregate_validation_stats
        ... )
        >>> results, _ = load_test_summary_from_json()
        >>> stats = aggregate_validation_stats(results)
        >>> print(f"Contract checks: {stats['contract']['total']}")
        45
        >>> print(f"Contract passed: {stats['contract']['passed']}")
        43
    """
    validation_stats = {
        'status_code': {'total': 0, 'passed': 0, 'failed': 0},
        'contract': {'total': 0, 'passed': 0, 'failed': 0},
        'security': {'total': 0, 'passed': 0, 'failed': 0},
        'performance': {'total': 0, 'passed': 0, 'failed': 0},
        'assertions': {'total': 0, 'passed': 0, 'failed': 0},
        'data_comparison': {'total': 0, 'passed': 0, 'failed': 0}
    }
    
    if not test_results:
        return validation_stats
    
    for result in test_results:
        vstats = result.get('validation_stats', {})
        
        if not vstats:
            continue
        
        # Aggregate each validation type
        # Mapping from validation_stats keys to aggregated stats keys
        for check_type, stat_key in [
            ('status_code_checks', 'status_code'),
            ('contract_checks', 'contract'),
            ('security_checks', 'security'),
            ('performance_checks', 'performance'),
            ('assertions', 'assertions'),
            ('data_comparisons', 'data_comparison')
        ]:
            if check_type in vstats:
                validation_stats[stat_key]['total'] += vstats[check_type].get('total', 0)
                validation_stats[stat_key]['passed'] += vstats[check_type].get('passed', 0)
                validation_stats[stat_key]['failed'] += vstats[check_type].get('failed', 0)
    
    return validation_stats


def generate_test_summary_table(test_summary, style='simple'):
    """Generate HTML table for test execution summary.
    
    Args:
        test_summary: Dictionary with test counts (total, passed, failed, skipped)
        style: 'simple' for email, 'dashboard' for pytest HTML report
        
    Returns:
        HTML string with formatted test execution summary table
    """
    total = test_summary['total']
    passed = test_summary['passed']
    failed = test_summary['failed']
    skipped = test_summary['skipped']
    
    pass_pct = (passed / total * 100) if total > 0 else 0
    fail_pct = (failed / total * 100) if total > 0 else 0
    skip_pct = (skipped / total * 100) if total > 0 else 0
    
    if style == 'dashboard':
        return f"""
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
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; color: #059669; background: #d1fae5; border-radius: 4px; font-size: 0.85em;">{pass_pct:.1f}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #fecaca; background: #fef2f2; transition: all 0.3s;">
                    <td style="padding: 8px 10px; font-weight: 600; color: #991b1b; font-size: 0.85em;">✗ Failed</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 800; color: #ef4444; font-size: 1em;">{failed}</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; color: #dc2626; background: #fecaca; border-radius: 4px; font-size: 0.85em;">{fail_pct:.1f}%</td>
                </tr>
                <tr style="background: #fffbeb; transition: all 0.3s;">
                    <td style="padding: 8px 10px; font-weight: 600; color: #92400e; font-size: 0.85em;">⊘ Skipped</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 800; color: #f59e0b; font-size: 1em;">{skipped}</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; color: #d97706; background: #fde68a; border-radius: 4px; font-size: 0.85em;">{skip_pct:.1f}%</td>
                </tr>
            </tbody>
        </table>
        """
    else:  # simple style for email
        return f"""
        <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Status</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Count</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">%</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">📊 Total</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;"><strong>{total}</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">100%</td>
                </tr>
                <tr style="background-color: #d4edda;">
                    <td style="border: 1px solid #ddd; padding: 8px;">✓ Passed</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;"><strong>{passed}</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{pass_pct:.1f}%</td>
                </tr>
                <tr style="background-color: #f8d7da;">
                    <td style="border: 1px solid #ddd; padding: 8px;">✗ Failed</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;"><strong>{failed}</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{fail_pct:.1f}%</td>
                </tr>
                <tr style="background-color: #fff3cd;">
                    <td style="border: 1px solid #ddd; padding: 8px;">⊘ Skipped</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;"><strong>{skipped}</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{skip_pct:.1f}%</td>
                </tr>
            </tbody>
        </table>
        """


def generate_validation_summary_table(validation_stats, style='simple'):
    """Generate HTML table for validation scenarios summary.
    
    Args:
        validation_stats: Dictionary with validation counts by type
        style: 'simple' for email, 'dashboard' for pytest HTML report
        
    Returns:
        HTML string with formatted validation summary table
    """
    total_validations = sum(v['total'] for v in validation_stats.values())
    total_val_passed = sum(v['passed'] for v in validation_stats.values())
    total_val_failed = sum(v['failed'] for v in validation_stats.values())
    
    if style == 'dashboard':
        return f"""
        <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden;">
            <thead>
                <tr style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white;">
                    <th style="padding: 8px 10px; text-align: left; font-weight: 600; text-transform: uppercase; font-size: 0.7em; letter-spacing: 0.3px;">Type</th>
                    <th style="padding: 8px 10px; text-align: center; font-weight: 600; text-transform: uppercase; font-size: 0.7em; letter-spacing: 0.3px;">Total</th>
                    <th style="padding: 8px 10px; text-align: center; font-weight: 600; text-transform: uppercase; font-size: 0.7em; letter-spacing: 0.3px;">Pass</th>
                    <th style="padding: 8px 10px; text-align: center; font-weight: 600; text-transform: uppercase; font-size: 0.7em; letter-spacing: 0.3px;">Fail</th>
                    <th style="padding: 8px 10px; text-align: center; font-weight: 600; text-transform: uppercase; font-size: 0.7em; letter-spacing: 0.3px;">%</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 8px 10px; font-weight: 600; font-size: 0.85em; color: #1f2937;">🔢 Status</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; font-size: 0.85em;">{validation_stats['status_code']['total']}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #10b981; font-weight: 700; font-size: 0.85em;">{validation_stats['status_code']['passed']}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #ef4444; font-weight: 700; font-size: 0.85em;">{validation_stats['status_code']['failed']}</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; font-size: 0.85em; background: #fef3c7; border-radius: 4px;">{(validation_stats['status_code']['passed'] / validation_stats['status_code']['total'] * 100) if validation_stats['status_code']['total'] > 0 else 0:.0f}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 8px 10px; font-weight: 600; font-size: 0.85em; color: #1f2937;">📋 Contract</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; font-size: 0.85em;">{validation_stats['contract']['total']}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #10b981; font-weight: 700; font-size: 0.85em;">{validation_stats['contract']['passed']}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #ef4444; font-weight: 700; font-size: 0.85em;">{validation_stats['contract']['failed']}</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; font-size: 0.85em; background: #fef3c7; border-radius: 4px;">{(validation_stats['contract']['passed'] / validation_stats['contract']['total'] * 100) if validation_stats['contract']['total'] > 0 else 0:.0f}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 8px 10px; font-weight: 600; font-size: 0.85em; color: #1f2937;">🔒 Security</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; font-size: 0.85em;">{validation_stats['security']['total']}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #10b981; font-weight: 700; font-size: 0.85em;">{validation_stats['security']['passed']}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #ef4444; font-weight: 700; font-size: 0.85em;">{validation_stats['security']['failed']}</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; font-size: 0.85em; background: #fef3c7; border-radius: 4px;">{(validation_stats['security']['passed'] / validation_stats['security']['total'] * 100) if validation_stats['security']['total'] > 0 else 0:.0f}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 8px 10px; font-weight: 600; font-size: 0.85em; color: #1f2937;">⚡ Perf</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; font-size: 0.85em;">{validation_stats['performance']['total']}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #10b981; font-weight: 700; font-size: 0.85em;">{validation_stats['performance']['passed']}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #ef4444; font-weight: 700; font-size: 0.85em;">{validation_stats['performance']['failed']}</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; font-size: 0.85em; background: #fef3c7; border-radius: 4px;">{(validation_stats['performance']['passed'] / validation_stats['performance']['total'] * 100) if validation_stats['performance']['total'] > 0 else 0:.0f}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 8px 10px; font-weight: 600; font-size: 0.85em; color: #1f2937;">🔄 Data Asserts</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; font-size: 0.85em;">{validation_stats['data_comparison']['total']}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #10b981; font-weight: 700; font-size: 0.85em;">{validation_stats['data_comparison']['passed']}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #ef4444; font-weight: 700; font-size: 0.85em;">{validation_stats['data_comparison']['failed']}</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; font-size: 0.85em; background: #fef3c7; border-radius: 4px;">{(validation_stats['data_comparison']['passed'] / validation_stats['data_comparison']['total'] * 100) if validation_stats['data_comparison']['total'] > 0 else 0:.0f}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 8px 10px; font-weight: 600; font-size: 0.85em; color: #1f2937;">✓ Other Asserts</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; font-size: 0.85em;">{validation_stats['assertions']['total']}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #10b981; font-weight: 700; font-size: 0.85em;">{validation_stats['assertions']['passed']}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #ef4444; font-weight: 700; font-size: 0.85em;">{validation_stats['assertions']['failed']}</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 700; font-size: 0.85em; background: #fef3c7; border-radius: 4px;">{(validation_stats['assertions']['passed'] / validation_stats['assertions']['total'] * 100) if validation_stats['assertions']['total'] > 0 else 0:.0f}%</td>
                </tr>
                <tr style="background: linear-gradient(90deg, #f8fafc 0%, #f1f5f9 100%); font-weight: 800;">
                    <td style="padding: 8px 10px; color: #1f2937; font-size: 0.85em;">📊 TOTAL</td>
                    <td style="padding: 8px 10px; text-align: center; color: #6366f1; font-size: 0.9em;">{total_validations}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #10b981; font-size: 0.9em;">{total_val_passed}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #ef4444; font-size: 0.9em;">{total_val_failed}</td>
                    <td style="padding: 8px 10px; text-align: center; background: #e0e7ff; border-radius: 4px; font-size: 0.9em;">{(total_val_passed / total_validations * 100) if total_validations > 0 else 0:.0f}%</td>
                </tr>
            </tbody>
        </table>
        """
    else:  # simple style for email
        return f"""
        <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Type</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Total</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Pass</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Fail</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">%</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">🔢 Status</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['status_code']['total']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['status_code']['passed']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['status_code']['failed']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{(validation_stats['status_code']['passed'] / validation_stats['status_code']['total'] * 100) if validation_stats['status_code']['total'] > 0 else 0:.0f}%</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">📋 Contract</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['contract']['total']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['contract']['passed']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['contract']['failed']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{(validation_stats['contract']['passed'] / validation_stats['contract']['total'] * 100) if validation_stats['contract']['total'] > 0 else 0:.0f}%</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">🔒 Security</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['security']['total']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['security']['passed']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['security']['failed']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{(validation_stats['security']['passed'] / validation_stats['security']['total'] * 100) if validation_stats['security']['total'] > 0 else 0:.0f}%</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">⚡ Perf</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['performance']['total']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['performance']['passed']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['performance']['failed']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{(validation_stats['performance']['passed'] / validation_stats['performance']['total'] * 100) if validation_stats['performance']['total'] > 0 else 0:.0f}%</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">🔄 Data Asserts</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['data_comparison']['total']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['data_comparison']['passed']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['data_comparison']['failed']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{(validation_stats['data_comparison']['passed'] / validation_stats['data_comparison']['total'] * 100) if validation_stats['data_comparison']['total'] > 0 else 0:.0f}%</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">✓ Other Asserts</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['assertions']['total']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['assertions']['passed']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{validation_stats['assertions']['failed']}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{(validation_stats['assertions']['passed'] / validation_stats['assertions']['total'] * 100) if validation_stats['assertions']['total'] > 0 else 0:.0f}%</td>
                </tr>
                <tr style="background-color: #f2f2f2; font-weight: bold;">
                    <td style="border: 1px solid #ddd; padding: 8px;">📊 TOTAL</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{total_validations}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{total_val_passed}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{total_val_failed}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{(total_val_passed / total_validations * 100) if total_validations > 0 else 0:.0f}%</td>
                </tr>
            </tbody>
        </table>
        """
