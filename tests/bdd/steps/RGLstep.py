"""
RGL verification steps for page elements and content validation
"""

from playwright.sync_api import Page
from pytest_bdd import parsers, given, then, when

from pages.rgl_page import RGLPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when(parsers.parse('user navigates to the RGL page "{client_name}"'))
def navigate_to_rgl_page(page: Page, client_name: str, test_context):
	row_data = test_context.get("excel_row_data") or {}
	excel_client_name = row_data.get("ClientName")
	if excel_client_name is not None and str(excel_client_name).strip() != "":
		excel_client_name = str(excel_client_name).strip()
		feature_client_name = client_name.strip()
		is_excel_placeholder = feature_client_name.lower() in {"clientname", "client name"}
		if (
			not feature_client_name.lower().startswith("source:")
			and not is_excel_placeholder
			and feature_client_name != excel_client_name
		):
			raise AssertionError(
				f"Client name mismatch: feature='{client_name}' excel='{excel_client_name}'"
			)
		client_name = excel_client_name

	logger.info(f"Navigating to RGL page for client: {client_name}")
	rgl_page = RGLPage(page)
	rgl_page.navigate_to_gain_loss_page(client_name)


@when("user navigates to the RGL page")
def navigate_to_rgl_page_from_excel_row(page: Page, test_context):
	row_data = test_context.get("excel_row_data") or {}
	client_name = row_data.get("ClientName")
	if client_name is None or str(client_name).strip() == "":
		raise ValueError(
			"ClientName is missing in excel row data. "
			"Provide a row with 'ClientName' value in the Excel sheet."
		)

	client_name = str(client_name).strip()
	logger.info(f"Navigating to RGL page from Excel row for client: {client_name}")
	rgl_page = RGLPage(page)
	rgl_page.navigate_to_gain_loss_page(client_name)


@when("navigates to account information screen for cash advantage account")
def navigate_to_account_information_screen(page: Page):
	logger.info("Navigating to account information screen for cash advantage account")
	rgl_page = RGLPage(page)
	rgl_page.navigate_account_information()


@when("navigates to account information screen for non cash advantage account")
def navigate_to_non_cash_account_information_screen(page: Page):
	logger.info("Navigating to account information screen for non cash advantage account")
	rgl_page = RGLPage(page)
	rgl_page.navigate_account_information_non_cash_advantage()


@then("user  validate all the headers are present")
def validate_rgl_headers(page: Page):
	logger.info("Validating RGL headers are present")
	rgl_page = RGLPage(page)
	rgl_page.apply_date_filter_all()
	rgl_page.assert_headers_present("tests/bdd/resources/rgl.properties")


@then("user validate the Costbasis,Proceeds,Gain/Loss")
def validate_rgl_values(page: Page):
	logger.info("Validating Costbasis, Proceeds, Gain/Loss values")
	rgl_page = RGLPage(page)
	rgl_page.apply_date_filter_all()
	rgl_page.assert_costbasis_proceeds_gainloss()


@then("RGL page should be displayed")
def verify_rgl_page_displayed(page: Page):
	logger.info("Verifying RGL page is displayed")
	rgl_page = RGLPage(page)
	# Verify page is on RGL by checking for key element (list of headers)
	rgl_page.wait_for_element(rgl_page.list_of_headers.first, timeout=10000)
	logger.info("RGL page successfully displayed")


@then("user can see the updated Bancorp Link")
def verify_updated_bancorp_link(page: Page):
	logger.info("Verifying updated Bancorp link")
	rgl_page = RGLPage(page)
	rgl_page.verify_bancorp_link_opens_updated_url()


@then("user can see Outdated Bancorp URL Is Not Present")
def verify_outdated_bancorp_url_not_present(page: Page):
	logger.info("Verifying outdated Bancorp URL is not present")
	rgl_page = RGLPage(page)
	rgl_page.verify_outdated_bancorp_url_not_present()


@then("user cannot see any Bancorp URL Present")
def verify_no_bancorp_url_present(page: Page):
	logger.info("Verifying no Bancorp URL is present")
	rgl_page = RGLPage(page)
	rgl_page.verify_no_bancorp_url_present()


# ============================================================================
# New NavBar RGL Steps
# ============================================================================


@when(parsers.parse('user navigates to the new navbar RGL page using "{sheet_name}" , {row_number:d}'))
def navigate_to_new_navbar_rgl_page(
	page: Page, excel_data_manager, test_context, sheet_name: str, row_number: int
):
	"""Navigate to the RGL page using the new navbar flow with Excel row data."""
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

	logger.info(f"Navigating to new navbar RGL page for client: {client_name}")
	rgl_page = RGLPage(page)
	rgl_page.navigate_to_gain_loss_page_from_clients(client_name)


@then("new navbar RGL page should be displayed")
def verify_new_navbar_rgl_page_displayed(page: Page):
	"""Verify the RGL page is displayed in the new navbar flow."""
	logger.info("Verifying new navbar RGL page is displayed")
	rgl_page = RGLPage(page)
	rgl_page.wait_for_element(rgl_page.list_of_headers.first, timeout=15000)
	logger.info("New navbar RGL page successfully displayed")
