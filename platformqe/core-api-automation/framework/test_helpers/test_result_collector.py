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
            "summary": ""
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
        security: Optional[str] = None
    ):
        """
        Update validation results (contract, custom, security).
        
        Args:
            result: Result entry dictionary to update
            contract: Contract check result (PASS/FAIL)
            custom: Custom validation result (PASS/FAIL)
            security: Security check result (PASS/FAIL)
        """
        if contract is not None:
            result["contract_check"] = contract
        if custom is not None:
            result["custom_validations"] = custom
        if security is not None:
            result["security_checks"] = security
        
        logger.debug(f"Updated validations for {result.get('test_id')}: "
                    f"contract={contract}, custom={custom}, security={security}")
    
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
