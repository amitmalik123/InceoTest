"""Step definitions shared across all feature files.

Common Background steps (login, switch app, open Leads tab) live here so they
can be reused by every feature without duplication.
"""
from pytest_bdd import given, parsers


# ---------------------------------------------------------------------------
# Background steps
# ---------------------------------------------------------------------------
@given("I am logged in to Salesforce as the configured user")
def step_login(login_page, setup_page, test_data, session_state):
    if session_state["logged_in"]:
        return
    login_page.login_to_salesforce_sbx(test_data["environment"])
    setup_page.login_as_different_user(test_data["userName"])
    session_state["logged_in"] = True


@given(parsers.parse('I have switched to the "{app_name}" app'))
def step_switch_app(home_page, app_name, session_state):
    if session_state["app_open"]:
        return
    home_page.navigate_to_app(app_name)
    session_state["app_open"] = True


@given("I have opened the Leads tab")
def step_open_leads_tab(home_page, session_state):
    if session_state["leads_tab_open"]:
        return
    home_page.access_leads_tab()
    session_state["leads_tab_open"] = True
