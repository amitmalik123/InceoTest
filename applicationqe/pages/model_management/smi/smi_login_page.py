from typing import Optional

from playwright.sync_api import Page

from pages.ewm.base_page import BasePage
from pages.model_management.smi.locators import login_locators


class SMILoginPage(BasePage):
    """Locators and URL constants for the SMI login page."""

    USERNAME_INPUT = login_locators.USERNAME_INPUT
    PASSWORD_INPUT = login_locators.PASSWORD_INPUT
    LOGIN_BUTTON   = login_locators.LOGIN_BUTTON

    def __init__(self, page: Page, base_url: Optional[str] = None):
        super().__init__(page, base_url)
