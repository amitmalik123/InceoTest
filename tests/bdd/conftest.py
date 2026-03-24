"""
Shared fixtures for all BDD tests (features, test_runners, steps)
Override test_data to select data based on scenario name from CSV
"""

import pytest


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

    # Try to find matching data by scenario name (strip whitespace from both)
    scenario_name_stripped = scenario_name.strip() if scenario_name else ""
    data = test_data_manager.get_by(scenario=scenario_name_stripped)

    if data:
        print("[TEST DATA] MATCHED in CSV!")
        print(f"[TEST DATA] Role: {data.get('role')}")
        print(f"[TEST DATA] Username: {data.get('username')}")
        print(f"[TEST DATA] Client ID: {data.get('client_id')}")
        print(f"[TEST DATA] Account Number: {data.get('account_number')}")
        print(f"[TEST DATA] Submission_Type: {data.get('Submission_Type')}")
        print(f"{'=' * 60}")
        return data
    else:
        print("[TEST DATA] NOT FOUND - No exact match")
        print("[TEST DATA] Available scenarios in CSV:")
        for row in test_data_manager.get_all():
            print(f"  - Scenario: '{row.get('scenario', 'N/A')}' | Submission_Type: '{row.get('Submission_Type', 'N/A')}'")
        print(f"[TEST DATA] Fallback: using first row with Submission_Type '{test_data_manager[0].get('Submission_Type')}'")
        print(f"{'=' * 60}")
        return test_data_manager[0] if len(test_data_manager) > 0 else {}


# Store test_context instances at module level to ensure persistence across steps in BDD scenarios
_test_context_cache = {}


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
    
    # Cleanup after test completes
    if test_node_id in _test_context_cache:
        print(f"[TEST CONTEXT] Cleanup: Removing context for {test_node_id}")
        del _test_context_cache[test_node_id]
