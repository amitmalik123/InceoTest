"""
Locators for Manage Instruction 2 Page

This module contains all locator definitions for the Manage Instruction 2 page.
"""

from typing import Dict
from playwright.sync_api import Page, Locator

def initialize_locators(page: Page) -> Dict[str, Locator]:
    """
    Initialize and return all locators for Manage Instruction 2 page.
    
    Args:
        page: Playwright Page object
        
    Returns:
        Dictionary containing all locators
    """
    return {
        "add_button": page.get_by_role("button", name="Add"),
    }
