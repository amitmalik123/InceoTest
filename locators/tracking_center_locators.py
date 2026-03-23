"""
Locators for Tracking Center Page

This module contains all locator definitions for the Tracking Center page.
"""

from typing import Dict
from playwright.sync_api import Page, Locator

def initialize_locators(page: Page) -> Dict[str, Locator]:
    """
    Initialize and return all locators for Tracking Center page.
    
    Args:
        page: Playwright Page object
        
    Returns:
        Dictionary containing all locators
    """
    return {
        "roth_str_label": page.get_by_text("Roth Conversion"),
        "logout_link": page.get_by_role("link", name="Logout"),
        "bodycontent_div": page.locator("div#BodyContent"),
    }
