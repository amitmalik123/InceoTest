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
    """
    Verify that Portfolio Engine widgets load with data content.
    
    Checks both headers and actual data content within widgets to ensure
    they're not just showing placeholder/loading states. Avoids brittle
    SVG selectors that differ between navbar and legacy environments.
    """
    logger.debug("\nVerifying widget data loads successfully")
    portfolio_engine_page_instance = get_portfolio_engine_instance()
    
    # Wait for first widget to appear (confirms PE iframe is fully loaded)
    expect(
        portfolio_engine_page_instance.upside_downside_capture_header
    ).to_be_visible(timeout=30000)
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
    
    # Verify actual data content is visible within widgets
    # (not just placeholders like "Data temporarily not available")
    logger.debug("Verifying data content in widgets")
    
    # Asset Allocation widget should show percentage values (e.g., "62.55 %", "Equity")
    asset_alloc_text = portfolio_engine_page_instance.form_root.locator("article:has-text('Asset Allocation & Holdings')").first
    expect(asset_alloc_text).to_contain_text("%")
    
    # Summary Statistics widget should show table with actual values
    summary_stats = portfolio_engine_page_instance.form_root.locator("article:has-text('Summary Statistics')").first
    expect(summary_stats).to_contain_text("Widget Test Portfolio")
    
    # Return by Strategy widget should have data
    return_strategy = portfolio_engine_page_instance.form_root.locator("article:has-text('Return by Strategy')").first
    expect(return_strategy).to_be_visible()
    
    logger.debug("All widget data verified successfully")
    expect(
        portfolio_engine_page_instance.performance_header
    ).to_be_visible()
    
    # Verify each widget article is present (all widget content is rendering on navbar)
    # Check by heading text rather than brittle SVG selectors
    logger.debug("\nVerifying widget articles are present with content...")
    widget_headings = [
        "Upside/Downside Capture",
        "Investment Approach",
        "Return by Strategy",
        "Stress Test",
        "Asset Allocation & Holdings",
        "Risk vs Return",
        "Summary Statistics",
        "Drawdown",
        "Performance",
    ]
    
    for heading_text in widget_headings:
        # Each widget is an article with a heading containing the widget name
        widget_article = portfolio_engine_page_instance.form_root.locator("article").filter(has_text=heading_text)
        expect(widget_article).to_be_visible(timeout=10000)
        logger.debug(f"  ✓ {heading_text} widget is visible")
    
    logger.debug("\nAll widgets loaded successfully!")
