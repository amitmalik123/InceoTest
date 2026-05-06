"""
Locators for Clients Page

This module contains all locator definitions for the Clients page.
"""

from typing import Callable
from playwright.sync_api import Page, Locator

def initialize_locators(page: Page) -> dict:
    """
    Initialize and return all locators for Clients page.
    
    Args:
        page: Playwright Page object
        
    Returns:
        Dictionary containing all locators
    """
    return {
        "clients_link": page.get_by_role("link", name="Clients", exact=True),
        "account_list_link": page.get_by_role("link", name="Account List", exact=True),
    }
