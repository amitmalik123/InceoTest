"""
BDD Step Screenshot Hook - Automatic screenshots after each step (optional)

This module provides:
1. Screenshot after EVERY step (when enabled)
2. Screenshot on FAILED steps (always)
3. Toggle control via environment variable or pytest option
"""

import os

import allure
import pytest
from playwright.sync_api import Page


class StepScreenshotConfig:
    """Configuration for step-level screenshots"""

    def __init__(self):
        # Check environment variable first, then default to False
        env_value = os.getenv("SCREENSHOT_EACH_STEP", "false").lower()
        self.screenshot_each_step = env_value in ("true", "1", "yes", "on")
        self.screenshot_on_failure = True  # Always enabled
        self.step_counter = 0

    def should_take_screenshot(self, step_failed: bool = False) -> bool:
        """Determine if screenshot should be taken"""
        if step_failed:
            return self.screenshot_on_failure
        return self.screenshot_each_step


# Global configuration instance
_config = StepScreenshotConfig()


def pytest_addoption(parser):
    """Add command-line option for step screenshots"""
    parser.addoption(
        "--screenshot-each-step",
        action="store_true",
        default=False,
        help="Take screenshot after each BDD step (can be slow)",
    )
    parser.addoption(
        "--no-screenshot-on-failure",
        action="store_true",
        default=False,
        help="Disable automatic screenshot on step failure",
    )


def pytest_configure(config):
    """Configure screenshot settings from command line"""
    global _config

    # Override with command-line option if provided
    if config.getoption("--screenshot-each-step"):
        _config.screenshot_each_step = True

    if config.getoption("--no-screenshot-on-failure"):
        _config.screenshot_on_failure = False

    # Print configuration
    print(f"\n{'=' * 60}")
    print("📸 Screenshot Configuration:")
    print(f"  - After each step: {_config.screenshot_each_step}")
    print(f"  - On failure: {_config.screenshot_on_failure}")
    print(f"{'=' * 60}\n")


@pytest.fixture(autouse=True)
def step_screenshot_tracker(request):
    """
    Fixture that automatically takes screenshots after BDD steps.

    Usage is automatic - no need to add to step functions.
    """
    # This fixture is autouse, so it runs for every test
    # We'll use it to track step execution
    yield

    # After test completion, reset counter
    global _config
    _config.step_counter = 0


def take_step_screenshot(
    page: Page, step_name: str, step_type: str = "when", step_failed: bool = False
) -> None:
    """
    Take screenshot after a step and attach to Allure.

    Args:
        page: Playwright Page object
        step_name: Name of the step (e.g., "I search for the client")
        step_type: Type of step (given/when/then)
        step_failed: Whether the step failed

    Usage in step file:
        from utils.bdd_screenshot_hook import take_step_screenshot

        @when("I search for the client")
        def search_client(page, account_list_page, test_context):
            try:
                # ... step logic ...
                account_list_page.search_client(client_id)
            finally:
                take_step_screenshot(page, "I search for the client", "when")
    """
    global _config

    if not _config.should_take_screenshot(step_failed):
        return

    try:
        _config.step_counter += 1

        # Create descriptive name
        status = "❌ FAILED" if step_failed else "✓"
        screenshot_name = f"Step {_config.step_counter} [{step_type.upper()}] {status} {step_name}"

        # Take and attach screenshot
        screenshot = page.screenshot()
        allure.attach(screenshot, name=screenshot_name, attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        print(f"Warning: Failed to take step screenshot: {e}")


def get_screenshot_config() -> StepScreenshotConfig:
    """Get the current screenshot configuration"""
    return _config
