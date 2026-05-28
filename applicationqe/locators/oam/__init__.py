"""
Locators Package - OAM

This package contains all locator definitions for OAM page objects.
Each module corresponds to a page object and contains all locators for that page.

Usage:
    from locators.oam import item_detail_locators
    status_locator = item_detail_locators.STATUS_LABEL

    from locators.oam import login_locators
    locators = login_locators.initialize_locators(page)
    username_field = locators["username_input_field"]
"""

__all__ = [
    "account_detail_locators",
    "account_list_locators",
    "account_management_locators",
    "account_wizard_locators",
    "add_ach_instruction_locators",
    "change_investments_locators",
    "client_accounts_locators",
    "clients_locators",
    "docusign_locators",
    "item_detail_locators",
    "login_locators",
    "manage_instruction_1_locators",
    "manage_instruction_2_locators",
    "outlook_locators",
    "roth_conversion_locators",
    "tracking_center_locators",
]
