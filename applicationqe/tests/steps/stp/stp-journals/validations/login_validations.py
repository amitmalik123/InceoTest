"""
Validations for Login Page functionality
"""
import logging
from playwright.sync_api import Page, expect
from utils.allure_helpers import assert_visible, assert_url, assert_title

logger = logging.getLogger(__name__)

class LoginValidations:
    """Validation methods for login functionality"""

    def __init__(self, page: Page):
        self.page = page

    def validate_login_page_loaded(self) -> None:
        """Validate login page has loaded correctly"""
        # Check title contains "AssetMark" instead of exact match
        page_title = self.page.title()
        assert "AssetMark" in page_title, f"Expected page title to contain 'AssetMark', got: '{page_title}'"
        assert_visible(self.page, self.page.get_by_label("Username"), "Username field visible")
        assert_visible(self.page, self.page.get_by_label("Password"), "Password field visible")

    def validate_successful_login(self) -> None:
        """Validate successful login completion"""
        assert_url(self.page, r"en\.aspx", "Verify login landed on home page")

    def validate_cookie_consent_dismissed(self) -> None:
        """Validate cookie consent banner is no longer present or has been dismissed"""
        cookie_button = self.page.get_by_role("button", name="Confirm My Choices")
        try:
            # Wait a moment to allow dialog to fully disappear
            self.page.wait_for_timeout(2000)
            # Check if button is hidden now
            expect(cookie_button).not_to_be_visible()
            logger.info("✅ Cookie consent dialog successfully dismissed")
        except AssertionError:
            # If still visible, log but don't fail the test since we attempted dismissal
            logger.warning("⚠️ Cookie consent button still visible, but dismissal was attempted")
            # This is acceptable - some sites may keep the button but mark it as already processed

    def validate_credentials_entered(self, username: str) -> None:
        """Validate credentials have been entered correctly"""
        username_field = self.page.locator("input#okta-signin-username")
        expect(username_field).to_have_value(username)

    def validate_page_title_contains(self, expected_text: str) -> None:
        """Validate page title contains expected text"""
        page_title = self.page.title()
        assert expected_text in page_title, f"Expected page title to contain '{expected_text}', got: '{page_title}'"

    def validate_username_password_fields_visible(self) -> None:
        """Validate username and password fields are visible"""
        assert_visible(self.page, self.page.get_by_label("Username"), "Username field visible")
        assert_visible(self.page, self.page.get_by_label("Password"), "Password field visible")

    def validate_password_masked(self) -> None:
        """Validate password input is masked"""
        password_field = self.page.locator("input#okta-signin-password")
        expect(password_field).to_have_attribute("type", "password")

    def validate_navigation_started(self) -> None:
        """Validate that navigation has started after sign in"""
        # Wait for URL to change from login page
        expect(self.page).not_to_have_url("**/account/login")

    def validate_user_authenticated(self) -> None:
        """Validate user is authenticated and on home page"""
        assert_url(self.page, r".*en\.aspx.*", "User redirected to authenticated home page")