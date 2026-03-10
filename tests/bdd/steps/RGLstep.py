"""
RGL verification steps for page elements and content validation
"""

from playwright.sync_api import Page
from pytest_bdd import parsers, then, when

from pages.rgl_page import RGLPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


@when(parsers.parse('user navigates to the RGL page "{client_name}"'))
def navigate_to_rgl_page(page: Page, client_name: str):
	logger.info(f"Navigating to RGL page for client: {client_name}")
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
