from typing import Dict

from playwright.sync_api import Locator, Page


def initialize_locators(page: Page) -> Dict[str, Locator]:
    return {
        "clients_tab": page.locator("//a[text()='Clients']"),
        "account_list_link": page.locator("//a[text()='Account List']"),
        "search_input": page.locator("//input[@name='search_input']"),
        "search_button": page.locator("//button[@type='submit']"),
        "account_information_link": page.locator('//a[text()="Account Information"]'),
        "tax_management_service_link": page.locator("//a[text()='Tax Management Service']"),
        "account_name_header": page.locator(
            "//div[@class='account-information-content']//h1/strong"
        ),
        "account_number_header": page.locator(
            "//div[@class='account-information-content']//h1[contains(text(),'Account')]"
        ),
        "loading_spinner": page.locator(
            "//div[contains(@class,'loading-indicator-component__spinner')]"
        ),
        "loading_indicator": page.locator(
            "//*[contains(@class, 'loading-indication-component')"
            " and contains(@class, 'isVisible')]"
        ),
        "loading_modal": page.locator("#loadingImageModal"),
    }
