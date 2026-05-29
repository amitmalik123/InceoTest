"""
SMI Database & Data Validations — Model Management

Migrated from tests/bdd/steps/database_steps.py and data_steps.py on branch
application/ModelManagement_SMI.
"""
from typing import Optional

from pytest_bdd import given, parsers, then, when

from utils.logger import setup_logger

logger = setup_logger(__name__)


# ===========================================================================
# Data steps (from data_steps.py)
# ===========================================================================


@when(parsers.parse('I load test data from excel sheet "{sheet_name}"'))
def load_data_from_excel(test_context, sheet_name: str, excel_data_manager):
    """Load test data from a specific Excel sheet into test_context."""
    data = excel_data_manager.get_sheet(sheet_name)
    logger.info(f"Loading sheet '{sheet_name}': {len(data)} rows")
    columns = list(data[0].keys()) if data else []
    logger.info(f"Columns: {columns}")
    for idx, row in enumerate(data[:3], 1):
        logger.info(f"Row {idx}: {row}")

    if "excel_data" not in test_context:
        test_context["excel_data"] = {}
    test_context["excel_data"][sheet_name] = data


@given(parsers.parse('I am using test data for scenario "{scenario_name}"'))
def use_test_data_for_scenario(test_context, test_data_manager, scenario_name):
    """Load test data by scenario name."""
    user_data = test_data_manager.get_by(test_scenario=scenario_name)
    if not user_data:
        raise ValueError(
            f"No test data found for scenario '{scenario_name}'. "
            f"Available scenarios: {test_data_manager.get_scenarios()}"
        )
    test_context["current_user_data"] = user_data
    logger.info(f"Using test data for scenario: {scenario_name}")


@given(parsers.parse('I am using test data for user type "{user_type}"'))
def use_test_data_for_user_type(test_context, test_data_manager, user_type):
    """Load test data by user type."""
    user_data = test_data_manager.get_by(user_type=user_type)
    if not user_data:
        raise ValueError(
            f"No test data found for user type '{user_type}'. "
            f"Available user types: {test_data_manager.get_user_types()}"
        )
    test_context["current_user_data"] = user_data
    logger.info(f"Using test data for user type: {user_type}")


# ===========================================================================
# Database steps (from database_steps.py)
# ===========================================================================


@when("I verify the database using query from <query_category>.<query_name>")
def verify_database_with_query(
    test_context, query_category: str, query_name: str, db_manager
):
    """Generic database verification step."""
    from utils.database import execute_query_from_yaml

    logger.info(f"Verifying database: {query_category}.{query_name}")
    results = execute_query_from_yaml(
        query_category=query_category,
        query_name=query_name,
        db_manager=db_manager,
    )
    query_key = f"{query_category}.{query_name}"
    if "db_results" not in test_context:
        test_context["db_results"] = {}
    test_context["db_results"][query_key] = results or []

    if results:
        logger.info(f"Found {len(results)} records for '{query_key}'")
    else:
        logger.warning(f"No records found for '{query_key}'")


@then("the database should contain records")
def verify_database_contains_records(test_context):
    """Verify that the last database query returned records."""
    _assert_records(test_context)


@then("the database should contain at least {count:d} records")
def verify_database_contains_minimum_records(test_context, count: int):
    """Verify the last query returned at least N records."""
    _assert_minimum_records(test_context, count)


def _assert_records(test_context, query_key: Optional[str] = None):
    """Verify records exist for a given query key or the last query."""
    if query_key:
        assert "db_results" in test_context, "No database queries have been executed"
        assert query_key in test_context["db_results"], (
            f"Query '{query_key}' was not executed. "
            f"Available: {list(test_context['db_results'].keys())}"
        )
        results = test_context["db_results"][query_key]
    else:
        assert "database_results" in test_context, "Database query was not executed or failed"
        results = test_context["database_results"]
        query_key = test_context.get("last_query", "Unknown")

    assert results is not None, f"Database results are None for '{query_key}'"
    assert len(results) > 0, f"No records found for query: {query_key}"
    logger.info(f"Verification passed: {len(results)} records for '{query_key}'")


def _assert_minimum_records(test_context, count: int, query_key: Optional[str] = None):
    """Verify minimum record count."""
    if query_key:
        assert "db_results" in test_context, "No database queries have been executed"
        results = test_context["db_results"][query_key]
    else:
        assert "database_results" in test_context, "Database query was not executed or failed"
        results = test_context["database_results"]
        query_key = test_context.get("last_query", "Unknown")

    assert results is not None, f"Database results are None for '{query_key}'"
    assert len(results) >= count, (
        f"Expected at least {count} records for '{query_key}', but found {len(results)}"
    )
    logger.info(f"Verification passed: {len(results)} records for '{query_key}' (expected >= {count})")
