# ============================================================================
# ADD TO tests/conftest.py
# ============================================================================
"""
Step-level Screenshot Configuration

Add this to your tests/conftest.py file to enable automatic screenshots
after each BDD step.
"""

import pytest

from utils.allure_logger import enable_step_screenshots, reset_step_counter

# ============================================================================
# 1. Add pytest option for command-line control
# ============================================================================


def pytest_addoption(parser):
    """
    Add command-line options for step screenshots.

    Usage:
        pytest --screenshot-each-step              # Screenshot after every step
        pytest                                      # Only screenshot on failure (default)
    """
    parser.addoption(
        "--screenshot-each-step",
        action="store_true",
        default=False,
        help="Take screenshot after each BDD step (can be slow)",
    )


# ============================================================================
# 2. Configure at session start
# ============================================================================


def pytest_configure(config):
    """Configure screenshot settings from command line or environment"""
    import os

    # Check command-line option
    screenshot_each_step = config.getoption("--screenshot-each-step", default=False)

    # Check environment variable (takes precedence)
    env_value = os.getenv("SCREENSHOT_EACH_STEP", "").lower()
    if env_value in ("true", "1", "yes", "on"):
        screenshot_each_step = True

    # Enable/disable
    enable_step_screenshots(screenshot_each_step)

    # Print configuration
    status = "ENABLED for ALL steps" if screenshot_each_step else "ENABLED on failure only"
    print(f"\n{'=' * 60}")
    print(f"📸 Step Screenshots: {status}")
    print(f"{'=' * 60}\n")


# ============================================================================
# 3. Auto-reset step counter for each test
# ============================================================================


@pytest.fixture(autouse=True)
def reset_step_screenshot_counter():
    """Automatically reset step counter before each test"""
    reset_step_counter()
    yield


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
# Method 1: Command-line
# pytest --screenshot-each-step
#
# Method 2: Environment variable
# export SCREENSHOT_EACH_STEP=true
# pytest
#
# Method 3: In conftest.py programmatically
# from utils.allure_logger import enable_step_screenshots
#
# enable_step_screenshots(True)
#
# Method 4: Per-test control
# def test_something(page):
#     from utils.allure_logger import enable_step_screenshots
#     enable_step_screenshots(True)  # Enable for this test only
#     # ... test code ...


# ============================================================================
# STEP FILE USAGE
# ============================================================================
# Old approach (manual screenshot)
# @when("I search for the client")
# def search_for_client(page, account_list_page, test_context):
#     with allure.step("Search for client"):
#         account_list_page.search_client(client_id)
#         screenshot = page.screenshot()
#         allure.attach(screenshot, name="After Search", ...)
#
# # New approach (auto-screenshot)
# from utils.allure_logger import get_allure_logger
#
# logger = get_allure_logger(__name__)
#
# @when("I search for the client")
# def search_for_client(page, account_list_page, test_context):
#     client_id = test_context['test_data']['client_id']
#
#     # Auto-screenshot if page is passed
#     with logger.step("Search for client", page=page):
#         logger.info(f"Searching for: {client_id}")
#         account_list_page.search_client(client_id)
#         # Screenshot automatically taken here (if enabled)
#
# # Or without auto-screenshot for specific step
# @when("I navigate to menu")
# def navigate_menu(page):
#     with logger.step("Navigate to menu", page=page, auto_screenshot=False):
#         # ... no screenshot taken ...
#         pass
