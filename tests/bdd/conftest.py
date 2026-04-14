"""
Shared fixtures for all BDD tests (features, test_runners, steps)
Override test_data to select data based on scenario name from CSV
"""

import pytest
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@pytest.fixture
def test_data(test_data_manager, request) -> dict:
    """
    Select test data based on scenario name matching CSV 'scenario' column.

    Each scenario gets its own data row by matching scenario name exactly.
    This runs BEFORE login, so each scenario uses correct credentials.

    CSV Format:
        scenario,role,username,password,...
        Successfully login and navigate to Account List,non-ira,user1,...
        Successfully complete Add ACH flow,ira,user2,...

    Args:
        test_data_manager: Session-scoped test data manager
        request: Pytest request object with scenario info

    Returns:
        dict: Test data row for this scenario
    """
    # Get actual scenario name from pytest-bdd scenario object
    scenario_name = None

    # pytest-bdd stores the scenario in the test function
    if (
        hasattr(request, "node")
        and hasattr(request.node, "obj")
        and hasattr(request.node.obj, "__scenario__")
    ):
        scenario_name = request.node.obj.__scenario__.name

    # Fallback: extract from test name
    if not scenario_name:
        scenario_name = request.node.name.replace("test_", "").replace("_", " ").title()

    print(f"\n{'=' * 60}")
    print(f"[TEST DATA] Scenario: '{scenario_name}'")

    # Try to find matching data by scenario name
    data = test_data_manager.get_by(scenario=scenario_name)

    if data:
        print("[TEST DATA] MATCHED in CSV!")
        print(f"[TEST DATA] Role: {data.get('role')}")
        print(f"[TEST DATA] Username: {data.get('username')}")
        print(f"[TEST DATA] Client ID: {data.get('client_id')}")
        print(f"[TEST DATA] Account Number: {data.get('account_number')}")
        print(f"{'=' * 60}")
        return data
    else:
        print("[TEST DATA] NOT FOUND - No exact match")
        print("[TEST DATA] Available in CSV:")
        for row in test_data_manager.get_all():
            print(f"  - '{row.get('scenario', 'N/A')}'")
        print("[TEST DATA] Fallback: using first row")
        print(f"{'=' * 60}")
        return test_data_manager[0] if len(test_data_manager) > 0 else {}


# Store test_context instances at module level to ensure persistence across steps in BDD scenarios
_test_context_cache = {}

# Store D_Numbers per test_node_id for parallel-safe logging (keyed by test_node_id)
# This is safe for parallel execution because each test has a unique node_id
_test_d_numbers = {}


@pytest.fixture
def test_context(test_data, request) -> dict:
    """
    Context to store test data and state across BDD steps.
    
    IMPORTANT: This fixture MUST persist across ALL steps in a single BDD scenario.
    Without this, steps cannot share data (e.g., database query results).
    
    Solution: Cache instances by test node ID so all steps in same scenario share context.

    Args:
        test_data: Injected from test_data fixture (filtered by scenario name)
        request: Pytest request object with node info

    Returns:
        dict: Context with test_data accessible via test_context["test_data"]
              and allows steps to store/retrieve shared state via test_context dict
    """
    # Use test node ID as cache key so all steps in same scenario share context
    test_node_id = request.node.nodeid
    
    # Create context only once per test, reuse for all steps
    if test_node_id not in _test_context_cache:
        print(f"\n[TEST CONTEXT] Creating new context for: {test_node_id}")
        _test_context_cache[test_node_id] = {"test_data": test_data}
    else:
        print(f"\n[TEST CONTEXT] Reusing existing context for: {test_node_id}")
    
    context = _test_context_cache[test_node_id]
    
    # Log current state
    print(f"[TEST CONTEXT] Available keys: {list(context.keys())}")
    for key in context.keys():
        if key != "test_data":  # Don't log large test_data dict
            value = context[key]
            if isinstance(value, list) and len(value) > 0:
                print(f"  - {key}: {len(value)} item(s)")
            else:
                print(f"  - {key}: {value}")
    
    yield context
    
    # Cleanup after test completes - LOG D_NUMBER BEFORE CLEANUP
    if test_node_id in _test_context_cache:
        # Extract D_Number before deleting context
        d_number = context.get("d_number", "N/A")
        
        # Store D_Number in per-test dictionary (thread-safe for parallel execution)
        _test_d_numbers[test_node_id] = d_number
        
        logger.info(f"\n{'=' * 60}")
        logger.info(f"D_Number generated - {d_number}")
        logger.info(f"{'=' * 60}")
        
        # Also print to stdout so it's definitely visible
        print(f"\n{'=' * 60}")
        print(f"D_Number generated - {d_number}")
        print(f"{'=' * 60}\n")
        
        logger.info(f"[TEST CONTEXT] Cleanup: Removing context for {test_node_id}")
        del _test_context_cache[test_node_id]


def pytest_runtest_logreport(report):
    """
    Hook that runs after each test result is logged.
    Logs the D_Number that was generated/used in the test.
    This is PARALLEL-SAFE because it uses test_node_id as the key.
    
    This hook works with parallel execution (pytest-xdist):
    - Each test has a unique test_node_id
    - D_Numbers are stored in _test_d_numbers dict keyed by test_node_id
    - Multiple workers can run simultaneously without interference
    """
    # Log when test is done (after all steps, after teardown)
    if report.when == "teardown":
        try:
            # Get test node ID - this is unique per test even in parallel execution
            test_node_id = report.nodeid
            
            # Look up D_Number from the per-test dictionary
            if test_node_id in _test_d_numbers:
                d_number = _test_d_numbers[test_node_id]
                
                logger.critical(f"D_Number generated - {d_number}")

                # Also print to ensure it's captured
                print(f"\n{'=' * 70}")
                print(f"D_Number generated - {d_number}")
                print(f"{'=' * 70}\n")
                
                # Clean up this test's entry
                del _test_d_numbers[test_node_id]
        except Exception as e:
            # Don't fail if logging fails
            logger.warning(f"Error logging D_Number in hook: {e}")


def pytest_sessionfinish(session):
    """
    Hook that runs at the end of the entire test session.
    Cleans up any remaining D_Numbers from _test_d_numbers dict.
    This is a safety cleanup in case some tests crashed before reporting.
    """
    global _test_d_numbers
    if _test_d_numbers:
        logger.info(f"Session cleanup: Removing {len(_test_d_numbers)} leftover D_Number entries")
        _test_d_numbers.clear()


def pytest_runtest_makereport(item, call):
    """
    Hook that processes test results and handles soft assertion warnings.
    
    This hook:
    - Catches SoftAssertionWarning exceptions
    - Marks test with warning status (yellow/orange indicator) in Allure
    - Prevents test from being marked as failed
    - Keeps test status as PASSED but with warning badge
    
    This is called for each test at different phases: setup, call, teardown
    """
    from utils.soft_assertions_enhanced import SoftAssertionWarning
    import allure
    
    # Only process during the test call phase (when test code runs)
    if call.when == "call":
        # Check if the test has a SoftAssertionWarning (soft assertion failure)
        if call.excinfo and isinstance(call.excinfo.value, SoftAssertionWarning):
            # Mark as passed despite the warning
            logger.warning(f"Test {item.nodeid} has soft assertion warnings - marking with yellow indicator")
            
            # Add Allure label for visual indication
            allure.dynamic.label("severity", "warning")
            allure.dynamic.label("status_badge", "⚠️ WARNINGS")
            
            # Suppress the exception so test doesn't fail
            call.excinfo = None


