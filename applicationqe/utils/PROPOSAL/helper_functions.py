"""
Helper functions for common Playwright operations.
Ported from TypeScript helper functions with full navigation and interaction logic.
"""

import logging
import os
from playwright.sync_api import Locator, Page

logger = logging.getLogger(__name__)


def select_if_visible(thing_to_select: Locator) -> None:
    """
    Click an element if it is visible, otherwise do nothing.
    
    Ported from TypeScript: selectIfVisible()

    Args:
        thing_to_select: Playwright Locator to click if visible.
    """
    if thing_to_select.is_visible():
        thing_to_select.click()
        logger.debug(f"Clicked element: {thing_to_select}")


def check_if_unchecked(checkbox_to_select: Locator) -> None:
    """
    Check a checkbox if it is currently unchecked, otherwise do nothing.
    
    Ported from TypeScript: checkIfUnchecked()

    Args:
        checkbox_to_select: Playwright Locator for the checkbox to check if unchecked.
    """
    if not checkbox_to_select.is_checked():
        checkbox_to_select.set_checked(True)
        logger.debug(f"Checked checkbox: {checkbox_to_select}")


def navigate_to_home_page(page: Page) -> None:
    """
    Navigate to the ewm home page.
    
    Ported from TypeScript: navigateToHomePage()
    
    Args:
        page: Playwright Page object
    """
    base_url = os.getenv('APP_BASE_URL', 'https://test11.ewealthmanager.com')
    home_url = f"{base_url}/en.aspx"
    page.goto(home_url)
    page.wait_for_load_state("domcontentloaded")
    logger.debug(f"Navigated to home page: {home_url}")


def navigate_to_portfolio_engine(page: Page) -> Page:
    """
    Navigate to Portfolio Engine from eWM.
    Opens Portfolio Engine in a new popup window.
    
    Ported from TypeScript: navigateToPortfolioEngine()
    Selectors from EwmPage and PortfolioEnginePage POMs
    
    Args:
        page: The main page object
        
    Returns:
        The Portfolio Engine page object (new popup window)
    """
    from pages.PROPOSAL.ewm_page import EwmPage
    
    logger.debug("Navigating to Portfolio Engine...")
    
    # Create EwmPage instance to access selectors from POM
    ewm_page = EwmPage(page)
    
    # Click Investments link
    ewm_page.investments_link.click()
    logger.debug("Clicked Investments link")
    
    # Click PortfolioEngine link
    ewm_page.portfolio_engine_link.click()
    logger.debug("Clicked PortfolioEngine link")
    
    # Set up popup listener before clicking Launch
    with page.context.expect_page() as popup_info:
        # Click Launch Portfolio Engine button
        ewm_page.launch_portfolio_engine_img.click()
        logger.debug("Clicked Launch Portfolio Engine button")
    
    # Get the new popup page
    portfolio_engine_page = popup_info.value
    page.wait_for_load_state()
    
    logger.debug("Portfolio Engine page opened in popup")
    return portfolio_engine_page


