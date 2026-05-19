"""
EXAMPLE: How to use AllureLogger in Page Objects and Utilities.

This demonstrates how pages and utilities can contribute to Allure reports
without tight coupling to the test framework.
"""

import pytest
from playwright.sync_api import Locator, Page

from utils.allure_logger import get_allure_logger

# ============================================================================
# EXAMPLE 1: Page Object with AllureLogger
# ============================================================================


class AccountListPage:
    """Account List Page Object - with integrated logging and Allure reporting"""

    def __init__(self, page: Page):
        self.page = page
        # Each page gets its own logger
        self.logger = get_allure_logger(self.__class__.__name__)

        # Locators
        self.search_input = page.locator("#client-search")
        self.account_link = page.locator(".account-row")

    def search_client(self, client_id: str) -> None:
        """Search for a client by ID"""
        # No need for allure.step here - steps should be in test files
        # Just log the action
        self.logger.info(f"Searching for client: {client_id}")

        try:
            self.search_input.fill(client_id)
            self.search_input.press("Enter")
            self.logger.info(f"Search completed for: {client_id}")
        except Exception as e:
            # Errors automatically attach to Allure
            self.logger.error(f"Search failed: {str(e)}")
            raise

    def select_account(self, account_name: str, client_id: str) -> None:
        """Select an account from the list"""
        self.logger.info(f"Selecting account: {account_name} for client: {client_id}")

        account_selector = f"text={account_name}"
        account = self.page.locator(account_selector).first

        if not account.is_visible():
            self.logger.warning(f"Account {account_name} not visible, waiting...")
            account.wait_for(state="visible", timeout=10000)

        account.click()
        self.logger.info(f"Account {account_name} selected successfully")


# ============================================================================
# EXAMPLE 2: Utility Function with AllureLogger
# ============================================================================


class DatabaseHelper:
    """Database utility with integrated logging"""

    def __init__(self):
        self.logger = get_allure_logger(self.__class__.__name__)

    def get_user_data(self, user_id: str) -> dict:
        """Fetch user data from database"""
        self.logger.info(f"Fetching data for user: {user_id}")

        try:
            # Simulate database query
            user_data = {"id": user_id, "name": "John Doe", "email": "john@example.com"}

            # Attach data to Allure report (useful for debugging)
            self.logger.attach_json(user_data, f"User Data - {user_id}")

            self.logger.info(f"Successfully fetched data for user: {user_id}")
            return user_data

        except Exception as e:
            self.logger.error(f"Database query failed for user {user_id}: {str(e)}")
            raise


# ============================================================================
# EXAMPLE 3: API Utility with AllureLogger
# ============================================================================


class APIClient:
    """API client with integrated logging and Allure reporting"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.logger = get_allure_logger(self.__class__.__name__)

    def create_account(self, account_data: dict) -> dict:
        """Create account via API"""
        self.logger.info(f"Creating account via API: {account_data.get('name')}")

        # Log request details (automatically attaches to Allure)
        self.logger.attach_json(account_data, "API Request - Create Account")

        try:
            # Simulate API call
            response = {"status": "success", "account_id": "ACC123"}

            # Log response
            self.logger.attach_json(response, "API Response - Create Account")
            self.logger.info(f"Account created successfully: {response['account_id']}")

            return response

        except Exception as e:
            self.logger.error(f"API call failed: {str(e)}")
            raise


# ============================================================================
# EXAMPLE 4: BasePage with AllureLogger
# ============================================================================


class BasePage:
    """Base Page with unified logging"""

    def __init__(self, page: Page):
        self.page = page
        # Use class name for logger
        self.logger = get_allure_logger(self.__class__.__name__)

    def click(self, locator: Locator, timeout: int = 10000) -> None:
        """Click an element with auto-healing and logging"""
        self.logger.info("Clicking element")

        try:
            locator.wait_for(state="visible", timeout=timeout)
            locator.click()
            self.logger.info("Click successful")

        except Exception as e:
            # Warning automatically attaches to Allure
            self.logger.warning(f"Click failed: {str(e)}")
            self.logger.info("🔧 Attempting auto-healing...")

            # Auto-healing logic here...
            raise

    def fill(self, locator: Locator, value: str) -> None:
        """Fill input with logging"""
        self.logger.info(f"Filling field with value: {value}")

        try:
            locator.fill(value)
            self.logger.info("Fill successful")
        except Exception as e:
            self.logger.error(f"Fill failed: {str(e)}")
            raise


# ============================================================================
# EXAMPLE 5: Using in Conftest/Fixtures
# ============================================================================

logger = get_allure_logger("fixtures")


@pytest.fixture
def authenticated_page(page: Page):
    """Fixture that provides an authenticated page"""
    with logger.step("Setup authenticated session"):
        logger.info("Loading authentication state")

        try:
            # Load session storage
            page.goto("https://example.com")
            logger.attach_screenshot(page, "Initial Page Load")

            # Verify authentication
            if "login" not in page.url.lower():
                logger.info("✓ Authentication successful")
            else:
                logger.error("Authentication failed - still on login page")
                raise AssertionError("Authentication failed")

            yield page

        finally:
            logger.info("Tearing down authenticated session")
