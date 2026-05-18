"""Test Data Step Definitions

Steps for loading and accessing test data from external sources (Excel, CSV, etc.).
Excel file is loaded once at session scope via excel_data_manager fixture.
"""

from pytest_bdd import parsers, when

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when(parsers.parse('I load test data from excel sheet "{sheet_name}"'))
def load_data_from_excel(test_context, sheet_name: str, excel_data_manager):
    """Load test data from a specific Excel sheet into test_context.

    Excel file is already loaded once at session scope by excel_data_manager fixture.
    This step reads the requested sheet and stores it in test_context for later access.

    Usage in feature:
        When I load test data from excel sheet "Shell"
    Access later:
        test_context["excel_data"]["Shell"][0]["ColumnName"]
    """
    data = excel_data_manager.get_sheet(sheet_name)

    logger.info(f"Loading sheet '{sheet_name}': {len(data)} rows")
    columns = list(data[0].keys()) if data else []
    logger.info(f"Columns: {columns}")
    for idx, row in enumerate(data[:3], 1):
        logger.info(f"Row {idx}: {row}")

    # Store in test_context for step access
    if "excel_data" not in test_context:
        test_context["excel_data"] = {}
    test_context["excel_data"][sheet_name] = data

    # client_name = test_context["excel_data"]["Shell"][1]["clientName"]
