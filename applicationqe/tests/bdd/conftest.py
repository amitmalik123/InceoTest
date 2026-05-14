"""
Shared fixtures for all BDD tests (features, test_runners, steps)
Override test_data to select data from Excel examples first, then generic test data lookup.
"""

import pytest


def _get_scenario_name(request) -> str:
    """Get the scenario name from a pytest-bdd request."""
    scenario_name = None

    if (
        hasattr(request, "node")
        and hasattr(request.node, "obj")
        and hasattr(request.node.obj, "__scenario__")
    ):
        scenario_name = request.node.obj.__scenario__.name

    if not scenario_name:
        scenario_name = request.node.name.replace("test_", "").replace("_", " ").title()

    return scenario_name


def _get_example_row_data(request, excel_data_manager) -> dict | None:
    """Resolve one Excel row from Scenario Outline example parameters."""
    callspec = getattr(request.node, "callspec", None)
    example_params = getattr(callspec, "params", {}) or {}

    sheet_name = example_params.get("SheetName") or example_params.get("sheet_name")
    row_number = example_params.get("RowNumber") or example_params.get("row_number")

    if sheet_name in (None, "") or row_number in (None, ""):
        return None

    row_number = int(row_number)
    if row_number < 2:
        raise ValueError(
            f"Invalid RowNumber '{row_number}' for sheet '{sheet_name}'. "
            "Use Excel row numbers starting at 2 (first data row)."
        )

    row_data = dict(excel_data_manager.get_row(str(sheet_name), row_number - 2))
    row_data.setdefault("SheetName", str(sheet_name))
    row_data.setdefault("RowNumber", row_number)
    return row_data


@pytest.fixture
def test_data(excel_data_manager, test_data_manager, request) -> dict:
    """
    Select test data for BDD scenarios.

    Priority:
    1. SheetName + RowNumber from Scenario Outline Examples
    2. Generic row lookup by scenario name from the loaded test data manager

    Args:
        excel_data_manager: Session-scoped Excel manager
        test_data_manager: Session-scoped test data manager
        request: Pytest request object with scenario info

    Returns:
        dict: Test data row for this scenario
    """
    scenario_name = _get_scenario_name(request)

    print(f"\n{'=' * 60}")
    print(f"[TEST DATA] Scenario: '{scenario_name}'")

    row_data = _get_example_row_data(request, excel_data_manager)
    if row_data:
        print("[TEST DATA] MATCHED from Excel Examples")
        print(f"[TEST DATA] SheetName: {row_data.get('SheetName')}")
        print(f"[TEST DATA] RowNumber: {row_data.get('RowNumber')}")
        print(f"[TEST DATA] Username: {row_data.get('username') or row_data.get('UserName')}")
        print(f"{'=' * 60}")
        return row_data

    data = test_data_manager.get_by(scenario=scenario_name) or test_data_manager.get_by(
        test_scenario=scenario_name
    )

    if data:
        print("[TEST DATA] MATCHED by scenario lookup")
        print(f"[TEST DATA] Role: {data.get('role')}")
        print(f"[TEST DATA] Username: {data.get('username') or data.get('UserName')}")
        print(f"[TEST DATA] Client ID: {data.get('client_id')}")
        print(f"{'=' * 60}")
        return data

    print("[TEST DATA] NOT FOUND - No matching Excel example or scenario row")
    print("[TEST DATA] Fallback: using first available test data row")
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
    context = {"test_data": test_data}
    if test_data:
        context["excel_row_data"] = dict(test_data)
    return context
