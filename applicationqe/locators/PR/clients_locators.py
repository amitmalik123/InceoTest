from typing import Dict

from playwright.sync_api import Locator, Page


def initialize_locators(page: Page) -> Dict[str, Locator]:
    return {
        "clients_link": page.get_by_role("link", name="Clients", exact=True),
        "account_list_link": page.get_by_role("link", name="Account List", exact=True),
    }
