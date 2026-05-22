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
    results. At pytest_sessionfinish, results are persisted to test_results_summary.json.
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
        
        # Find test_results_summary.json (primary source with full validation stats)
        test_summary_pattern = os.path.join(reports_path, 'test_results_summary.json')
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
                
                logger.info(f"Loaded {len(test_results)} test results from test_results_summary.json")
                return test_results, test_summary
        
        # Fallback: Try to load from json_report_*.json
        logger.warning("test_results_summary.json not found, falling back to json_report_*.json")
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


# ============================================================================
# BACKWARD COMPATIBILITY IMPORTS
# ============================================================================
# HTML generation functions have been moved to framework/common/html_utils.py
# These imports maintain backward compatibility for existing code

from framework.common.html_utils import (
    generate_test_summary_table,
    generate_validation_summary_table,
    generate_pie_chart_html,
    generate_horizontal_bar_chart_html,
    generate_progress_bar_html,
    generate_matplotlib_charts,
    generate_email_charts_section,
    generate_overall_pass_rates_section
)

__all__ = [
    # Data loading functions (primary purpose of this module)
    'load_test_summary_from_json',
    'aggregate_validation_stats',
    # HTML generation (re-exported for backward compatibility)
    'generate_test_summary_table',
    'generate_validation_summary_table',
    'generate_pie_chart_html',
    'generate_horizontal_bar_chart_html',
    'generate_progress_bar_html',
    'generate_matplotlib_charts',
    'generate_email_charts_section',
    'generate_overall_pass_rates_section',
]
