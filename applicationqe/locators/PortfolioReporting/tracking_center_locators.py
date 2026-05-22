from typing import Dict

from playwright.sync_api import Locator, Page


def initialize_locators(page: Page) -> Dict[str, Locator]:
    return {
        "roth_str_label": page.get_by_text("Roth Conversion"),
        "logout_link": page.get_by_role("link", name="Logout"),
        "bodycontent_div": page.locator("div#BodyContent"),
    }