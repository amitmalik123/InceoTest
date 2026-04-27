"""
Enhanced Login Page Object - Handles authentication workflow actions
"""
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.ewm.locators.login_locators import LoginLocators
from typing import Optional

class LoginPage(BasePage):
    """Page object for login functionality with comprehensive cookie handling"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = LoginLocators()

    def navigate_to_login(self, url: str) -> None:
        """Navigate to the login page"""
        self.logger.info(f"Navigating to login page: {url}")
        self.navigate_to(url)
        self.wait_for_load_state("domcontentloaded")

    def dismiss_cookie_consent(self) -> bool:
        """Dismiss cookie consent banner using multiple strategies"""
        self.logger.info("Attempting to dismiss cookie consent banner")
        
        # Check if cookie consent dialog exists first
        try:
            cookie_button = self.page.get_by_role("button", name="Confirm My Choices")
            cookie_button.wait_for(state="visible", timeout=3000)
            self.logger.info("Cookie consent dialog found - 'Confirm My Choices' button visible")
        except:
            self.logger.info("No cookie consent dialog found")
            return False
        
        # Strategy 1: Direct click on "Confirm My Choices"
        try:
            cookie_button = self.page.get_by_role("button", name="Confirm My Choices")
            cookie_button.wait_for(state="visible", timeout=3000)
            cookie_button.click()
            self.logger.info("Clicked 'Confirm My Choices' button")
            
            # Wait longer for dialog to disappear and verify it's gone
            self.wait_for_timeout(3000)
            
            # Check if the button is now hidden/removed
            try:
                cookie_button.wait_for(state="hidden", timeout=5000)
                self.logger.info("Cookie consent dialog successfully dismissed - button no longer visible")
                return True
            except:
                self.logger.warning("Cookie consent button clicked but still visible")
                return True  # Still return true since we did click it
                
        except Exception as e:
            self.logger.warning(f"Failed to click 'Confirm My Choices' button: {e}")
        
        # Strategy 2: OneTrust JavaScript-based dismissal as fallback        
        if self._dismiss_onetrust_with_javascript():
            self.logger.info("Cookie consent dismissed via JavaScript")
            # Wait longer after JavaScript dismissal
            self.wait_for_timeout(3000)
            return True
        
        self.logger.info("No cookie consent banner found or could not be dismissed")
        return False

    def _dismiss_onetrust_with_javascript(self) -> bool:
        """Use JavaScript to directly dismiss OneTrust cookie banner"""
        try:
            self.wait_for_timeout(2000)  # Wait for OneTrust to potentially load
            
            js_dismissal_code = """
            (function() {
                // Look for and click OneTrust accept button
                const acceptBtn = document.querySelector('#onetrust-accept-btn-handler, .onetrust-accept-btn-handler');
                if (acceptBtn) {
                    acceptBtn.click();
                    return true;
                }
                
                // Try alternative OneTrust selectors
                const altAcceptBtn = document.querySelector('[data-optanongroupid] button, .ot-sdk-show-settings button');
                if (altAcceptBtn) {
                    altAcceptBtn.click();
                    return true;
                }
                
                // Try generic accept buttons
                const genericAccept = Array.from(document.querySelectorAll('button')).find(btn => 
                    btn.textContent.toLowerCase().includes('accept') || 
                    btn.textContent.toLowerCase().includes('allow') ||
                    btn.textContent.toLowerCase().includes('confirm')
                );
                if (genericAccept) {
                    genericAccept.click();
                    return true;
                }
                
                return false;
            })();
            """
            
            result = self.page.evaluate(js_dismissal_code)
            if result:
                self.wait_for_timeout(1000)
                return True
                
        except Exception as e:
            self.logger.warning(f"JavaScript cookie dismissal failed: {e}")
            
        return False

    def enter_username(self, username: str) -> None:
        """Enter username in the login form"""
        self.logger.info(f"Entering username: {username}")
        username_field = self.page.locator(self.locators.USERNAME_FIELD)
        self.fill(username_field, username)

    def enter_password(self, password: str) -> None:
        """Enter password in the login form"""
        self.logger.info("Entering password")
        password_field = self.page.locator(self.locators.PASSWORD_FIELD)
        self.fill(password_field, password)

    def click_sign_in(self) -> None:
        """Click sign in button and wait for navigation"""
        self.logger.info("Clicking sign in button")
        sign_in_button = self.page.locator(self.locators.SIGN_IN_BUTTON)
        
        # Click and wait for navigation
        with self.page.expect_navigation(wait_until='networkidle', timeout=self.locators.LOGIN_TIMEOUT):
            self.click(sign_in_button)
        
        self.logger.info(f"Navigation completed. Current URL: {self.page.url}")

    def complete_login(self, username: str, password: str, login_url: str) -> None:
        """Complete full login workflow"""
        self.logger.info("Starting complete login workflow")
        
        # Step 1: Navigate to login page
        self.navigate_to_login(login_url)
        
        # Step 2: Handle cookie consent
        self.dismiss_cookie_consent()
        
        # Step 3: Enter credentials
        self.enter_username(username)
        self.enter_password(password)
        
        # Step 4: Sign in
        self.click_sign_in()
        
        # Step 5: Wait for home page to load
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        self.logger.info("Complete login workflow finished")

    def is_logged_in(self) -> bool:
        """Check if user is currently logged in"""
        current_url = self.get_current_url()
        return "en.aspx" in current_url and "login" not in current_url.lower()

    def get_login_errors(self) -> list:
        """Get any login error messages"""
        error_selectors = [
            ".error-message",
            ".alert-error", 
            "[data-testid*='error']",
            ".validation-error"
        ]
        
        errors = []
        for selector in error_selectors:
            error_elements = self.page.locator(selector).all()
            for element in error_elements:
                if element.is_visible():
                    errors.append(element.text_content())
        
        return errors
