"""
Locators for Roth Conversion Page

This module contains all locator definitions for the Roth Conversion page.
"""

from typing import Dict
from playwright.sync_api import Page, Locator

def initialize_locators(page: Page) -> Dict[str, Locator]:
    """
    Initialize and return all locators for Roth Conversion page.
    
    Args:
        page: Playwright Page object
        
    Returns:
        Dictionary containing all locators
    """
    return {
        "destination_account_div": page.locator("div.css-1z0509q"),
        "convert_portion_span": page.get_by_text("Convert a Portion of the Account"),
        "portion_radio_input": page.locator("input.PrivateSwitchBase-input.css-1m9pwf3[name='radio-buttons-group'][value='portion']"),
        "amount_input_field": page.locator('input[type="text"].MuiInputBase-input.MuiOutlinedInput-input.MuiInputBase-inputAdornedStart'),
        "do_not_withhold_span": page.get_by_text("Do not withhold"),
        "do_not_withhold_radio_input": page.locator("input.PrivateSwitchBase-input.css-1m9pwf3[name='radio-buttons-group'][value='do_not_withhold']"),
        "str_message_paragraph": page.get_by_text("Your request will require additional review to ensure the existing source and/or destination account is still eligible due to recent actions on the account(s). Please refer to the Tracking Center for any additional requirements and an updated status."),
        "str_button": page.get_by_role("button", name="SUBMIT TO REVIEW"),
        "next_button": page.get_by_role("button", name="Next"),
    }
