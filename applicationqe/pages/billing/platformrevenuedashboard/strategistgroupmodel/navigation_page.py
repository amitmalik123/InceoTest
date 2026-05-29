"""Navigation page object for Strategist Group Model."""

from playwright.sync_api import Page

from pages.base_page import BasePage


class NavigationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_strategist_group_model(self):
        self.page.get_by_role("link", name="Strategist Group Model").click()
        self.page.wait_for_load_state("domcontentloaded")
