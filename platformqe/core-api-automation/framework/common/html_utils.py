"""
HTML Utilities

Centralized HTML generation utilities for test reports and email notifications.
Provides reusable components for generating tables, charts, and other HTML elements.

This module is used by:
- email_reporter.py: Email notifications with test summaries and charts
- conftest.py: Pytest HTML report customization (dashboard style)
- Any component needing HTML visualization of test data

Architecture:
    This module handles PRESENTATION (HTML generation).
    It takes data dictionaries and returns HTML strings.
    
    Data loading is handled by:
    - framework/loaders/test_result_loader.py (loads test results from JSON)
"""

import os
from typing import Dict, Optional, Tuple
from framework.common.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# HTML TABLE GENERATION UTILITIES
# ============================================================================

def generate_test_summary_table(test_summary: Dict, style: str = 'simple') -> str:
    """Generate HTML table for test execution summary.
    
    Args:
        test_summary: Dictionary with test counts (total, passed, failed, skipped)
        style: 'simple' for email, 'dashboard' for pytest HTML report
        
    Returns:
        HTML string with formatted test execution summary table
    """
    total = test_summary.get('total', 0)
    passed = test_summary.get('passed', 0)
    failed = test_summary.get('failed', 0)
    skipped = test_summary.get('skipped', 0)
    
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


def generate_validation_summary_table(validation_stats: Dict, style: str = 'simple') -> str:
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


# ============================================================================
# CHART GENERATION UTILITIES
# ============================================================================

def generate_pie_chart_html(test_summary: Dict, width: int = 150) -> str:
    """
    Generate a pure HTML/CSS pie chart for test results.
    Works in all email clients without JavaScript.
    
    Args:
        test_summary: Dictionary with total, passed, failed, skipped counts
        width: Width of the chart in pixels
        
    Returns:
        HTML string with CSS-based pie chart
    """
    total = test_summary.get('total', 0)
    passed = test_summary.get('passed', 0)
    failed = test_summary.get('failed', 0)
    skipped = test_summary.get('skipped', 0)
    
    if total == 0:
        return '<p style="color: #666; font-style: italic;">No test data available</p>'
    
    # Calculate percentages
    pass_pct = (passed / total) * 100
    fail_pct = (failed / total) * 100
    skip_pct = (skipped / total) * 100
    
    # Calculate cumulative percentages for conic-gradient
    pass_end = pass_pct
    fail_end = pass_end + fail_pct
    skip_end = fail_end + skip_pct
    
    # Colors
    pass_color = '#10b981'  # Green
    fail_color = '#ef4444'  # Red
    skip_color = '#f59e0b'  # Orange/Yellow
    
    return f'''
    <div style="display: inline-block; text-align: center;">
        <div style="
            width: {width}px;
            height: {width}px;
            border-radius: 50%;
            background: conic-gradient(
                {pass_color} 0% {pass_pct}%,
                {fail_color} {pass_pct}% {fail_end}%,
                {skip_color} {fail_end}% {skip_end}%,
                #e5e7eb {skip_end}% 100%
            );
            margin: 10px auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        "></div>
        <div style="margin-top: 10px; font-size: 12px;">
            <span style="display: inline-block; margin: 3px 8px;">
                <span style="display: inline-block; width: 12px; height: 12px; background: {pass_color}; border-radius: 2px; vertical-align: middle;"></span>
                Passed: {passed} ({pass_pct:.1f}%)
            </span>
            <span style="display: inline-block; margin: 3px 8px;">
                <span style="display: inline-block; width: 12px; height: 12px; background: {fail_color}; border-radius: 2px; vertical-align: middle;"></span>
                Failed: {failed} ({fail_pct:.1f}%)
            </span>
            <span style="display: inline-block; margin: 3px 8px;">
                <span style="display: inline-block; width: 12px; height: 12px; background: {skip_color}; border-radius: 2px; vertical-align: middle;"></span>
                Skipped: {skipped} ({skip_pct:.1f}%)
            </span>
        </div>
    </div>
    '''


def generate_horizontal_bar_chart_html(validation_stats: Dict, max_width: int = 300) -> str:
    """
    Generate pure HTML/CSS horizontal bar chart for validation results.
    Works in all email clients without JavaScript.
    
    Args:
        validation_stats: Dictionary with validation counts by type
        max_width: Maximum width of bars in pixels
        
    Returns:
        HTML string with CSS-based horizontal bar chart
    """
    # Colors
    pass_color = '#10b981'  # Green
    fail_color = '#ef4444'  # Red
    
    # Find max value for scaling
    max_value = max(
        max(v['passed'], v['failed'], 1) 
        for v in validation_stats.values()
    )
    
    # Validation type labels with emojis
    labels = {
        'status_code': '🔢 Status Code',
        'contract': '📋 Contract',
        'security': '🔒 Security',
        'performance': '⚡ Performance',
        'data_comparison': '🔄 Data Asserts',
        'assertions': '✓ Assertions'
    }
    
    bars_html = []
    for key, label in labels.items():
        stats = validation_stats.get(key, {'passed': 0, 'failed': 0, 'total': 0})
        passed = stats.get('passed', 0)
        failed = stats.get('failed', 0)
        total = stats.get('total', 0)
        
        # Calculate bar widths
        pass_width = int((passed / max_value) * max_width) if max_value > 0 else 0
        fail_width = int((failed / max_value) * max_width) if max_value > 0 else 0
        
        bars_html.append(f'''
        <tr>
            <td style="padding: 6px 10px; text-align: left; font-size: 13px; white-space: nowrap;">{label}</td>
            <td style="padding: 6px 10px; width: {max_width + 50}px;">
                <div style="display: flex; align-items: center; gap: 2px;">
                    <div style="
                        width: {pass_width}px;
                        height: 18px;
                        background: {pass_color};
                        border-radius: 3px 0 0 3px;
                        display: inline-block;
                    "></div>
                    <div style="
                        width: {fail_width}px;
                        height: 18px;
                        background: {fail_color};
                        border-radius: 0 3px 3px 0;
                        display: inline-block;
                    "></div>
                    <span style="margin-left: 8px; font-size: 11px; color: #666;">
                        {passed}/{total}
                    </span>
                </div>
            </td>
        </tr>
        ''')
    
    return f'''
    <div style="margin: 15px 0;">
        <table style="border-collapse: collapse; width: 100%;">
            <tbody>
                {''.join(bars_html)}
            </tbody>
        </table>
        <div style="margin-top: 10px; font-size: 12px; text-align: center;">
            <span style="margin-right: 15px;">
                <span style="display: inline-block; width: 12px; height: 12px; background: {pass_color}; border-radius: 2px; vertical-align: middle;"></span>
                Passed
            </span>
            <span>
                <span style="display: inline-block; width: 12px; height: 12px; background: {fail_color}; border-radius: 2px; vertical-align: middle;"></span>
                Failed
            </span>
        </div>
    </div>
    '''


def generate_progress_bar_html(passed: int, total: int, label: str = '', width: int = 200) -> str:
    """
    Generate a simple progress bar for pass rate visualization.
    
    Args:
        passed: Number of passed tests/validations
        total: Total number of tests/validations
        label: Optional label for the progress bar
        width: Width of the progress bar in pixels
        
    Returns:
        HTML string with CSS-based progress bar
    """
    if total == 0:
        percentage = 0
    else:
        percentage = (passed / total) * 100
    
    # Determine color based on percentage
    if percentage >= 90:
        color = '#10b981'  # Green
    elif percentage >= 70:
        color = '#f59e0b'  # Orange
    else:
        color = '#ef4444'  # Red
    
    bar_width = int((percentage / 100) * width)
    
    return f'''
    <div style="margin: 5px 0;">
        {f'<span style="font-size: 12px; color: #333; margin-right: 10px;">{label}</span>' if label else ''}
        <div style="
            display: inline-block;
            width: {width}px;
            height: 20px;
            background: #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
            vertical-align: middle;
        ">
            <div style="
                width: {bar_width}px;
                height: 100%;
                background: {color};
                border-radius: 10px;
                transition: width 0.3s;
            "></div>
        </div>
        <span style="font-size: 12px; color: #333; margin-left: 10px; font-weight: bold;">
            {percentage:.1f}% ({passed}/{total})
        </span>
    </div>
    '''


def generate_matplotlib_charts(test_summary: Dict, validation_stats: Dict, output_path: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate matplotlib-based charts and return as base64 encoded images.
    Falls back gracefully if matplotlib is not available.
    
    Args:
        test_summary: Dictionary with test counts
        validation_stats: Dictionary with validation stats
        output_path: Optional path to save chart images
        
    Returns:
        Tuple of (pie_chart_base64, bar_chart_base64) or (None, None) if matplotlib unavailable
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import io
        import base64
        
        # Color scheme
        colors = {
            'passed': '#10b981',
            'failed': '#ef4444', 
            'skipped': '#f59e0b'
        }
        
        # === PIE CHART ===
        fig1, ax1 = plt.subplots(figsize=(4, 4), dpi=100)
        
        passed = test_summary.get('passed', 0)
        failed = test_summary.get('failed', 0)
        skipped = test_summary.get('skipped', 0)
        
        sizes = [passed, failed, skipped]
        labels = ['Passed', 'Failed', 'Skipped']
        chart_colors = [colors['passed'], colors['failed'], colors['skipped']]
        explode = (0.02, 0.02, 0.02)
        
        # Filter out zero values
        non_zero = [(s, l, c, e) for s, l, c, e in zip(sizes, labels, chart_colors, explode) if s > 0]
        if non_zero:
            sizes, labels, chart_colors, explode = zip(*non_zero)
            ax1.pie(sizes, explode=explode, labels=labels, colors=chart_colors,
                    autopct='%1.1f%%', startangle=90, shadow=True)
        
        ax1.set_title('Test Results Distribution', fontsize=12, fontweight='bold')
        ax1.axis('equal')
        
        # Save pie chart to base64
        buf1 = io.BytesIO()
        fig1.savefig(buf1, format='png', bbox_inches='tight', facecolor='white')
        buf1.seek(0)
        pie_base64 = base64.b64encode(buf1.read()).decode('utf-8')
        plt.close(fig1)
        
        # === BAR CHART ===
        fig2, ax2 = plt.subplots(figsize=(6, 4), dpi=100)
        
        categories = ['Status', 'Contract', 'Security', 'Perf', 'Data', 'Asserts']
        keys = ['status_code', 'contract', 'security', 'performance', 'data_comparison', 'assertions']
        
        passed_vals = [validation_stats.get(k, {}).get('passed', 0) for k in keys]
        failed_vals = [validation_stats.get(k, {}).get('failed', 0) for k in keys]
        
        x = range(len(categories))
        width = 0.35
        
        bars1 = ax2.bar([i - width/2 for i in x], passed_vals, width, 
                        label='Passed', color=colors['passed'])
        bars2 = ax2.bar([i + width/2 for i in x], failed_vals, width,
                        label='Failed', color=colors['failed'])
        
        ax2.set_xlabel('Validation Type')
        ax2.set_ylabel('Count')
        ax2.set_title('Validation Results by Type', fontsize=12, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars1 + bars2:
            height = bar.get_height()
            if height > 0:
                ax2.annotate(f'{int(height)}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        # Save bar chart to base64
        buf2 = io.BytesIO()
        fig2.savefig(buf2, format='png', bbox_inches='tight', facecolor='white')
        buf2.seek(0)
        bar_base64 = base64.b64encode(buf2.read()).decode('utf-8')
        plt.close(fig2)
        
        # Optionally save to files
        if output_path:
            pie_path = os.path.join(output_path, 'test_pie_chart.png')
            bar_path = os.path.join(output_path, 'validation_bar_chart.png')
            
            # Re-save from base64 to files
            import base64 as b64
            with open(pie_path, 'wb') as f:
                f.write(b64.b64decode(pie_base64))
            with open(bar_path, 'wb') as f:
                f.write(b64.b64decode(bar_base64))
            
            logger.info(f"Charts saved to: {pie_path}, {bar_path}")
        
        return pie_base64, bar_base64
        
    except ImportError:
        logger.warning("matplotlib not available, falling back to HTML/CSS charts")
        return None, None
    except Exception as e:
        logger.error(f"Failed to generate matplotlib charts: {e}")
        return None, None


# ============================================================================
# EMAIL SECTION GENERATION UTILITIES
# ============================================================================

def generate_email_charts_section(test_summary: Dict, validation_stats: Dict, use_matplotlib: bool = False) -> str:
    """
    Generate complete charts section for email body.
    Uses matplotlib if available and requested, otherwise falls back to HTML/CSS.
    
    Args:
        test_summary: Dictionary with test counts
        validation_stats: Dictionary with validation stats
        use_matplotlib: Whether to try using matplotlib for better charts
        
    Returns:
        HTML string with charts section
    """
    charts_html = '<div style="margin: 20px 0;">'
    
    if use_matplotlib:
        pie_b64, bar_b64 = generate_matplotlib_charts(test_summary, validation_stats)
        
        if pie_b64 and bar_b64:
            # Use matplotlib-generated images
            charts_html += f'''
            <h3 style="color: #333; border-bottom: 2px solid #6366f1; padding-bottom: 8px;">📊 Visual Summary</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin: 15px 0;">
                <div style="text-align: center;">
                    <h4 style="margin: 0 0 10px 0; color: #555;">Test Results</h4>
                    <img src="data:image/png;base64,{pie_b64}" alt="Test Results Pie Chart" style="max-width: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />
                </div>
                <div style="text-align: center;">
                    <h4 style="margin: 0 0 10px 0; color: #555;">Validation Results</h4>
                    <img src="data:image/png;base64,{bar_b64}" alt="Validation Results Bar Chart" style="max-width: 450px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />
                </div>
            </div>
            '''
            charts_html += '</div>'
            return charts_html
    
    # Fallback to HTML/CSS charts - only pie and bar charts (pass rates shown separately)
    charts_html += f'''
    <div style="text-align: center; margin-bottom: 15px;">
        <h4 style="margin: 0 0 10px 0; color: #555;">Test Results Distribution</h4>
        {generate_pie_chart_html(test_summary, width=120)}
    </div>
    <div style="margin-top: 15px;">
        <h4 style="margin: 0 0 10px 0; color: #555;">Validation Results by Type</h4>
        {generate_horizontal_bar_chart_html(validation_stats, max_width=180)}
    </div>
    '''
    
    charts_html += '</div>'
    return charts_html


def generate_overall_pass_rates_section(test_summary: Dict, validation_stats: Dict) -> str:
    """
    Generate the Overall Pass Rates section with progress bars.
    This is displayed separately from the visual charts section.
    
    Args:
        test_summary: Dictionary with test counts
        validation_stats: Dictionary with validation stats
        
    Returns:
        HTML string with pass rates section
    """
    total = test_summary.get('total', 0)
    passed = test_summary.get('passed', 0)
    total_val = sum(v['total'] for v in validation_stats.values()) if validation_stats else 0
    total_val_passed = sum(v['passed'] for v in validation_stats.values()) if validation_stats else 0
    
    return f'''
    <div style="margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 10px; border: 1px solid #e2e8f0;">
        <h3 style="margin: 0 0 12px 0; color: #333; font-size: 16px;">📊 Overall Pass Rates</h3>
        {generate_progress_bar_html(passed, total, 'Tests', 280)}
        {generate_progress_bar_html(total_val_passed, total_val, 'Validations', 280)}
    </div>
    '''
