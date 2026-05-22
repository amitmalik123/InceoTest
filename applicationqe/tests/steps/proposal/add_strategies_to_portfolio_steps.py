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

logger = logging.getLogger(__name__)


@given("I am on the Portfolio Engine page")
def navigate_to_portfolio_engine_page(page: Page):
    navigate_to_home_page(page)
    portfolio_engine_page_object = navigate_to_portfolio_engine(page)
    portfolio_engine_page_instance = PortfolioEnginePage(portfolio_engine_page_object)
    set_portfolio_engine_instance(portfolio_engine_page_instance)

    # Dismiss privacy dialog immediately
    portfolio_engine_page_instance.dismiss_privacy_dialog()

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

    # Otherwise, handle OK/Manage Portfolios flow where either button takes you to the next step.
    # OK button is part of the overlay; clicking it dismisses the overlay and proceeds.
    for attempt in range(5):
        if (
            portfolio_engine_page_instance.manage_portfolios_button.is_visible()
        ):
            # Manage Portfolios is visible and not blocked; click to proceed
            portfolio_engine_page_instance.manage_portfolios_button.click(
                timeout=5000
            )
            return

        # Delay before retry if neither button is visible
        portfolio_engine_page_instance.page.evaluate(
            "() => new Promise((resolve) => setTimeout(resolve, 300))"
        )

    raise RuntimeError(
        "Neither OK button nor Manage Portfolios button was visible after retries"
    )


@when("I create a new model portfolio")
def create_new_model_portfolio(page: Page):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.create_new_model_portfolio_button.click()


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


@when("I add the following strategies to the portfolio:", target_fixture=None)
def add_strategies_to_portfolio(page: Page, datatable):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    # Handle both DataTable object and list formats
    if hasattr(datatable, 'raw'):
        strategies = [row[0] for row in datatable.raw()]
    else:
        # If it's already a list from BDD scenario
        strategies = [row[0] if isinstance(row, (list, tuple)) else row for row in datatable]
    for strategy in strategies:
        portfolio_engine_page_instance.add_strategy_to_portfolio(strategy)


@when(parsers.parse('I enter portfolio name "{portfolio_name}"'))
def enter_portfolio_name(page: Page, portfolio_name: str):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.model_portfolio_name_textbox.fill(portfolio_name)


@when("I save the portfolio")
def save_portfolio(page: Page):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.strategy_save_button.click()
    portfolio_engine_page_instance.page.wait_for_load_state()


@then("the portfolio should contain the expected strategies")
def verify_portfolio_contains_strategies(page: Page):
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    try:
        expect(
            portfolio_engine_page_instance.investment_allocation_text,
        ).to_contain_text(
            "Core MarketsAssetMark Income Builder, Profile 2, ConservativeETF | 2Tactical Strategies - Enhanced Return FocusBlackRock Equity DividendIMA | 6Tactical Strategies - Limit Loss FocusSavos US Risk Controlled Strategy, Profile 6GMS | 6Diversifying Strategies - Equity AlternativesAlphaSimplex, Alternative Model Portfolio, Profile 5, GrowthMF | 5Diversifying Strategies - Bonds and Bond AlternativesJPMorgan Absolute Return - Profile 1MF | 1"
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
