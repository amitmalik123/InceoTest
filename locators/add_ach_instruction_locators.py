"""
Locators for Add ACH Instruction Page

This module contains all locator definitions for the Add ACH Instruction page.
"""

from typing import Dict
from playwright.sync_api import Page, Locator

def initialize_locators(page: Page) -> Dict[str, Locator]:
    """
    Initialize and return all locators for Add ACH Instruction page.
    
    Args:
        page: Playwright Page object
        
    Returns:
        Dictionary containing all locators
    """
    return {
        "routing_number": page.locator('input[maxlength="9"][inputmode="numeric"]'),
        "bank_account_number": page.locator('[aria-label="Bank-AccountNumber"] input'),
        "confirm_bank_account_number": page.locator('[aria-label="Confirm-BankAccount-Number"] input'),
        "verify_button": page.locator("span:text('Verify')"),
        "bank_name_display": page.locator("span:text('Bank Name') + span"),
        "name_on_bank_account": page.locator('[aria-label="Bank-Account-OwnerName"] textarea[aria-invalid]'),
        "additional_bank_account_owner_name": page.get_by_placeholder("Additional Bank Account Owner Name"),
        "checking_radio": page.get_by_role("radio", name="Checking"),
        "savings_radio": page.get_by_role("radio", name="Savings"),
        "investment_account_checkbox": page.get_by_test_id("checkbox").locator("input[type='checkbox']"),
        "account_name_list": page.get_by_test_id("account-details").locator("span").first,
        "next_button": page.get_by_role("button", name="Next"),
    }
