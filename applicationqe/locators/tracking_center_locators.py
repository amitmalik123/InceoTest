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
        "client_search_input": page.locator("#client_search_input"),
        "search_button": page.locator("#searchbutton"),
        "tracking_center_link": page.locator('a[href="/AccountsAnalysis/TrackingCenter"]'),
    }


# D-Number table row locator - dynamically created with d_number value
def get_d_number_table_row_locator(page: Page, d_number: str) -> Locator:
    """
    Get locator for table row with D-number.
    
    Uses multiple strategies:
    1. Row with matching id attribute (tr#D003525811)
    2. Row containing a cell with matching text content
    
    Args:
        page: Playwright Page object
        d_number: D-number string (e.g., "D003525811")
        
    Returns:
        Locator for the table row matching the D-number
    """
    # Primary: tr with id matching D-number
    # Fallback: tr containing a td/cell with the D-number text
    return page.locator(f"tr#{d_number}, tr:has(td:text-is('{d_number}'))").first
