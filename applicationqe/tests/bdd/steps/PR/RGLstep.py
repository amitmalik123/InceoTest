"""
RGL verification steps for page elements and content validation
"""

from playwright.sync_api import Page
from pytest_bdd import parsers, given, then, when

from config.settings import get_settings
from pages.PR.clients_page import ClientsPage
from pages.PR.rgl_page import RGLPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


def _get_excel_value(row_data: dict, keys: list[str], field_label: str) -> str:
	for key in keys:
		value = row_data.get(key)
		if value is not None and str(value).strip() != "":
			return str(value).strip()
	raise ValueError(f"{field_label} is missing in excel row data. Expected one of columns: {', '.join(keys)}")


def _click_clients_tab_and_wait(page: Page):
	"""Open Clients tab before navigating to RGL page."""
	logger.info("Ensuring Clients tab is clicked before RGL navigation")
	if page.is_closed():
		raise AssertionError(
			"Cannot click Clients tab because the browser page is already closed. "
			"Do not close the browser while the test is running."
		)

	current_url = page.url or ""
	if current_url.startswith("about:blank"):
		settings = get_settings()
		home_url = settings.get_app_config("ewm").get("home_url", settings.base_url)
		logger.info(f"Recovered from about:blank before clicking Clients, opening {home_url}")
		page.goto(home_url, timeout=30000)
		page.wait_for_load_state("domcontentloaded", timeout=30000)

	# Keep the pre-click wait short so visible Clients tab clicks do not stall.
	page.wait_for_load_state("domcontentloaded", timeout=5000)

	current_url = page.url or ""
	if page.is_closed() or current_url.startswith("about:blank"):
		raise AssertionError(
			"Page is not ready after login/navigation (closed or about:blank). "
			"Login/redirect did not complete successfully."
		)
	page.wait_for_timeout(250)

	settings = get_settings()
	clients_page = ClientsPage(page, base_url=settings.base_url)
	try:
		clients_page.click_clients()
		return
	except Exception as exc:
		logger.info(f"ClientsPage.click_clients() fallback engaged: {exc}")

	locator_candidates = [
		page.get_by_role("link", name="Clients").first,
		page.locator("//a[normalize-space()='Clients']").first,
		page.locator("text=Clients").first,
	]

	last_error = None
	for clients_tab in locator_candidates:
		try:
			clients_tab.wait_for(state="visible", timeout=10000)
			clients_tab.scroll_into_view_if_needed(timeout=3000)
			clients_tab.click(timeout=8000)
			page.wait_for_load_state("domcontentloaded", timeout=15000)
			return
		except Exception as exc:
			last_error = exc
			try:
				clients_tab.click(timeout=8000, force=True)
				page.wait_for_load_state("domcontentloaded", timeout=15000)
				return
			except Exception as force_exc:
				last_error = force_exc

	raise AssertionError(f"Unable to click Clients tab before RGL navigation: {last_error}")


@when(parsers.parse('user navigates to the RGL page "{client_name}"'))
def navigate_to_rgl_page(page: Page, client_name: str, test_context):
	row_data = test_context.get("excel_row_data") or {}
	if row_data:
		excel_client_name = _get_excel_value(
			row_data,
			["ClientName", "Client name", "Client Name", "clientname"],
			"Client name",
		)
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
	client_name = _get_excel_value(
		row_data,
		["ClientName", "Client name", "Client Name", "clientname"],
		"Client name",
	)
	logger.info(f"Navigating to RGL page from Excel row for client: {client_name}")
	rgl_page = RGLPage(page)
	rgl_page.navigate_to_gain_loss_page(client_name)


@given("user click on clients tab")
def given_user_clicks_clients_tab(page: Page):
	"""BDD Given step to open Clients tab before RGL navigation."""
	_click_clients_tab_and_wait(page)


@given("navigates to account information screen for cash advantage account")
@when("navigates to account information screen for cash advantage account")
def navigate_to_account_information_screen(page: Page):
	logger.info("Navigating to account information screen for cash advantage account")
	rgl_page = RGLPage(page)
	rgl_page.navigate_account_information()


@given("navigates to account information screen for non cash advantage account")
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
