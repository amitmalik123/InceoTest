"""
PortfolioReporting runner-local fixtures.

These fixtures preserve the original BDD Scenario Outline behavior after
moving files out of tests/bdd/.
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

    normalized = {str(k).strip().lower().replace(" ", ""): v for k, v in example_params.items()}
    sheet_name = normalized.get("sheetname") or normalized.get("sheet_name")
    row_number = normalized.get("rownumber") or normalized.get("row_number")

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
    2. Generic row lookup by scenario name from test_data_manager
    """
    scenario_name = _get_scenario_name(request)

    row_data = _get_example_row_data(request, excel_data_manager)
    if row_data:
        return row_data

    data = test_data_manager.get_by(scenario=scenario_name) or test_data_manager.get_by(
        test_scenario=scenario_name
    )

    if data:
        return data

    return test_data_manager[0] if len(test_data_manager) > 0 else {}


@pytest.fixture
def test_context(test_data) -> dict:
    """Context to store test data and state across BDD steps."""
    context = {"test_data": test_data}
    if test_data:
        context["excel_row_data"] = dict(test_data)
    return context
