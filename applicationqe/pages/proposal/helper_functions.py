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
    from config.proposal.settings import get_settings
    
    settings = get_settings()
    home_url = settings.get_app_config("ewm")["home_url"]
    page.goto(home_url)
    page.wait_for_load_state("domcontentloaded")
    logger.debug(f"Navigated to home page: {home_url}")


def navigate_to_portfolio_engine(page: Page, is_navbar: bool = False) -> Page:
    """
    Navigate to Portfolio Engine from eWM.
    Supports both:
    - Legacy path: Investments → Portfolio Engine link → Launch img (test11, silo, prod)
    - Navbar path: [navbar-specific navigation] (test01)

    Portfolio Engine opens in a new tab; the new page object is returned.

    Args:
        page: The main page object (Dashboard)
        is_navbar: Whether this is a navbar environment

    Returns:
        page: The new Portfolio Engine page object (new tab)
    """
    from pages.proposal.ewm_page import EwmPage

    logger.debug(f"Navigating to Portfolio Engine (navbar={is_navbar})...")

    ewm_page = EwmPage(page)

    if is_navbar:
        # Navbar path (test01): Investments → Portfolio Engine button → same tab
        logger.debug("Attempting navbar path: Investments → Portfolio Engine button...")
        ewm_page.investments_link.click()
        logger.debug("Clicked Investments link")
        page.wait_for_load_state("domcontentloaded")

        ewm_page.portfolio_engine_nav_button.click()
        logger.debug("Clicked Portfolio Engine nav button")
        page.wait_for_load_state("domcontentloaded")

        logger.debug("Portfolio Engine loaded in same tab (navbar path)")
        return page
    else:
        # Legacy path (test11, silo, prod): Investments → Portfolio Engine link → Launch img → new tab
        logger.debug("Attempting legacy path: Investments → Portfolio Engine → Launch img...")
        ewm_page.investments_link.click()
        logger.debug("Clicked Investments link")
        page.wait_for_load_state("domcontentloaded")

        ewm_page.portfolio_engine_link.click()
        logger.debug("Clicked Portfolio Engine link")
        page.wait_for_load_state("domcontentloaded")

        # Portfolio Engine launches in a new tab via the Launch img
        with page.context.expect_page() as new_page_info:
            ewm_page.launch_portfolio_engine_img.click()
            logger.debug("Clicked Launch Portfolio Engine img")

        pe_page = new_page_info.value
        pe_page.wait_for_load_state("domcontentloaded")
        logger.debug("Portfolio Engine loaded in new tab (legacy path)")
        return pe_page


def navigate_to_account_wizard(page: Page, home_url: str, is_navbar: bool) -> Page:
    """
    Navigate to Account Wizard for managing client accounts.
    Supports both:
    - Navbar path: Direct URL to /clients/manage-accounts which loads NAW in #iframeWrapper (test01)
    - Legacy path: Direct NAW URL (test11, silo, prod)
    
    Args:
        page: The main page object
        home_url: The home URL from config
        is_navbar: Whether this is a navbar environment
    
    Returns:
        page: The page object after navigating to Account Wizard
    """
    logger.debug(f"Navigating to Account Wizard (navbar={is_navbar})...")
    
    if is_navbar:
        # Navbar: Navigate directly to /clients/manage-accounts which loads NAW in #iframeWrapper
        # The iframe src is ewm.{domain}/DNeWM/NBT/list/AccountWizard.aspx
        manage_accounts_url = home_url.replace("/dashboard", "/clients/manage-accounts")
        logger.debug(f"Navigating to navbar manage-accounts: {manage_accounts_url}")
        page.goto(manage_accounts_url, wait_until="domcontentloaded")
        page.frame_locator("#iframeWrapper").locator("body").wait_for(state="visible", timeout=30000)
        logger.debug("Account Wizard loaded in iframe (navbar path)")
    else:
        # Legacy: Navigate directly to NAW URL
        account_wizard_url = home_url.replace("/en.aspx", "/DNeWM/NBT/list/AccountWizard.aspx")
        logger.debug(f"Navigating to legacy NAW URL: {account_wizard_url}")
        page.goto(account_wizard_url, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle", timeout=15000)
        logger.debug("Account Wizard loaded (legacy path)")
    
    return page

