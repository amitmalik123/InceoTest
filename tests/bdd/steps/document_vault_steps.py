from playwright.sync_api import Page
from pytest_bdd import parsers, given, then, when

from pages.document_vault_page import DocumentVaultPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when("navigates to Document vault")
@given("navigates to Document vault")
def navigate_to_document_vault(page: Page):
    document_vault_page = DocumentVaultPage(page)
    document_vault_page.navigate_to_document_vault()


@when(parsers.parse('navigates to document vault with "{sheet_name}" , {row_number:d}'))
def navigates_to_document_vault_with(page: Page, excel_data_manager, test_context, sheet_name: str, row_number: int):
    """Navigate to document vault using Excel row data (new navbar flow - clients tab already clicked)."""
    if row_number < 2:
        raise ValueError(
            f"Invalid RowNumber '{row_number}' for sheet '{sheet_name}'. "
            "Use Excel row numbers starting at 2 (first data row)."
        )
    row_data = excel_data_manager.get_row(sheet_name, row_number - 2)
    test_context["excel_row_data"] = row_data

    client_name = None
    for key in ["ClientName", "Client Name", "clientname"]:
        value = row_data.get(key)
        if value is not None and str(value).strip() != "":
            client_name = str(value).strip()
            break

    if not client_name:
        raise ValueError(
            f"ClientName is missing in Excel sheet '{sheet_name}' row {row_number}. "
            "Expected one of columns: ClientName, Client Name"
        )

    logger.info(f"Navigating to Document Vault for client: {client_name}")
    document_vault_page = DocumentVaultPage(page)
    document_vault_page.navigates_to_doc_vault_from_clients(client_name)


@when("switch the date filter dropdown to All")
def switch_the_date_filter_dropdown_to_all(page: Page):
    document_vault_page = DocumentVaultPage(page)
    document_vault_page.date_filter()


@when("validate document vault column headers")
def validate_document_vault_column_headers(page: Page):
    document_vault_page = DocumentVaultPage(page)
    result = document_vault_page.validate_document_vault_headers(
        "tests/bdd/resources/document_vault.properties"
    )
    assert result, "Header validation failed"


@then("expand all headers and validate the download functionality")
def expand_all_headers_and_validate_the_download_functionality(page: Page):
    document_vault_page = DocumentVaultPage(page)
    document_vault_page.validate_download_func()


@then("validate the Restore Default functionality")
def validate_the_restore_default_functionality(page: Page):
    document_vault_page = DocumentVaultPage(page)
    document_vault_page.restore_default()


@then("close all the expanded headers")
def close_all_the_expanded_headers(page: Page):
    document_vault_page = DocumentVaultPage(page)
    document_vault_page.close_expanded_headers()


@when("validate all the dropdowns are enabled for user interaction")
def validate_all_dropdowns_enabled_for_user_interaction(page: Page):
    document_vault_page = DocumentVaultPage(page)
    document_vault_page.validate_all_dropdowns_enabled_for_user_interaction()


@when("click documenttype dropdown and select QPR document")
def click_documenttype_dropdown_and_select_document(page: Page):
    document_vault_page = DocumentVaultPage(page)
    document_vault_page.select_document_type_quarterly_performance_reports()


@then("validate find button is enabled for user interaction")
def validate_find_button_enabled(page: Page):
    document_vault_page = DocumentVaultPage(page)
    assert document_vault_page.validate_find_button_enabled(), "Find button should be enabled"


@when("user clicks Select All filters")
def user_clicks_select_all_filters(page: Page):
    document_vault_page = DocumentVaultPage(page)
    document_vault_page.click_select_all_filters()


@then("verify all filters are selected")
def verify_all_filters_selected(page: Page):
    document_vault_page = DocumentVaultPage(page)
    assert document_vault_page.verify_all_filters_selected(), "All filters should be selected"


@when("user clicks Clear All filters")
def user_clicks_clear_all_filters(page: Page):
    document_vault_page = DocumentVaultPage(page)
    document_vault_page.click_clear_all_filters()


@then("verify all filters are cleared")
@when("verify all filters are cleared")
def verify_all_filters_cleared(page: Page):
    document_vault_page = DocumentVaultPage(page)
    assert document_vault_page.verify_all_filters_cleared(), "All filters should be cleared"


@then("validate View selected and Save selected buttons are enabled or disabled based on filter selection")
def validate_button_states_based_on_filter_selection(page: Page):
    document_vault_page = DocumentVaultPage(page)
    assert document_vault_page.validate_button_states_based_on_filter_selection(), (
        "View selected and Save selected buttons should match expected state"
    )
