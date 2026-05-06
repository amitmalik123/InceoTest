"""
Locators for Change Investments Page

This module contains all locator definitions for the Change Investments page.
"""

from typing import Dict
from playwright.sync_api import Page, Locator

def initialize_locators(page: Page) -> Dict[str, Locator]:
    """
    Initialize and return all locators for Change Investments page.
    
    Args:
        page: Playwright Page object
        
    Returns:
        Dictionary containing all locators
    """
    return {
        "account_wizard_link": page.locator("#clientDetailAccountDetailAnchor"),
        "change_investments_link": page.get_by_role("link", name="Change Investments", exact=True),
        "next_button": page.get_by_role("button", name="Next"),
        "back_button": page.get_by_role("button", name="Back"),
        "investment_action_modal": page.locator("#InvestmentActionModal"),
        "radio_destination_investment": page.locator("input[name='action'][value='DestinationInvestment']"),
        "radio_modify_allocations": page.locator("input[name='action'][value='ModifyAllocations']"),
        "modal_ok_button": page.locator("#InvestmentActionModal").get_by_role("button", name="OK"),
        "modal_cancel_button": page.locator("#InvestmentActionModal").get_by_role("button", name="Cancel"),
        "step_investment_selection": page.get_by_text("Investment Selection", exact=True),
        "step_account_number": page.get_by_text("Account Number", exact=True),
        "completion_modal": page.locator("#eSigConfirmModal, .modal:has-text('Investment Change Completed')"),
    }
