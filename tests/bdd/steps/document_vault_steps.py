from playwright.sync_api import Page
from pytest_bdd import parsers, given, then, when

from pages.document_vault_page import DocumentVaultPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)
# This import ensures test_context is available in all step functions that need it


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
    document_vault_page.select_document_type(option_value="QPR")


@when("click documenttype dropdown and select market value report")
def click_documenttype_dropdown_and_select_market_value_report(page: Page):
    document_vault_page = DocumentVaultPage(page)
    document_vault_page.select_document_type(option_label="Market Value Reports")


@when("click documenttype dropdown and select AssetMark Trust Tax Documents")
def click_documenttype_dropdown_and_select_assetmark_trust_tax_documents(page: Page):
    document_vault_page = DocumentVaultPage(page)
    document_vault_page.select_document_type(option_label="AssetMark Trust Tax Documents")


@when("validate the Quarter dropdown should be visible for user interaction")
@when("validate the Document dropdown should be visible for user interaction")
def validate_quarter_dropdown_visible_for_user_interaction(page: Page):
    document_vault_page = DocumentVaultPage(page)
    assert document_vault_page.validate_quarter_dropdown_visible_for_user_interaction(), (
        "Quarter dropdown should be visible for user interaction"
    )


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


@then("the user clicks Save Selected and verifies a QPR-year-quarter ZIP download")
def user_clicks_save_selected_and_verify_qpr_zip(page: Page):
    document_vault_page = DocumentVaultPage(page)
    zip_filename = document_vault_page.validate_qpr_zip_download()
    assert zip_filename, "ZIP download validation failed"
    logger.info(f"ZIP download validated: {zip_filename}")


@then("the user clicks Save Selected and verifies a Document type-year ZIP download")
def user_clicks_save_selected_and_verify_document_type_year_zip(page: Page):
    document_vault_page = DocumentVaultPage(page)
    zip_filename = document_vault_page.validate_document_type_year_zip_download()
    assert zip_filename, "Document type-year ZIP download validation failed"
    logger.info(f"Document type-year ZIP download validated: {zip_filename}")


@when("select a single document and click Save selected")
@then("select a single document and click Save selected")
def select_single_document_and_click_save_selected(page: Page, test_context):
    document_vault_page = DocumentVaultPage(page)
    document_vault_page.clear_all_and_select_first_checkbox()
    # Capture PDF download when Save Selected is clicked
    pdf_download_name = document_vault_page.capture_save_selected_pdf_download()
    test_context["pdf_download_name"] = pdf_download_name
    logger.info(f"PDF download captured and stored: {pdf_download_name}")


@then("user verifies a QPR-year-quarter PDF download")
def user_verifies_qpr_pdf_download(page: Page, test_context):
    document_vault_page = DocumentVaultPage(page)
    pdf_download_name = test_context.get("pdf_download_name", "")
    assert pdf_download_name, "No PDF download captured in previous step"
    is_valid = document_vault_page.validate_qpr_pdf_download(pdf_download_name)
    assert is_valid, f"PDF validation failed for {pdf_download_name}"
    logger.info(f"PDF download validated: {pdf_download_name}")


@then("user verifies a Document type-year PDF download")
def user_verifies_document_type_year_pdf_download(page: Page, test_context):
    document_vault_page = DocumentVaultPage(page)
    pdf_download_name = test_context.get("pdf_download_name", "")
    assert pdf_download_name, "No PDF download captured in previous step"
    is_valid = document_vault_page.validate_document_type_year_pdf_download(pdf_download_name)
    assert is_valid, f"Document type-year PDF validation failed for {pdf_download_name}"
    logger.info(f"Document type-year PDF download validated: {pdf_download_name}")
