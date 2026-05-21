"""
Shared fixtures for all BDD tests (features, test_runners, steps)
Override test_data to select data based on scenario name from CSV
"""

import pytest

from fixtures.auth_providers import ensure_sessions


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


@pytest.fixture
def test_context(test_data) -> dict:
    """
    Context to store test data and state across BDD steps.

    Args:
        test_data: Injected from test_data fixture (filtered by scenario name)

    Returns:
        dict: Context with test_data accessible via test_context["test_data"]
    """
    return {"test_data": test_data}


@pytest.fixture(scope="session", autouse=True)
def ensure_auth_sessions():
    """Autouse session fixture that ensures multi-user storage states exist.

    This mirrors Playwright's TypeScript `setup` dependency: it runs once
    before any tests and will refresh sessions only when the runner's
    timestamp indicates expiration.
    """
    try:
        ensure_sessions()
    except Exception as e:
        print(f"[AUTH_SETUP] ensure_sessions failed: {e}")
    yield
