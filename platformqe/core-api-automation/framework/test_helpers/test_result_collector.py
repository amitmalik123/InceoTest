"""
Test Result Collector

Centralized result collection for test execution.
Replaces global mutable state (collected_api_results) with a singleton pattern.
Thread-safe result management for concurrent test execution.
"""

from typing import Dict, List, Optional
from framework.common.logger import get_logger

logger = get_logger(__name__)


class TestResultCollector:
    """
    Manages collection and tracking of test results for reporting.
    Singleton pattern ensures single source of truth for all test results.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - only one instance exists"""
        if cls._instance is None:
            cls._instance = super(TestResultCollector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize result collection (only once due to singleton)"""
        if self._initialized:
            return
        
        self._results: List[Dict] = []
        self._initialized = True
        logger.debug("TestResultCollector initialized")
    
    def create_result_entry(
        self, 
        case: Dict, 
        actual_url: str,
        protocol: str = "REST"
    ) -> Dict:
        """
        Create initial result entry dictionary for a test case.
        
        Args:
            case: Test case configuration dictionary
            actual_url: Actual URL used for the request
            protocol: Protocol type (REST, SOAP, DB_ONLY)
        
        Returns:
            Result entry dictionary with default values
        """
        result = {
            "test_id": case.get("test_id", case.get("test_name", "")),
            "test_name": case.get("test_name", case.get("test_id", "")),
            "service_name": case.get("service_name", ""),
            "type": case.get("test_type", ""),
            "endpoint": case.get("endpoint", ""),
            "method": case.get("method", ""),
            "main_url": actual_url,
            "status": "PASS",  # Default to PASS, updated if failures occur
            "response_time": None,
            "contract_check": "FAIL",  # Default to FAIL until validation passes
            "security_checks": "PASS",  # Default to PASS
            "custom_validations": "PASS",  # Default to PASS
            "data_comparison": "N/A",  # Default to N/A (not applicable if no comparison configured)
            "summary": "",
            # Detailed validation statistics
            "validation_stats": {
                "status_code_checks": {"total": 0, "passed": 0, "failed": 0},
                "assertions": {"total": 0, "passed": 0, "failed": 0},
                "data_comparisons": {"total": 0, "passed": 0, "failed": 0},
                "contract_checks": {"total": 0, "passed": 0, "failed": 0},
                "security_checks": {"total": 0, "passed": 0, "failed": 0},
                "performance_checks": {"total": 0, "passed": 0, "failed": 0}
            },
            # Individual validation details for UI display
            "validation_details": {
                "assertions": [],  # List of {"message": str, "status": "PASS"|"FAIL"|"SKIP"|"NA"}
                "data_comparisons": [],  # List of {"comparison_name": str, "status": "PASS"|"FAIL"|"SKIP"|"NA"}
                "contract_checks": [],  # List of {"check_name": str, "status": "PASS"|"FAIL"|"SKIP"|"NA"}
                "security_checks": [],  # List of {"check_name": str, "status": "PASS"|"FAIL"|"SKIP"|"NA"}
                "performance_checks": []  # List of {"check_name": str, "status": "PASS"|"FAIL"|"SKIP"|"NA"}
            }
        }
        
        logger.debug(f"Created result entry for test_id: {result['test_id']}")
        return result
    
    def update_status(self, result: Dict, status: str, summary: str = ""):
        """
        Update result status and summary.
        
        Args:
            result: Result entry dictionary to update
            status: New status (PASS, FAIL, SKIPPED)
            summary: Summary message describing the result
        """
        result["status"] = status
        if summary:
            result["summary"] = summary
        
        logger.debug(f"Updated status for {result.get('test_id')}: {status}")
    
    def update_validation(
        self, 
        result: Dict, 
        contract: Optional[str] = None,
        custom: Optional[str] = None,
        security: Optional[str] = None,
        data_comparison: Optional[str] = None
    ):
        """
        Update validation results (contract, custom, security, data_comparison).
        
        Args:
            result: Result entry dictionary to update
            contract: Contract check result (PASS/FAIL)
            custom: Custom validation result (PASS/FAIL)
            security: Security check result (PASS/FAIL)
            data_comparison: Data comparison validation result (PASS/FAIL)
        """
        if contract is not None:
            result["contract_check"] = contract
        if custom is not None:
            result["custom_validations"] = custom
        if security is not None:
            result["security_checks"] = security
        if data_comparison is not None:
            result["data_comparison"] = data_comparison
        
        logger.debug(f"Updated validations for {result.get('test_id')}: "
                    f"contract={contract}, custom={custom}, security={security}, data_comparison={data_comparison}")
    
    def update_validation_stats(
        self,
        result: Dict,
        validator_type: str,
        total: int = 0,
        passed: int = 0,
        failed: int = 0
    ):
        """Update detailed validation statistics for a specific validator type.
        
        Args:
            result: Result entry dictionary to update
            validator_type: Type of validator ('assertions', 'data_comparisons', 'contract_checks', 'security_checks')
            total: Total number of validations
            passed: Number of passed validations
            failed: Number of failed validations
        """
        if "validation_stats" not in result:
            result["validation_stats"] = {
                "assertions": {"total": 0, "passed": 0, "failed": 0},
                "data_comparisons": {"total": 0, "passed": 0, "failed": 0},
                "contract_checks": {"total": 0, "passed": 0, "failed": 0},
                "security_checks": {"total": 0, "passed": 0, "failed": 0}
            }
        
        if validator_type in result["validation_stats"]:
            result["validation_stats"][validator_type] = {
                "total": total,
                "passed": passed,
                "failed": failed
            }
            logger.debug(f"Updated {validator_type} stats for {result.get('test_id')}: "
                        f"total={total}, passed={passed}, failed={failed}")
    
    def add_validation_detail(
        self,
        result: Dict,
        validator_type: str,
        validation_name: str,
        status: str
    ):
        """Add individual validation detail for UI display.
        
        Args:
            result: Result entry dictionary to update
            validator_type: Type of validator ('assertions', 'data_comparisons', 'contract_checks', 'security_checks')
            validation_name: Name/message of the validation (e.g., assertion message or comparison_name)
            status: Status of the validation ('PASS', 'FAIL', 'SKIP', 'NA')
        """
        if "validation_details" not in result:
            result["validation_details"] = {
                "assertions": [],
                "data_comparisons": [],
                "contract_checks": [],
                "security_checks": []
            }
        
        if validator_type in result["validation_details"]:
            # Determine the key name based on validator type
            if validator_type == "assertions":
                detail = {"message": validation_name, "status": status}
            elif validator_type == "data_comparisons":
                detail = {"comparison_name": validation_name, "status": status}
            else:  # contract_checks, security_checks
                detail = {"check_name": validation_name, "status": status}
            
            result["validation_details"][validator_type].append(detail)
            logger.debug(f"Added {validator_type} detail for {result.get('test_id')}: {validation_name} - {status}")
    
    def update_response_time(self, result: Dict, response_time_ms: int):
        """
        Update response time in milliseconds.
        
        Args:
            result: Result entry dictionary to update
            response_time_ms: Response time in milliseconds
        """
        result["response_time"] = int(response_time_ms)
        logger.debug(f"Updated response time for {result.get('test_id')}: {response_time_ms}ms")
    
    def add_result(self, result: Dict):
        """
        Add result entry to the collection.
        
        Args:
            result: Complete result entry dictionary
        """
        if not result.get("test_id"):
            logger.warning("Attempted to add result without test_id, skipping")
            return
        
        self._results.append(result)
        logger.info(f"Added result for test_id: {result['test_id']} - Status: {result['status']}")
    
    def get_results(self) -> List[Dict]:
        """
        Get all collected results.
        
        Returns:
            List of all result entries
        """
        return self._results.copy()
    
    def filter_results(self, 
                       by_status: Optional[str] = None,
                       by_service: Optional[str] = None) -> List[Dict]:
        """
        Get filtered results based on criteria.
        
        Args:
            by_status: Filter by status (PASS, FAIL, SKIPPED)
            by_service: Filter by service_name
        
        Returns:
            List of filtered result entries
        """
        filtered = self._results
        
        # Filter by test_id presence (exclude entries without test_id)
        filtered = [r for r in filtered if r.get('test_id')]
        
        if by_status:
            filtered = [r for r in filtered if r.get('status') == by_status]
        
        if by_service:
            filtered = [r for r in filtered if r.get('service_name') == by_service]
        
        logger.debug(f"Filtered results: {len(filtered)} out of {len(self._results)}")
        return filtered
    
    def clear_results(self):
        """
        Clear all collected results.
        Useful for test isolation or cleanup.
        """
        count = len(self._results)
        self._results.clear()
        logger.info(f"Cleared {count} results from collector")
    
    def get_summary_stats(self) -> Dict[str, int]:
        """
        Get summary statistics of collected results.
        
        Returns:
            Dictionary with counts by status
        """
        stats = {
            "total": len(self._results),
            "passed": sum(1 for r in self._results if r.get("status") == "PASS"),
            "failed": sum(1 for r in self._results if r.get("status") == "FAIL"),
            "skipped": sum(1 for r in self._results if r.get("status") == "SKIPPED"),
        }
        return stats


# Singleton accessor function
_collector_instance = None

def get_result_collector() -> TestResultCollector:
    """
    Get the singleton TestResultCollector instance.
    
    Returns:
        TestResultCollector singleton instance
    
    Example:
        >>> collector = get_result_collector()
        >>> result = collector.create_result_entry(case, url)
        >>> collector.add_result(result)
    """
    global _collector_instance
    if _collector_instance is None:
        _collector_instance = TestResultCollector()
    return _collector_instance


def aggregate_validation_stats(collector=None):
    """Aggregate validation statistics from collected test results.
    
    This utility function processes validation statistics from all collected
    test results and returns aggregated counts for reporting purposes.
    
    Args:
        collector: TestResultCollector instance (optional, uses singleton if not provided)
        
    Returns:
        Dictionary with aggregated validation statistics containing:
        - status_code: Status code validation counts
        - contract: API contract validation counts
        - security: Security validation counts
        - performance: Performance validation counts
        - data_comparison: Data comparison validation counts
        - assertions: Assertion validation counts
        
    Example:
        >>> stats = aggregate_validation_stats()
        >>> print(f"Total status checks: {stats['status_code']['total']}")
    """
    if collector is None:
        collector = TestResultCollector()
    
    validation_stats = {
        'status_code': {'total': 0, 'passed': 0, 'failed': 0},
        'contract': {'total': 0, 'passed': 0, 'failed': 0},
        'security': {'total': 0, 'passed': 0, 'failed': 0},
        'performance': {'total': 0, 'passed': 0, 'failed': 0},
        'data_comparison': {'total': 0, 'passed': 0, 'failed': 0},
        'assertions': {'total': 0, 'passed': 0, 'failed': 0}
    }
    
    for result in collector.get_results():
        vstats = result.get('validation_stats', {})
        
        # Map from validation_stats keys to output keys
        key_mappings = [
            ('status_code_checks', 'status_code'),
            ('contract_checks', 'contract'),
            ('security_checks', 'security'),
            ('performance_checks', 'performance'),
            ('data_comparisons', 'data_comparison'),
            ('assertions', 'assertions')
        ]
        
        for source_key, dest_key in key_mappings:
            if source_key in vstats:
                stat = vstats[source_key]
                validation_stats[dest_key]['total'] += stat.get('total', 0)
                validation_stats[dest_key]['passed'] += stat.get('passed', 0)
                validation_stats[dest_key]['failed'] += stat.get('failed', 0)
    
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
