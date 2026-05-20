"""
Database Step Definitions

These steps handle database queries and validation for BDD scenarios.
"""

import allure
from pytest_bdd import parsers, then, when

from utils.stp.constants.constants import Constants
from utils.database import get_azure_db_connection, get_configured_azure_db, get_configured_ewm_db
from utils.settings import settings


from utils.allure_logger import get_allure_logger
from utils.database import execute_query_from_yaml

logger = get_allure_logger(__name__)


@then(parsers.parse('User should execute azure db query with item number and verify note "{expected_note}" for AINS where stepID is "{step_id}"'))
def execute_azure_db_query_with_item_number_for_ains(test_context, expected_note, step_id):
  
    with allure.step(f"Execute Azure DB query and verify note for stepID {step_id}"):
       
        item_number = test_context.get('item_number')

        query_template = settings.database_queries.get('instance_audit', {}).get('audit_by_reference_and_step')
        if not query_template:
            raise ValueError("Query not found: instance_audit.audit_by_reference_and_step in queries/sql_queries.yaml")
        
        # Format query with actual values
        query = query_template.format(item_number=item_number, step_id=step_id)
        
        logger.info(f"Executing DB query for stepID: {step_id}")
       
        try:
            with get_azure_db_connection() as db:
                results = db.execute_query(query)
            
                first_row = results[0]
            
                columns = [column[0] for column in db.cursor.description]
                logger.info(f"Available columns: {columns}")
            
                notes_index = columns.index('Notes')
                actual_note = first_row[notes_index]
                
                logger.info(f"Actual Note from DB: {actual_note}")
                
                assert expected_note == actual_note, (
                    f"Instance Audit note for stepID '{step_id}' mismatch. "
                    f"Expected: '{expected_note}', Actual: '{actual_note}'"
                )
                allure.attach(
                    f"Query: {query}\n\nNote: {actual_note}",
                    name=f"DB Query Results - StepID {step_id}",
                    attachment_type=allure.attachment_type.TEXT
                )
                
        except Exception as e:
            logger.error(f"Error executing Azure DB query: {str(e)}")
            allure.attach(
                f"Error: {str(e)}\nQuery: {query}",
                name="DB Query Error",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@then(parsers.parse('User should execute azure db query and fetch the Instance Audit table notes and validate them for SLOA "{sloa_type}" and role as "{role}"'))
def execute_azure_db_query_and_validate_instance_audit_notes(test_context, sloa_type: str, role: str):
    """Execute Azure DB query to fetch and validate Instance Audit table notes"""
    with allure.step(f"Validate Instance Audit notes for SLOA {sloa_type} and role {role}"):
        logger.info(f"Validating Instance Audit notes for SLOA: {sloa_type}, Role: {role}")
        
        item_number = test_context.get('item_number')
        initial_role = test_context.get('initial_role', role)
        
        logger.info(f"Item Number: {item_number}")
        logger.info(f"Initial Role: {initial_role}, Current Role: {role}")
        
        try:
            with get_azure_db_connection() as db:
                query1_template = settings.database_queries.get('instance_audit', {}).get('external_reference_by_id')
                if not query1_template:
                    raise ValueError("Query not found: instance_audit.external_reference_by_id in queries/sql_queries.yaml")
                query1 = query1_template.format(item_number=item_number)
                logger.info(f"Querying InstanceExternalReference for ReferenceID: {item_number}")
                
                instance_id = db.execute_query_and_get_first_value(query1, "InstanceID")
                logger.info(f"InstanceID: {instance_id}")
                
                query2_template = settings.database_queries.get('instance_audit', {}).get('audit_by_instance_id')
                if not query2_template:
                    raise ValueError("Query not found: instance_audit.audit_by_instance_id in queries/sql_queries.yaml")
                query2 = query2_template.format(instance_id=instance_id)
                logger.info(f"Querying InstanceAudit for InstanceID: {instance_id}")
                
                notes_list_db = db.execute_select_query_and_get_string_list(query2, "Notes")
                notes_size = len(notes_list_db)
                logger.info(f"Retrieved {notes_size} notes from InstanceAudit table")
                
                query3_template = settings.database_queries.get('instance_audit', {}).get('instance_status_by_id')
                if not query3_template:
                    raise ValueError("Query not found: instance_audit.instance_status_by_id in queries/sql_queries.yaml")
                query3 = query3_template.format(instance_id=instance_id)
                logger.info(f"Querying Instance table for InstanceID: {instance_id}")
                
                status = db.execute_query_and_get_first_value(query3, "Status")
                logger.info(f"Instance Status: {status}")
                
                expected_notes = []
                expected_status = ""
                
                if sloa_type == "Esign":
                    if "Admin" in role and "Admin" in initial_role:
                        expected_notes = Constants.notes_sloa_esign_admin()
                        expected_status = "In Process"
                    elif "Advisor" in role and "Admin" in initial_role:
                        expected_notes = Constants.notes_sloa_esign_advisor_via_admin()
                        expected_status = "Success"
                    else:
                        expected_notes = Constants.notes_sloa_esign()
                        expected_status = "Success"
                        
                elif sloa_type == "Print":
                    expected_notes = Constants.notes_sloa_print()
                    
                elif sloa_type == "NoEsign":
                    if "Admin" in role and "Admin" in initial_role:
                        expected_notes = Constants.notes_sloa_no_esign_admin()
                        expected_status = "In Process"
                    elif "Advisor" in role and "Admin" in initial_role:
                        expected_notes = Constants.notes_sloa_no_esign_advisor_via_admin()
                        expected_status = "Success"
                    else:
                        expected_notes = Constants.notes_sloa_no_esign()
                        expected_status = "Success"
                
                logger.info(f"\nValidating {notes_size} notes against expected {len(expected_notes)} notes")
                for i in range(notes_size):
                    actual_note = notes_list_db[i]
                    expected_note = expected_notes[i] if i < len(expected_notes) else "N/A"
                    
                    if actual_note != expected_note:
                        logger.error(f"\n{'='*80}")
                        logger.error(f"INSTANCE AUDIT NOTES MISMATCH at index {i}")
                        logger.error(f"{'='*80}")
                        logger.error(f"\nExpected Notes ({len(expected_notes)} total):")
                        for idx, note in enumerate(expected_notes):
                            logger.error(f" [{idx}] {note}")
                        
                        logger.error(f"\nActual Notes from DB ({notes_size} total):")
                        for idx, note in enumerate(notes_list_db):
                            logger.error(f" [{idx}] {note}")
                        
                        logger.error(f"\nSQL Query Executed:")
                        logger.error(f" Query 2: SELECT * FROM InstanceAudit WHERE InstanceID = ({instance_id}) ORDER BY CreatedDate")
                        
                        logger.error(f"\nMismatch Details:")
                        logger.error(f" Index: {i}")
                        logger.error(f" Expected: '{expected_note}'")
                        logger.error(f" Actual: '{actual_note}'")
                        logger.error(f"{'='*80}\n")
                    
                    assert actual_note == expected_note, (
                        f"Instance Note mismatch at index {i}. "
                        f"Expected: '{expected_note}', Actual: '{actual_note}'"
                    )
                    logger.info(f"The Instance Note in DB is--> {actual_note}")
                
                if expected_status:
                    assert status == expected_status, (
                        f"Status mismatch. Expected: '{expected_status}', Actual: '{status}'"
                    )
                    logger.info(f"The Status is --> {status}")
                
                notes_text = "\n".join([f"{i+1}. {note}" for i, note in enumerate(notes_list_db)])
                allure.attach(
                    f"InstanceID: {instance_id}\nStatus: {status}\n\nNotes:\n{notes_text}",
                    name=f"Instance Audit Validation - {sloa_type} {role}",
                    attachment_type=allure.attachment_type.TEXT
                )
                
        except Exception as e:
            logger.error(f"Error executing Azure DB query for Instance Audit: {str(e)}")
            allure.attach(
                f"Error: {str(e)}\nItem Number: {item_number}\nSLOA Type: {sloa_type}\nRole: {role}",
                name="DB Query Error",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
"""
Common Database Step Definitions for reusable database verification.
"""


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

    # Execute query - db_manager provides connections lazily (only when accessed)
    results = execute_query_from_yaml(
        query_category=query_category,
        query_name=query_name,
        azure_db=db_manager.azure_db,
        sql_server_db=db_manager.sql_server_db,
    )

    # Store results in test context
    if results:
        logger.info(f"Found {len(results)} records")
        test_context["database_results"] = results
        test_context["last_query"] = f"{query_category}.{query_name}"

        # Log first 5 records for verification
        for idx, row in enumerate(results[:5], 1):
            logger.info(f"Record {idx}: Status={row.status if hasattr(row, 'status') else 'N/A'}")
    else:
        logger.warning("No records found in database")
        test_context["database_results"] = []
        test_context["last_query"] = f"{query_category}.{query_name}"


@when("I verify the Roth Conversion status in database")
def verify_roth_conversion_in_database(test_context, db_manager):
    """Verify the Roth Conversion status in Azure SQL Database"""
    verify_database_with_query(test_context, "transfer", "transfer_audit", db_manager)


@when("I verify the transfer status in database")
def verify_transfer_status_in_database(test_context, db_manager):
    """Verify transfer status in database"""
    verify_database_with_query(test_context, "transfer", "transfer_audit", db_manager)


@when("I verify the account details in database")
def verify_account_in_database(test_context, db_manager):
    """Verify account details in database"""
    verify_database_with_query(test_context, "account", "account_details", db_manager)


@then("the database should contain records")
def verify_database_contains_records(test_context):
    """Verify that database query returned records"""
    logger.info("Verifying database contains records")

    assert "database_results" in test_context, "Database query was not executed or failed"

    results = test_context["database_results"]
    assert results is not None, "Database results are None"
    assert (
        len(results) > 0
    ), f"No records found in database for query: {test_context.get('last_query', 'Unknown')}"

    logger.info(f"Database verification successful: {len(results)} records found")


@then("the transfer status should be in the database")
def verify_transfer_status_exists(test_context):
    """Verify that transfer status records exist in database"""
    verify_database_contains_records(test_context)


@then("the database should contain at least {count:d} records")
def verify_database_contains_minimum_records(test_context, count: int):
    """Verify database contains at least N records"""
    logger.info(f"Verifying database contains at least {count} records")

    assert "database_results" in test_context, "Database query was not executed or failed"

    results = test_context["database_results"]
    assert results is not None, "Database results are None"
    assert len(results) >= count, f"Expected at least {count} records, but found {len(results)}"

    logger.info(
        f"Database verification successful: {len(results)} records found (expected >= {count})"
    )
    allure.attach(
        f"Records found: {len(results)} (expected >= {count})",
        name="Database Verification Result",
        attachment_type=allure.attachment_type.TEXT,
    )


@then(parsers.parse('User should execute azure db query with item number and verify note "{expected_note}" for CancelAIP where stepID is "{step_id}"'))
def execute_azure_db_query_with_item_number_for_cancel_aip(test_context: dict, expected_note: str, step_id: str):
    """Execute Azure DB query and verify note for Cancel AIP"""
    with allure.step(f"Execute Azure DB query and verify note for CancelAIP stepID {step_id}"):
        logger.info(f"Executing DB query for CancelAIP with stepID: {step_id}")
        
        item_number = test_context.get('item_number')
        if not item_number:
            raise ValueError("item_number not found in test_context")
        
        logger.info(f"Item Number: {item_number}")
        
        # Get query from centralized queries file
        query_template = settings.database_queries.get('instance_audit', {}).get('audit_by_reference_and_step')
        if not query_template:
            raise ValueError("Query not found: instance_audit.audit_by_reference_and_step in queries/sql_queries.yaml")
        
        query = query_template.format(item_number=item_number, step_id=step_id)
        
        logger.info(f"Executing DB query for CancelAIP with stepID: {step_id}")
        logger.info(f"DB Query: {query}")
        
        try:
            with get_azure_db_connection() as db:
                results = db.execute_query(query)
                
                if not results:
                    raise AssertionError(f"No results found for item_number: {item_number} and stepID: {step_id}")
                
                first_row = results[0]
                
                columns = [column[0] for column in db.cursor.description]
                logger.info(f"Available columns: {columns}")
                
                notes_index = columns.index('Notes')
                actual_note = first_row[notes_index]
                
                logger.info(f"Expected Note: {expected_note}")
                logger.info(f"Actual Note from DB: {actual_note}")
                
                assert expected_note == actual_note, (
                    f"Instance Audit note for CancelAIP stepID '{step_id}' mismatch. "
                    f"Expected: '{expected_note}', Actual: '{actual_note}'"
                )
                
                allure.attach(
                    f"Query: {query}\n\nItem Number: {item_number}\nStepID: {step_id}\nExpected Note: {expected_note}\nActual Note: {actual_note}",
                    name=f"CancelAIP DB Query Results - StepID {step_id}",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                logger.info(f"CancelAIP database verification passed for stepID {step_id}")
                
        except Exception as e:
            logger.error(f"Error executing Azure DB query for CancelAIP: {str(e)}")
            allure.attach(
                f"Error: {str(e)}\nQuery: {query}\nItem Number: {item_number}\nStepID: {step_id}",
                name="CancelAIP DB Query Error",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@when('User should execute db query to get HouseholdID')
def execute_db_query_to_get_household_id(test_context):

    with allure.step("Execute DB query to get HouseholdID"):
        test_data = test_context.get("test_data", {})
        account_number = test_data.get("account_number") or test_data.get("account_name")
        
        if not account_number:
            account_number = test_context.get("account_number")
        
        if not account_number:
            raise ValueError("Account number not found in test_context. Ensure test data is loaded.")
        
        query_template = settings.database_queries.get('account', {}).get('household_id_by_account')
        if not query_template:
            raise ValueError("Query not found: account.household_id_by_account in queries/sql_queries.yaml")
        
        query = query_template.format(account_number=account_number)
        
        logger.info(f"Executing DB query to get HouseholdID for account: {account_number}")
        logger.info(f"DB Query: {query}")
        logger.info("Setting up EWM database connection (AM_Billing)")
        
        try:
            db = get_configured_ewm_db()
            db.connect()
            
            try:
                results = db.execute_query(query)
                
                if not results or len(results) == 0:
                    raise ValueError(f"No HouseholdID found for account number: {account_number}")
                
                first_row = results[0]
                columns = [column[0] for column in db.cursor.description]
                
                family_id_index = columns.index('FamilyID')
                household_id = first_row[family_id_index]
                
                test_context['household_id'] = household_id
                
                logger.info(f"HouseholdID retrieved: {household_id}")
                
                allure.attach(
                    f"Query: {query}\n\nAccount Number: {account_number}\nHouseholdID: {household_id}",
                    name="HouseholdID DB Query Results",
                    attachment_type=allure.attachment_type.TEXT
                )
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error executing DB query to get HouseholdID: {str(e)}")
            allure.attach(
                f"Error: {str(e)}\nQuery: {query}\nAccount Number: {account_number}",
                name="HouseholdID DB Query Error",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


