"""
Adhesion-specific Login Page Object

Extends LoginPage to support Okta-based authentication used by Adhesion.
This POM detects and uses Okta-specific selectors when available, falling back
to label-based locators for compatibility.
"""

from playwright.sync_api import Page

from pages.login_page import LoginPage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class AdhesionLoginPage(LoginPage):
    """
    Adhesion Login Page with Okta support.

    Overrides locators to detect and prefer Okta-specific input IDs while
    maintaining fallback to label-based locators for robustness.
    """

    def __init__(self, page: Page, base_url: str = ""):
        # Initialize parent with default label-based locators
        super().__init__(page, base_url=base_url)

        # Override with Okta-specific selectors, falling back to inherited defaults
        try:
            username_candidate = page.locator("input#okta-signin-username")
            if username_candidate.count() > 0:
                self.username_input_field = username_candidate
                logger.info("Using Okta username selector")
        except Exception as e:
            logger.info(f"Okta username selector not found, using fallback: {e}")

        try:
            password_candidate = page.locator("input#okta-signin-password")
            if password_candidate.count() > 0:
                self.password_input_field = password_candidate
                logger.info("Using Okta password selector")
        except Exception as e:
            logger.info(f"Okta password selector not found, using fallback: {e}")
