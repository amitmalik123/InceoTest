"""Reusable common BDD steps/fixtures for Billing Revenue Dashboard modules."""

import os
from pathlib import Path

import pytest
import yaml
from playwright.sync_api import Page, expect
from pytest_bdd import given, then, when

from pages.billing.platformrevenuedashboard.common.login_page import LoginPage
from pages.billing.platformrevenuedashboard.common.navigation_page import NavigationPage


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


@pytest.fixture
def revenue_dashboard_subfolder() -> str:
    # Override this fixture in child modules (for example, strategistgroupmodel, future folders).
    return "strategistgroupmodel"


def _load_env_config(revenue_dashboard_subfolder: str) -> dict:
    root = _repo_root()
    base_config_path = (
        root
        / "config"
        / "billing"
        / "platformrevenuedashboard"
        / revenue_dashboard_subfolder
        / "env.qa.yaml"
    )
    local_config_path = base_config_path.with_name("env.qa.local.yaml")

    explicit_path = os.getenv("TEST_CONFIG_PATH", "").strip()
    if explicit_path:
        config_path = Path(explicit_path)
        if not config_path.exists():
            return {}
        with open(config_path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    merged = {}
    for config_path in [base_config_path, local_config_path]:
        if not config_path.exists():
            continue
        with open(config_path, "r", encoding="utf-8") as fh:
            loaded = yaml.safe_load(fh) or {}
            for section_name in ["application", "credentials"]:
                if section_name in loaded and isinstance(loaded[section_name], dict):
                    merged.setdefault(section_name, {}).update(loaded[section_name])
    return merged


@pytest.fixture
def settings_data(revenue_dashboard_subfolder: str) -> dict:
    config = _load_env_config(revenue_dashboard_subfolder)
    cfg = config.get("application", {})
    creds = config.get("credentials", {})
    return {
        "base_url": os.getenv("BILLING_BASE_URL", cfg.get("base_url", "https://app-billing-ui-test.azurewebsites.net/")),
        "username": os.getenv("BILLING_USERNAME", creds.get("username", "")),
        "password": os.getenv("BILLING_PASSWORD", creds.get("password", "")),
    }


@pytest.fixture
def login_page(page: Page, settings_data: dict) -> LoginPage:
    return LoginPage(page, settings_data["base_url"])


@pytest.fixture
def navigation_page(page: Page) -> NavigationPage:
    return NavigationPage(page)


@pytest.fixture
def logged_in_page(
    page: Page,
    login_page: LoginPage,
    settings_data: dict,
    revenue_dashboard_subfolder: str,
) -> Page:
    if not settings_data["username"] or not settings_data["password"]:
        raise ValueError(
            "Missing credentials. Set BILLING_USERNAME and BILLING_PASSWORD env vars "
            "or populate config/billing/platformrevenuedashboard/"
            f"{revenue_dashboard_subfolder}/env.qa.local.yaml"
        )

    # Azure/AD sign-in submit can intermittently time out; retry a few times before failing.
    last_error = None
    for attempt in range(4):
        try:
            login_page.login(settings_data["username"], settings_data["password"])
            break
        except Exception as exc:
            last_error = exc
            if attempt == 3:
                raise
            page.wait_for_timeout(2000)
            page.goto(settings_data["base_url"])
            page.wait_for_load_state("domcontentloaded")

    if last_error is not None and page.url == "about:blank":
        raise last_error

    return page


@given("the user is logged into the application")
def user_logged_in(logged_in_page: Page):
    # Step is intentionally empty; requesting logged_in_page performs login via fixture side effects.
    pass


@given("the user verifies login is successful")
def verify_login_successful(logged_in_page: Page):
    logged_in_page.wait_for_load_state("domcontentloaded")

    nav_menu = logged_in_page.get_by_role("button", name="Navigation menu")
    logo = logged_in_page.get_by_role("img", name="assetmark-logo")
    strategist_group_model = logged_in_page.get_by_text("Strategist Group Model", exact=False)

    try:
        expect(nav_menu).to_be_visible(timeout=30000)
        expect(logo).to_be_visible(timeout=10000)
    except AssertionError:
        expect(strategist_group_model).to_be_visible(timeout=30000)


@when("the user navigates to Strategist Group Model")
def navigate_to_strategist_group_model(navigation_page: NavigationPage):
    navigation_page.navigate_to_strategist_group_model()


@when("the user verifies Strategist Group Model page is loaded")
def verify_strategist_group_model_page(logged_in_page: Page):
    expect(logged_in_page.get_by_text("Model", exact=True)).to_be_visible()
    expect(logged_in_page.get_by_text("Family", exact=True)).to_be_visible()


@when("the user clicks the Family tab")
def click_family_tab(logged_in_page: Page):
    logged_in_page.get_by_text("Family", exact=True).click()


@when("the user submits the form")
def submit_form(request, logged_in_page: Page):
    if getattr(request.node, "skip_submit_for_existing_record", False):
        return

    submit_button = logged_in_page.get_by_role("button", name="Submit").first
    if submit_button.is_visible():
        submit_button.click()


@when("the user confirms the submission")
def confirm_submission(request, logged_in_page: Page):
    success_dialog = logged_in_page.get_by_role("dialog").filter(has_text="Family added successfully")
    if success_dialog.count() > 0 and success_dialog.first.is_visible():
        success_dialog.get_by_role("button", name="OK").click()
        expect(success_dialog.first).to_be_hidden(timeout=10000)


@then("the user logs out")
def user_logs_out(login_page: LoginPage):
    login_page.logout()
