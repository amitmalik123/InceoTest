"""
Common Database Step Definitions

These steps are thin wrappers around database utility functions.
All business logic is in utils/database.py for reusability.
"""

from typing import Optional

from pytest_bdd import then, when

from utils.allure_logger import get_allure_logger
from utils.database import execute_query_from_yaml

logger = get_allure_logger(__name__)


@when("I verify the database using query from <query_category>.<query_name>")
def verify_database_with_query(test_context, query_category: str, query_name: str, db_manager):
    """
    Generic database verification step.
    Automatically selects and connects to correct database based on YAML.
    Only connects when needed (lazy initialization).

    Usage in feature files:
        When I verify the database using query from "transfer.transfer_audit"
        When I verify the database using query from "crm.retirement_billing_client"
    """
    logger.info(f"Verifying database: {query_category}.{query_name}")

    # Execute query - db_manager reuses connection, switches database via USE
    results = execute_query_from_yaml(
        query_category=query_category,
        query_name=query_name,
        db_manager=db_manager,
    )

    # Build the query key
    query_key = f"{query_category}.{query_name}"

    # Initialize db_results dict if first call
    if "db_results" not in test_context:
        test_context["db_results"] = {}

    # Store results under the query key
    test_context["db_results"][query_key] = results or []

    if results:
        logger.info(f"Found {len(results)} records for '{query_key}'")
        for idx, row in enumerate(results[:5], 1):
            logger.info(f"Record {idx}: {row}")
    else:
        logger.warning(f"No records found for '{query_key}'")


@when("I verify the retirement billing client in database")
def verify_retirement_billing_client_in_database(test_context, db_manager):
    """Verify the retirement billing client in Azure SQL Database"""
    verify_database_with_query(test_context, "crm", "retirement_billing_client", db_manager)


@when("I verify the am billing accounts data from database")
def verify_am_billing_accounts_data_from_database(test_context, db_manager):
    """Verify the AM billing accounts data in SQL Server database"""
    verify_database_with_query(test_context, "am_billing", "account_details", db_manager)


@when("I verify the transfer status in database")
def verify_transfer_status_in_database(test_context, db_manager):
    """Verify transfer status in database"""
    verify_database_with_query(test_context, "transfer", "transfer_audit", db_manager)


@when("I verify the account distribution in database")
def verify_account_distribution_in_database(test_context, db_manager):
    """Verify account distribution in database"""
    verify_database_with_query(test_context, "account_distributions", "Amount_Lookup", db_manager)


@when("I verify the account details in database")
def verify_account_in_database(test_context, db_manager):
    """Verify account details in database"""
    verify_database_with_query(test_context, "account", "account_details", db_manager)


@then("the database should contain records")
def verify_database_contains_records(test_context):
    """Verify that the last database query returned records"""
    _assert_records(test_context)


def _assert_records(test_context, query_key: Optional[str] = None):
    """Internal helper to verify records exist for a given query key or the last query.

    Args:
        test_context: Test context dict.
        query_key: Optional query key like 'transfer.transfer_audit'.
                   If None, checks the last executed query.
    """
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


@then("the transfer status should be in the database")
def verify_transfer_status_exists(test_context):
    """Verify that transfer status records exist in database"""
    verify_database_contains_records(test_context)


@then("the database should contain at least {count:d} records")
def verify_database_contains_minimum_records(test_context, count: int):
    """Verify the last query returned at least N records"""
    _assert_minimum_records(test_context, count)


def _assert_minimum_records(test_context, count: int, query_key: Optional[str] = None):
    """Internal helper to verify minimum record count.

    Args:
        test_context: Test context dict.
        count: Minimum number of records expected.
        query_key: Optional query key. If None, checks the last query.
    """
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
    assert (
        len(results) >= count
    ), f"Expected at least {count} records for '{query_key}', but found {len(results)}"

    logger.info(
        f"Verification passed: {len(results)} records for '{query_key}' (expected >= {count})"
    )

    # Specific query result (never overwritten)


# transfer_rows = test_context["db_results"]["transfer.transfer_audit"]
# status = transfer_rows[0]["Status"]

# Last query result (legacy shortcut)
# last = test_context["database_results"]
