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
@then("Verify the Routing Order in database")
def verify_routing_order_in_database(test_context):
    """Verify the Routing Order of specified role(s) in datbase
    
    Accepts one or multiple roles:
    - Single role: Verify the Routing Order in database for Role(s) "Advisor"
    - Multiple roles: Verify the Routing Order in database for Role(s) "Advisor" "Shared Access User"
    
    Uses dnumber and queries trackingcenter database.
    Validates that recipient role matches one of the specified roles.
    """
    logger.info("Verifying Routing Order in database")

    # Get dnumber from test context
    dnumber = test_context.get('d_number', '')

    if not dnumber:
        raise ValueError(
            "Dnumber not found in test_context. "
        )

    logger.info(f"Querying ItemId for dnumber: {dnumber}")

    # Get configured database connection (using SQL Server for trackingcenter DB)
    from utils.database import get_configured_sql_server

    db = get_configured_sql_server(database="CRM")

    try:
        # Connect to database
        db.connect()
        from config.settings import settings
        logger.info(f"Connected to database")

        # Get query from centralized queries file
        from config.settings import settings
        query = settings.database_queries.get("tracking_center", {}).get(
            "itemId_by_dnumber"
        )
        
        if not query:
            raise ValueError(
                "Query not found: tracking_center.itemId_by_dnumber in queries/sql_queries.yaml"
            )

        logger.info(f"Executing query: {query}")
        logger.info(f"Query parameter (dnumber): {dnumber}")
        logger.info(f"Attempting up to 6 retries with exponential backoff...")

        # Use retry logic for itemId query
        # Data may not be immediately available in tracking center database
        try:
            results = None
            def get_itemid():
                nonlocal results
                results = db.execute_query(query, (dnumber,))
                return bool(results)
            
            retry_until_true(
                condition=get_itemid,
                max_attempts=6,
                delay=5.0,
                error_message=f"No ItemId found in database for dnumber: {dnumber}"
            )
        except RetryError as e:
            raise AssertionError(str(e)) from e

        # Extract ItemId from result
        item_id = results[0].get("ItemId")  # Dictionary access

        logger.info(f"✓ ItemId: {item_id} found in database for dnumber: {dnumber}")

        # Step 2: Query DocuSignID using the fetched ItemId
        logger.info(f"Step 2: Querying DocuSignID for ItemId: {item_id} and dnumber: {dnumber}")

        # Get second query from centralized queries file
        query_docusign = settings.database_queries.get("tracking_center", {}).get(
            "docusign_id_by_item_id"
        )
        if not query_docusign:
            raise ValueError(
                "Query not found: tracking_center.docusign_id_by_item_id in queries/sql_queries.yaml"
            )

        logger.info(f"Executing query: {query_docusign}")
        logger.info(f"Query parameter (ItemId): {item_id}")
        logger.info(f"Attempting up to 6 retries with exponential backoff...")

        # Use retry logic for docusign_id query
        # Data may not be immediately available in tracking center database
        try:
            docusign_results = None
            def get_docusignid():
                nonlocal docusign_results
                docusign_results = db.execute_query(query_docusign, (item_id,))
                return bool(docusign_results)
            
            retry_until_true(
                condition=get_docusignid,
                max_attempts=6,
                delay=5.0,
                error_message=f"No DocuSignID found in database for ItemId: {item_id} and dnumber: {dnumber}"
            )
        except RetryError as e:
            raise AssertionError(str(e)) from e

        # Extract DocuSignID from result
        docusign_id = docusign_results[0].get("DocuSignID")  # Dictionary access

        logger.info(f"✓ DocuSignID {docusign_id} found in database for ItemId: {item_id} and dnumber: {dnumber}")

        # Step 3: Query recipient data using the fetched DocuSignID
        # NOTE: Using retry logic since data may not be immediately available in esignaturedata DB
        logger.info(f"Step 3: Querying recipient data for DocuSignID: {docusign_id} (with retry logic)")

        # Get third query from centralized queries file
        query_recipient = settings.database_queries.get("esignature_data", {}).get(
            "recipient_by_envelope_provider_id"
        )
        if not query_recipient:
            raise ValueError(
                "Query not found: esignature_data.recipient_by_envelope_provider_id in queries/sql_queries.yaml"
            )

        logger.info(f"Query: {query_recipient}")
        logger.info(f"Query parameter (DocuSignID): {docusign_id}")
        logger.info(f"Attempting up to 6 retries with exponential backoff (5s → 10s → 20s → 40s → 60s)...")

        # Use retry logic for recipient query
        # Data may not be immediately available due to database replication/async processing
        try:
            recipient_results = None
            def get_recipient():
                nonlocal recipient_results
                recipient_results = db.execute_query(query_recipient, (docusign_id,))
                return bool(recipient_results)
            
            retry_until_true(
                condition=get_recipient,
                max_attempts=6,
                delay=5.0,
                error_message=f"No recipient data found in database for DocuSignID: {docusign_id}"
            )
        except RetryError as e:
            raise AssertionError(str(e)) from e

        logger.info(f"✓ Recipient data found in database for DocuSignID: {docusign_id}, ItemId: {item_id} and Dnumber: {dnumber}")
        
        # Validate routing order for expected roles
        logger.info(f"Validating routing order")

        # Get test data
        test_data = test_context.get("test_data", {})
        expected_roles = test_data.get("Expected_Roles", "")
        expected_routing_orders = test_data.get("Expected_RoutingOrders", "")
        expected_roles_list = [role.strip() for role in expected_roles.split(",")]
        expected_routing_orders_list = [order.strip() for order in expected_routing_orders.split(",")]
        role_routing_map = dict(zip(expected_roles_list, expected_routing_orders_list))
        logger.info(f"Expected Roles and Routing Orders: {role_routing_map}")
        for row in recipient_results:
            role = row.get("Role")
            routing_order = str(row.get("RoutingOrder"))
            logger.info(f"  Recipient Role: {role}, Routing Order: {routing_order}")

            if role in role_routing_map:
                expected_order = role_routing_map[role]
                assert (
                    routing_order == expected_order
                ), f"Routing Order mismatch for Role '{role}': expected {expected_order}, got {routing_order}"
                logger.info(f"  ✓ Routing Order for Role '{role}' matches expected value: {expected_order}")
            else:
                raise AssertionError(
                    f"Unexpected role '{role}' found in database recipient records. "
                    f"Expected roles: {list(role_routing_map.keys())}"
                )

        logger.info("\n✓ Routing Order verification successful")

    except Exception as e:
        logger.error(f"Routing Order verification failed: {e}")
        raise
    finally:
        try:
            db.close()
            logger.info("Database connection closed")
        except:
            pass
