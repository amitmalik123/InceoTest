from typing import Dict

from playwright.sync_api import Locator, Page


def initialize_locators(page: Page) -> Dict[str, Locator]:
    return {
        "account_wizard_link": page.locator("#clientDetailAccountDetailAnchor"),
        "funded_radio_input": page.locator(
            "input#ctl00_cphContentArea_rdlAccountList_1[type='radio']"
        ),
        "move_assets_between_accounts_list_item": page.get_by_text(
            "Move Assets Between Accounts"
        ),
        "roth_ira_conversion_list_item": page.locator("#lstSubCategory5"),
        "next_button": page.get_by_role("button", name="Next"),
    }
