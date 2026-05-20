from typing import Dict

from playwright.sync_api import Locator, Page


def initialize_locators(page: Page) -> Dict[str, Locator]:
    return {
        "switch_id_link": page.locator("//ul[@id='userMenu']/li/a[text()='Switch ID']"),
        "lookup_user_id_input": page.locator(
            "//input[@name='ctl00$cphContentArea$txtLookUp']"
            " | //input[@id='ctl00_cphContentArea_txtLookUp']"
            " | //input[contains(@name,'txtLookUp')]"
            " | //input[contains(@id,'txtLookUp')]"
        ).first,
        "find_button": page.locator(
            "#ctl00_cphContentArea_btnLookUp, "
            "button[id*='btnLookUp'], "
            "input[id*='btnLookUp'], "
            "button:has-text('Find')"
        ).first,
        "results_row": page.locator("//td[text()='Agent']/parent::tr"),
        "sso_user_link": page.locator("//td[text()='Agent']/parent::tr/td[6]/a[1]"),
        "name_user_link": page.locator("//td[text()='Agent']/parent::tr/td[2]/a[1]"),
    }
