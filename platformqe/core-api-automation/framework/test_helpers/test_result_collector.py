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
            # Additional fields for test_results_summary.json
            "workflow_mode": case.get("workflow_mode", ""),
            "protocol": protocol,
            "test_summary": case.get("test_summary", ""),
            "test_scenario": case.get("test_scenario", ""),
            "start_time": None,  # Will be set when test starts
            "end_time": None,  # Will be set when test ends
            # Detailed validation statistics
            "validation_stats": {
                "status_code_checks": {"total": 0, "passed": 0, "failed": 0},
                "assertions": {"total": 0, "passed": 0, "failed": 0},
                "data_comparisons": {"total": 0, "passed": 0, "failed": 0},
                "contract_checks": {"total": 0, "passed": 0, "failed": 0},
                "security_checks": {"total": 0, "passed": 0, "failed": 0},
                "performance_checks": {"total": 0, "passed": 0, "failed": 0},
                "db_row_checks": {"total": 0, "passed": 0, "failed": 0},
                "db_column_checks": {"total": 0, "passed": 0, "failed": 0},
                "db_count_checks": {"total": 0, "passed": 0, "failed": 0},
                "db_missing_source": {"total": 0, "passed": 0, "failed": 0},
                "db_missing_target": {"total": 0, "passed": 0, "failed": 0}
            },
            # Individual validation details for UI display
            "validation_details": {
                "assertions": [],  # List of {"message": str, "status": "PASS"|"FAIL"|"SKIP"|"NA"}
                "data_comparisons": [],  # List of {"comparison_name": str, "status": "PASS"|"FAIL"|"SKIP"|"NA"}
                "contract_checks": [],  # List of {"check_name": str, "status": "PASS"|"FAIL"|"SKIP"|"NA"}
                "security_checks": [],  # List of {"check_name": str, "status": "PASS"|"FAIL"|"SKIP"|"NA"}
                "performance_checks": [],  # List of {"check_name": str, "status": "PASS"|"FAIL"|"SKIP"|"NA"}
                "db_row_checks": [],
                "db_column_checks": [],
                "db_count_checks": [],
                "db_missing_source": [],
                "db_missing_target": []
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
                "security_checks": {"total": 0, "passed": 0, "failed": 0},
                "db_row_checks": {"total": 0, "passed": 0, "failed": 0},
                "db_column_checks": {"total": 0, "passed": 0, "failed": 0},
                "db_count_checks": {"total": 0, "passed": 0, "failed": 0},
                "db_missing_source": {"total": 0, "passed": 0, "failed": 0},
                "db_missing_target": {"total": 0, "passed": 0, "failed": 0}
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
                "security_checks": [],
                "db_row_checks": [],
                "db_column_checks": [],
                "db_count_checks": [],
                "db_missing_source": [],
                "db_missing_target": []
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
        result["duration"] = int(response_time_ms)  # Set duration same as response_time
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
    
    DEPRECATED: For in-memory usage during test execution only.
    For post-execution/reporter usage, use framework.loaders.test_result_loader.aggregate_validation_stats() instead.
    
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
        - row_match: Row-level comparison counts
        - column_match: Column-level comparison counts
        - count_check: Source/target count validation counts
        - missing_source: Missing-source row counts
        - missing_target: Missing-target row counts
        
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
        'assertions': {'total': 0, 'passed': 0, 'failed': 0},
        'row_match': {'total': 0, 'passed': 0, 'failed': 0},
        'column_match': {'total': 0, 'passed': 0, 'failed': 0},
        'count_check': {'total': 0, 'passed': 0, 'failed': 0},
        'missing_source': {'total': 0, 'passed': 0, 'failed': 0},
        'missing_target': {'total': 0, 'passed': 0, 'failed': 0}
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
            ('assertions', 'assertions'),
            ('db_row_checks', 'row_match'),
            ('db_column_checks', 'column_match'),
            ('db_count_checks', 'count_check'),
            ('db_missing_source', 'missing_source'),
            ('db_missing_target', 'missing_target')
        ]
        
        for source_key, dest_key in key_mappings:
            if source_key in vstats:
                stat = vstats[source_key]
                validation_stats[dest_key]['total'] += stat.get('total', 0)
                validation_stats[dest_key]['passed'] += stat.get('passed', 0)
                validation_stats[dest_key]['failed'] += stat.get('failed', 0)
    
    return validation_stats

# HTML generation functions moved to framework.loaders.test_result_loader
# Import from there for centralized usage:
#   from framework.loaders.test_result_loader import (
#       generate_test_summary_table,
#       generate_validation_summary_table
#   )
