"""
Locators for Account Wizard Page

This module contains all locator definitions for the Account Wizard page.
"""

from typing import Dict
from playwright.sync_api import Page, Locator

def initialize_locators(page: Page) -> Dict[str, Locator]:
    """
    Initialize and return all locators for Account Wizard page.
    
    Args:
        page: Playwright Page object
        
    Returns:
        Dictionary containing all locators
    """
    return {
        "account_wizard_link": page.get_by_role("link", name="Account Wizard"),
        "account_wizard_header": page.get_by_role("heading", name="Account Wizard"),
        "selected_account_label": page.locator("div.radio:has(span.checked) + label"),
        "client_name": page.locator("[data-testid='client-name'], .client-name, h2.client-name"),
    }
