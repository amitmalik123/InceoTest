"""
Step definitions for adding strategies to a portfolio via Portfolio Engine.
Converts TypeScript: addStrategiesToPortfolio.ts
"""

import logging
from pytest_bdd import given, when, then, parsers
from playwright.sync_api import Page, expect

from pages.proposal import PortfolioEnginePage
from tests.steps.proposal.instance_manager import (
    set_portfolio_engine_instance,
    get_portfolio_engine_instance,
)
from pages.proposal.helper_functions import navigate_to_home_page, navigate_to_portfolio_engine
from config.proposal.settings import get_settings

logger = logging.getLogger(__name__)


@given("I am on the Portfolio Engine page")
def navigate_to_portfolio_engine_page(page: Page):
    settings = get_settings()
    ewm_cfg = settings.config.get("applications", {}).get("ewm", {})
    is_navbar = ewm_cfg.get("login_page_class", "") == "NavbarLoginPage"

    navigate_to_home_page(page)
    portfolio_engine_page_object = navigate_to_portfolio_engine(page, is_navbar=is_navbar)
    portfolio_engine_page_instance = PortfolioEnginePage(portfolio_engine_page_object)
    set_portfolio_engine_instance(portfolio_engine_page_instance)

    # Dismiss privacy dialog immediately
    portfolio_engine_page_instance.dismiss_privacy_dialog()

    # Dismiss soft-closed warning modal if it appears
    portfolio_engine_page_instance.dismiss_soft_closed_warning()

    # Wait for either Get Started or Manage Portfolios button to be visible
    max_retries = 30
    retry_interval = 1000  # milliseconds
    
    for attempt in range(max_retries):
        if (portfolio_engine_page_instance.get_started_button.is_visible(timeout=500)
            or portfolio_engine_page_instance.manage_portfolios_button.is_visible(timeout=500)):
            break
        portfolio_engine_page_instance.page.wait_for_timeout(retry_interval)
    else:
        raise TimeoutError("Neither Get Started nor Manage Portfolios button appeared after 30 seconds")


@when("I click the manage portfolios button")
def click_manage_portfolios_button(page: Page):
    portfolio_engine_page_instance = get_portfolio_engine_instance()

    try:
        # Wait for either button to be visible using polling
        max_retries = 30
        retry_interval = 1000  # milliseconds
        
        for attempt in range(max_retries):
            if (
                portfolio_engine_page_instance.get_started_button.is_visible()
                or portfolio_engine_page_instance.manage_portfolios_button.is_visible()
            ):
                break
            portfolio_engine_page_instance.page.wait_for_timeout(retry_interval)
        else:
            raise TimeoutError("Neither Get Started nor Manage Portfolios button appeared after 30 seconds")
    except Exception as err:
        logger.error(
            "Portfolio Engine homepage failed to load in time", exc_info=err
        )
        raise err

    # If Get Started is visible, it is an exclusive page state.
    if portfolio_engine_page_instance.get_started_button.is_visible():
        portfolio_engine_page_instance.get_started_button.click()
        return

    # Race condition: either the portfolio warning modal OR Manage Portfolios button will be visible
    # Try to dismiss modal first (if it appears); otherwise click Manage Portfolios
    for attempt in range(5):
        # Check if portfolio warning modal is visible
        if portfolio_engine_page_instance.portfolio_warning_modal.is_visible(timeout=15000):
            portfolio_engine_page_instance.dismiss_portfolio_warning()
            return

        # Check if Manage Portfolios button is visible
        if portfolio_engine_page_instance.manage_portfolios_button.is_visible(timeout=15000):
            portfolio_engine_page_instance.manage_portfolios_button.click()
            return

        # Delay before retry
        portfolio_engine_page_instance.page.evaluate(
            "() => new Promise((resolve) => setTimeout(resolve, 300))"
        )

    raise RuntimeError(
        "Neither portfolio warning modal nor Manage Portfolios button was visible after retries"
    )


@when("I create a new model portfolio")
def create_new_model_portfolio(page: Page):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.form_root.locator("body").wait_for(state="visible", timeout=15000)
    portfolio_engine_page_instance.create_new_model_portfolio_button.wait_for(state="visible", timeout=60000)
    portfolio_engine_page_instance.create_new_model_portfolio_button.click(timeout=60000)


@when("I select AssetMark Platform Strategies as portfolio type")
def select_assetmark_platform_strategies(page: Page):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.asset_mark_platform_strategies_text.wait_for(
        state="visible"
    )
    portfolio_engine_page_instance.asset_mark_platform_strategies_text.evaluate(
        "el => el.click()"
    )


@when("I select Savos Personal Portfolio Custom as portfolio type")
def select_savos_personal_strategy(page: Page):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.savos_personal_strategy_text.wait_for(
        state="visible"
    )
    portfolio_engine_page_instance.savos_personal_strategy_text.evaluate(
        "el => el.click()"
    )


@when(parsers.re(r'I add the following strategies to the portfolio "(?P<strategies>.*)"'))
def add_strategies_to_portfolio(page: Page, strategies: str):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    strategy_list = [s.strip() for s in strategies.split(";")]
    for strategy in strategy_list:
        portfolio_engine_page_instance.add_strategy_to_portfolio(strategy)


@when(parsers.parse('I enter portfolio name "{portfolio_name}"'))
def enter_portfolio_name(page: Page, portfolio_name: str):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.model_portfolio_name_textbox.fill(portfolio_name)


@when("I save the portfolio")
def save_portfolio(page: Page):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    with portfolio_engine_page_instance.page.expect_response(
        lambda r: "/api/pe/v2/portfolio" in r.url and r.request.method in ("GET", "POST"),
        timeout=60000,
    ):
        portfolio_engine_page_instance.strategy_save_button.click()
    logger.debug("Portfolio save confirmed — /api/pe/v2/portfolio responded")


@then("the portfolio should contain the expected strategies")
def verify_portfolio_contains_strategies(page: Page):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    try:
        expect(
            portfolio_engine_page_instance.investment_allocation_text,
        ).to_contain_text(
            "Core MarketsAssetMark Income Builder, Profile 2, ConservativeETF | 2Tactical Strategies - Enhanced Return FocusBlackRock Equity DividendIMA | 6Tactical Strategies - Limit Loss FocusSavos US Risk Controlled Strategy, Profile 6GMS | 6Tactical Strategies - Enhanced Return FocusAIM Decathlon Growth, Profile 5ETF | 5Diversifying Strategies - Bonds and Bond AlternativesJPMorgan Absolute Return - Profile 1MF | 1"
        )
    except Exception as err:
        logger.error(
            "Expected strategies not found in portfolio allocation text", exc_info=err
        )
        raise err


@then(parsers.parse('all strategies should have "{expected_allocation}" percent allocation'))
def verify_allocation_percentage(page: Page, expected_allocation: str):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    for i in range(5):
        try:
            expect(
                portfolio_engine_page_instance.get_allocation_textbox(i),
            ).to_have_value(expected_allocation)
        except Exception as err:
            logger.error(
                f"Allocation percent mismatch for strategy index {i}", exc_info=err
            )
            raise err
