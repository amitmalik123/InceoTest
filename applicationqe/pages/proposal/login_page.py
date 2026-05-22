"""
Login Page Object Model for Proposals application.
Handles login page navigation, credential entry, and privacy banner dismissal.
"""

import logging
import os
import time
from playwright.sync_api import Locator, Page

from ..base_page import BasePage

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """Login page for eWM authentication."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.login_url = os.getenv("LOGIN_URL", "https://test11.ewealthmanager.com/eWMLogin/account/login")
        
        # Login form elements
        self.username_field: Locator = page.get_by_role("textbox", name="Username")
        self.password_field: Locator = page.get_by_role("textbox", name="Password")
        self.submit_button: Locator = page.get_by_role("button", name="Sign In")
        
        # Privacy banner
        self.privacy_reject_button: Locator = page.get_by_role("button", name="Reject")

    def goto_login_page(self) -> None:
        """Navigate to the login page."""
        logger.info(f"Navigating to login page: {self.login_url}")
        self.page.goto(self.login_url, wait_until="networkidle")

    def sign_in(self, username: str, password: str) -> None:
        """
        Sign in with provided credentials.
        Includes delays to avoid bot detection.
        
        Args:
            username: The username to enter
            password: The password to enter
        """
        logger.info(f"Signing in as {username}")
        
        # Fill username with slight delay
        self.username_field.fill(username)
        time.sleep(0.5)  # Human-like delay after typing username
        
        # Fill password with slight delay
        self.password_field.fill(password)
        time.sleep(0.5)  # Human-like delay after typing password
        
        # Small delay before clicking submit to avoid appearing like a bot
        time.sleep(1.0)
        self.submit_button.click()

    def reject_privacy_banner(self) -> None:
        """
        Reject privacy/cookie consent banner if present.
        Does not fail if banner is not visible.
        """
        try:
            if self.privacy_reject_button.is_visible(timeout=5000):
                logger.info("Rejecting privacy banner")
                self.privacy_reject_button.click()
        except Exception:
            logger.debug("Privacy banner not present or could not be dismissed")
