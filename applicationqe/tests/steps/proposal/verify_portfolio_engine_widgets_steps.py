"""
Step definitions for verifying Portfolio Engine widgets load correctly.
Converts TypeScript: verifyPortfolioEngineWidgetsLoad.ts
"""

import logging
from pytest_bdd import when, then
from playwright.sync_api import Page, expect

from tests.steps.proposal.instance_manager import get_portfolio_engine_instance

logger = logging.getLogger(__name__)


@when("I enable all Portfolio Engine widgets")
def enable_all_widgets(page: Page):
    logger.debug("\nEnabling all widgets")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    portfolio_engine_page_instance.select_all_widgets_if_needed()


@then("the Portfolio Engine widgets should load successfully")
def verify_widgets_load_successfully(page: Page):
    # Verify all widget headers are loaded
    logger.debug("\nVerifying widget headers are visible")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    
    expect(
        portfolio_engine_page_instance.upside_downside_capture_header
    ).to_be_visible()
    expect(
        portfolio_engine_page_instance.investment_approach_header
    ).to_be_visible()
    expect(
        portfolio_engine_page_instance.return_by_strategy_header
    ).to_be_visible()
    expect(
        portfolio_engine_page_instance.stress_test_header
    ).to_be_visible()
    expect(
        portfolio_engine_page_instance.asset_allocation_holdings_header
    ).to_be_visible()
    expect(
        portfolio_engine_page_instance.risk_vs_return_header
    ).to_be_visible()
    expect(
        portfolio_engine_page_instance.summary_statistics_header
    ).to_be_visible()
    expect(
        portfolio_engine_page_instance.drawdown_header
    ).to_be_visible()
    expect(
        portfolio_engine_page_instance.performance_header
    ).to_be_visible()

    # Verify all widgets have content loaded
    logger.debug(
        "\nWaiting for all widgets to load content (this may take some time)"
    )

    # Define widgets to verify
    widgets_to_verify = [
        {
            "name": "Investment Approach",
            "locator": portfolio_engine_page_instance.investment_approach_graph_content,
        },
        {
            "name": "Asset Allocation",
            "locator": portfolio_engine_page_instance.asset_allocation_graph_content,
        },
        {
            "name": "Drawdown",
            "locator": portfolio_engine_page_instance.drawdown_graph_content,
        },
        {
            "name": "Summary Statistics",
            "locator": portfolio_engine_page_instance.summary_statistics_graph_content,
        },
        {
            "name": "Risk vs Return",
            "locator": portfolio_engine_page_instance.risk_vs_return_graph_content,
        },
        {
            "name": "Stress Test",
            "locator": portfolio_engine_page_instance.stress_test_graph_content,
        },
        {
            "name": "Upside/Downside",
            "locator": portfolio_engine_page_instance.upside_downside_graph_content,
        },
        {
            "name": "Performance",
            "locator": portfolio_engine_page_instance.performance_graph_content,
        },
        {
            "name": "Return by Strategy",
            "locator": portfolio_engine_page_instance.return_by_strategy_graph_content,
        },
    ]

    # Expect each widget to have content loaded
    for widget in widgets_to_verify:
        logger.debug(f"  Waiting for {widget['name']} to load content...")
        expect(widget["locator"].first).to_be_visible()

    logger.debug("\nAll widgets finished loading")
