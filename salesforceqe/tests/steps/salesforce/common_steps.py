"""Step definitions shared across all feature files.

Common Background steps (login, switch app, open Leads tab) live here so they
can be reused by every feature without duplication.
"""

from pytest_bdd import given, parsers
from utils.logger import get_allure_logger
logger = get_allure_logger(__name__)


# When running in Azure Pipelines (or any CI), always re-execute Background
# steps. The browser context is fresh/headless on the build agent and the
# cached session_state flags can be stale, causing login / app / tab steps
# to be skipped while the page is not actually in the expected state.
# ---------------------------------------------------------------------------
# Background steps
# ---------------------------------------------------------------------------
@given("I am logged in to Salesforce as the configured user")
def step_login(login_page, setup_page, test_data, session_state):
    if session_state["logged_in"]:
        logger.info("User is already logged in.")
        return
    login_page.login_to_salesforce_sbx(test_data["environment"])
    setup_page.login_as_different_user(test_data["userName"])
    session_state["logged_in"] = True
    logger.info(f"Logged in to Salesforce as {test_data['userName']}.")


@given(parsers.parse('I have switched to the "{app_name}" app'))
def step_switch_app(home_page, app_name, session_state):
    if session_state["app_open"]:
        logger.info(f"App {app_name} is already open.")
        return
    home_page.navigate_to_app(app_name)
    session_state["app_open"] = True
    logger.info(f"Switched to the {app_name} app.")


@given("I have opened the Leads tab")
def step_open_leads_tab(home_page, session_state):
    if session_state["leads_tab_open"]:
        logger.info("Leads tab is already open.")
        return
    home_page.access_leads_tab()
    session_state["leads_tab_open"] = True
    logger.info("Leads tab is opened.")
