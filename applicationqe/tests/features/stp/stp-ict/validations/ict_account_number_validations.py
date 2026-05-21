from playwright.sync_api import Page, expect

from locators.stp.stp_ict.ict_account_number_locators import ICTAccountNumberLocators


class AccountNumberValidations:
    def __init__(self, page: Page):
        self.page = page
        self.locators = ICTAccountNumberLocators()

    def validate_retain_selected(self) -> None:
        """Assert that the 'Retain Account Number' radio input is checked."""
        locator = self.page.locator(self.locators.RETAIN_RADIO['css']).first
        expect(locator).to_be_checked()

    def validate_new_account_selected(self) -> None:
        """Assert that the 'New Account Number' radio input is checked."""
        locator = self.page.locator(self.locators.NEW_RADIO['css']).first
        expect(locator).to_be_checked()
