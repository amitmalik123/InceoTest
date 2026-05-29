import pytest
from playwright.sync_api import Playwright

from pages.salesforce.loginPage import LoginPage
from pages.salesforce.setupPage import Setup
from pages.salesforce.homePage import Homepage
from pages.salesforce.leadsPage_HappyPath import LeadsPage_HappyPath
from pages.salesforce.leadsPage_ValidationErrors import LeadsPage_ValidationErrors
from pages.salesforce.leadsPage_Fields import LeadsPage_Fields
from pages.salesforce.leadsPage_PicklistValues import LeadsPage_PicklistValues
from utils.randomString import Utils
from utils.logger import get_allure_logger
logger = get_allure_logger(__name__)


# ---------------------------------------------------------------------------
# Static configuration (kept in sync with the original test modules)
# ---------------------------------------------------------------------------
ENVIRONMENT = "FSCQA"
USER_NAME = "Gaurav Joshi"
APP_NAME = "Monarch Console"


# ---------------------------------------------------------------------------
# Browser / page (module scoped so login persists across scenarios)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def open_browser(playwright: Playwright):
    browser = playwright.chromium.launch(
        headless=True,
        args=["--start-maximized", "--deny-permission-prompts"],
    )
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        screen={"width": 1920, "height": 1080},
        locale="None",
    )
    page = context.new_page()
    logger.info("Browser is opened...")
    yield page

    # ----- Teardown: logout from Salesforce, then close context / browser -----
    logger.info("Logging out from Salesforce...")
    LoginPage(page).logout_from_salesforce_sbx()  # perform logout via UI to ensure session ends properly
    context.close()
    browser.close()
    logger.info("Logged out from Salesforce and browser is closed.")
    # try:
    #     # /secur/logout.jsp is Salesforce's standard logout endpoint and works
    #     # for every org/theme without depending on UI element locators.
    #     current_url = page.url or ""
    #     if current_url.startswith("http"):
    #         # Derive the org base URL (scheme + host) from the current page.
    #         from urllib.parse import urlparse
    #         parsed = urlparse(current_url)
    #         base = f"{parsed.scheme}://{parsed.netloc}"
    #         page.goto(f"{base}/secur/logout.jsp", wait_until="load", timeout=15000)
    # except Exception as exc:  # never let teardown fail the test run
    #     print(f"[teardown] Salesforce logout skipped: {exc}")
    # finally:
    #     try:
    #         context.close()
    #     finally:
    #         browser.close()


@pytest.fixture(scope="module")
def page(open_browser):
    """Alias used by BDD step definitions."""
    return open_browser


# ---------------------------------------------------------------------------
# Test data (module scoped so the same Lead is reused across scenarios)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def test_data():
    utils = Utils()
    last_name = utils.generate_random_string()
    first_name = "Automation"
    return {
        "environment": ENVIRONMENT,
        "userName": USER_NAME,
        "appName": APP_NAME,
        "firstName": first_name,
        "lastName": last_name,
        "email": f"{first_name}{last_name}@test.com",
        # "CRD": utils.generate_random_number(),
        # "CRD_Firm": utils.generate_random_number(),
        "CRD_Advisor": utils.generate_random_number(),
        "BD_Account": "BD Account_Test1",
    }


# ---------------------------------------------------------------------------
# Page object fixtures (module scoped - they only wrap the shared page)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def login_page(page):
    return LoginPage(page)


@pytest.fixture(scope="module")
def setup_page(page):
    return Setup(page)


@pytest.fixture(scope="module")
def home_page(page):
    return Homepage(page)


@pytest.fixture(scope="module")
def lead_fields(page):
    return LeadsPage_Fields(page)


@pytest.fixture(scope="module")
def lead_picklists(page):
    return LeadsPage_PicklistValues(page)


@pytest.fixture(scope="module")
def lead_validation(page):
    return LeadsPage_ValidationErrors(page)


@pytest.fixture(scope="module")
def lead_happy_path(page):
    return LeadsPage_HappyPath(page)


# ---------------------------------------------------------------------------
# Session-wide flags so background steps only execute once
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def session_state():
    return {
        "logged_in": False,
        "app_open": False,
        "leads_tab_open": False,
        "lead_created": False,
    }
