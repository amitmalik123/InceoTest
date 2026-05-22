from playwright.sync_api import Page, expect


class TrackingCenterValidations:
    def __init__(self, page: Page):
        self.page = page

    def validate_account_src(self, expected: str) -> None:
        locator = self.page.get_by_text(expected)
        expect(locator.first).to_have_text(expected)

    def validate_roth_str(self, expected: str) -> None:
        locator = self.page.get_by_text(expected)
        expect(locator.first).to_have_text(expected)
