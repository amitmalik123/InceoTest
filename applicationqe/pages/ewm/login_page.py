"""Merged EWM login page object with legacy login helpers."""

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, expect

from pages.base_page import BasePage
from pages.ewm.locators.login_locators import LoginLocators
from utils.logger import setup_logger

logger = setup_logger(__name__)

class LoginPage(BasePage):
    """Page object for login functionality with broad backward compatibility."""

    PAGE_PATH = "ewmLogin/account/login"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)
        self.locators = LoginLocators()
        self.allow_all_button: Locator = page.get_by_role("button", name="Allow All")
        self.accept_all_button: Locator = page.locator("#ketch-banner-button-primary")
        self.username_input_field: Locator = page.locator("input#okta-signin-username")
        self.password_input_field: Locator = page.locator("input#okta-signin-password")
        self.sign_in_button: Locator = page.locator("input#okta-signin-submit")
        self.login_form: Locator = page.locator(
            "form#form32.primary-auth-form.o-form.o-form-edit-mode"
        )
        self.onetrust_accept_button: Locator = page.locator("#accept-recommended-btn-handler")
        self.onetrust_overlay: Locator = page.locator("div.onetrust-pc-dark-filter")

    def _resolve_login_url(self) -> str:
        if self.base_url:
            return f"{self.base_url.rstrip('/')}/{self.PAGE_PATH.lstrip('/')}"
        return self.PAGE_PATH

    def navigate(self) -> None:
        url = self._resolve_login_url()
        logger.info(f"Navigating to login page: {url}")
        self.page.goto(url)
        try:
            if self.accept_all_button.is_visible(timeout=2000):
                logger.info("Ketch Accept All button found")
            elif self.allow_all_button.is_visible(timeout=1000):
                logger.info("Allow All button found")
            else:
                logger.info("No cookie consent button present (session may already exist)")
        except Exception:
            logger.info("No cookie consent button present (session may already exist)")
        logger.info("Login page loaded successfully")

    def navigate_to_login(self, url: str) -> None:
        """Navigate to the login page"""
        logger.info(f"Navigating to login page: {url}")
        self.navigate_to(url)
        self.wait_for_load_state("domcontentloaded")

    def accept_cookies(self) -> None:
        logger.info("Accepting cookies")
        try:
            if self.accept_all_button.is_visible(timeout=2000):
                self.accept_all_button.click(timeout=3000)
                logger.info("Ketch Accept All button clicked")
                return
        except Exception:
            pass
        try:
            self.allow_all_button.click(timeout=2000)
        except Exception:
            logger.info("No cookie consent button available (already accepted or session exists)")

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
        if username_field.count() > 0:
            self.fill(username_field, username)
        else:
            self.fill(self.username_input_field, username)

    def enter_password(self, password: str) -> None:
        """Enter password in the login form"""
        self.logger.info("Entering password")
        password_field = self.page.locator(self.locators.PASSWORD_FIELD)
        if password_field.count() > 0:
            self.fill(password_field, password)
        else:
            self.fill(self.password_input_field, password)

    def click_sign_in(self) -> None:
        """Click sign in button and wait for navigation"""
        self.logger.info("Clicking sign in button")
        sign_in_button = self.page.locator(self.locators.SIGN_IN_BUTTON)

        try:
            with self.page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                if sign_in_button.count() > 0:
                    self.click(sign_in_button)
                else:
                    self.click(self.sign_in_button)
        except PlaywrightTimeoutError:
            self.logger.warning(
                "Sign-in did not trigger timed navigation; continuing with post-click waits"
            )
            if sign_in_button.count() > 0:
                self.click(sign_in_button)
            else:
                self.click(self.sign_in_button)
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                pass

        self.logger.info(f"Navigation completed. Current URL: {self.page.url}")

    def dismiss_onetrust(self) -> None:
        """Dismiss OneTrust cookie consent overlay if present (appears after login)."""
        try:
            if self.onetrust_accept_button.is_visible(timeout=5000):
                self.click(self.onetrust_accept_button)
                logger.info("OneTrust 'Allow All' button clicked")
                self.onetrust_overlay.wait_for(state="hidden", timeout=5000)
                return
        except Exception:
            pass

        try:
            self.page.evaluate("document.querySelector('#onetrust-accept-btn-handler')?.click()")
            self.onetrust_overlay.wait_for(state="hidden", timeout=3000)
            logger.info("OneTrust consent dismissed via JS fallback")
        except Exception:
            logger.info("No OneTrust consent overlay present")

    def submit_login_form(self) -> None:
        logger.info("Form submission triggered by sign-in button")
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        logger.info(f"Final login URL: {self.page.url}")

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

    def verify_account_src(self, expected: str) -> None:
        logger.info(f"Verifying account source: {expected}")
        account_src_label = self.page.get_by_text(expected)
        expect(account_src_label).to_have_text(expected)
        logger.info(f"Account source {expected} verified")

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

    # --- Method migrated from pages.stp.shared.login_page ---

    def navigate_to_new_nav(self) -> None:
        from config.settings import get_settings
        new_nav_url = getattr(get_settings(), 'new_nav_url', None) or self._resolve_login_url()
        logger.info(f"Navigating to new nav page: {new_nav_url}")
        self.page.goto(new_nav_url)
        self.dismiss_cookie_banner()
        logger.info("New nav page loaded successfully")
