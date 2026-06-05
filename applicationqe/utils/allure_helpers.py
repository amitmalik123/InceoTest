"""
Allure helper utilities for assertions and screenshots.

Usage:
    from utils.allure_helpers import assert_visible, assert_title, assert_url, assert_text, screenshot

    assert_title(page, "My Page Title")
    assert_visible(page, page.get_by_text("Dashboard"), "Dashboard heading")
    assert_text(page, page.locator("#msg"), "Success")
    assert_url(page, ".*dashboard.*")
    screenshot(page, "After Login")
"""

import re
import allure
from playwright.sync_api import Page, expect


def screenshot(page: Page, name: str = "Screenshot"):
    """Capture a screenshot and attach it to the Allure report."""
    img = page.screenshot()
    allure.attach(img, name=name, attachment_type=allure.attachment_type.PNG)
    print(f"  ≡ƒô╕ {name}")


def _run_assertion(page: Page, step_label: str, assertion_fn):
    """Internal: run an assertion inside an Allure step with auto failure screenshot."""
    with allure.step(step_label):
        try:
            assertion_fn()
            print(f"  Γ£ô {step_label}")
        except Exception:
            screenshot(page, f"FAIL - {step_label}")
            raise


def assert_visible(page: Page, locator, step: str = "", timeout: int = 10000):
    """Assert a locator is visible.

    Usage: assert_visible(page, page.get_by_text("Hello"), "Greeting visible")
    """
    label = step or "Element is visible"
    _run_assertion(page, label, lambda: expect(
        locator).to_be_visible(timeout=timeout))


def assert_not_visible(page: Page, locator, step: str = "", timeout: int = 5000):
    """Assert a locator is NOT visible.

    Usage: assert_not_visible(page, page.get_by_text("Error"), "No error shown")
    """
    label = step or "Element is not visible"
    _run_assertion(page, label, lambda: expect(
        locator).not_to_be_visible(timeout=timeout))


def assert_title(page: Page, expected_title: str, step: str = ""):
    """Assert page title matches.

    Usage: assert_title(page, "My App")
    """
    label = step or f"Page title is '{expected_title}'"
    _run_assertion(page, label, lambda: expect(
        page).to_have_title(expected_title))


def assert_url(page: Page, url_pattern: str, step: str = "", timeout: int = 10000):
    """Assert page URL matches a regex pattern.

    Usage: assert_url(page, ".*dashboard.*")
    """
    label = step or f"URL matches '{url_pattern}'"
    _run_assertion(page, label, lambda: expect(page).to_have_url(
        re.compile(url_pattern, re.IGNORECASE), timeout=timeout))


def assert_text(page: Page, locator, expected_text: str, step: str = "", exact: bool = False, timeout: int = 10000):
    """Assert a locator has specific text.

    Usage: assert_text(page, page.locator("#msg"), "Success")
    """
    label = step or f"Element has text '{expected_text}'"
    if exact:
        _run_assertion(page, label, lambda: expect(
            locator).to_have_text(expected_text, timeout=timeout))
    else:
        _run_assertion(page, label, lambda: expect(
            locator).to_contain_text(expected_text, timeout=timeout))


def assert_checked(page: Page, locator, step: str = "", timeout: int = 5000):
    """Assert a checkbox/radio is checked.

    Usage: assert_checked(page, page.get_by_role("checkbox"))
    """
    label = step or "Element is checked"
    _run_assertion(page, label, lambda: expect(
        locator).to_be_checked(timeout=timeout))


def assert_enabled(page: Page, locator, step: str = "", timeout: int = 5000):
    """Assert a locator is enabled.

    Usage: assert_enabled(page, page.get_by_role("button", name="Submit"))
    """
    label = step or "Element is enabled"
    _run_assertion(page, label, lambda: expect(
        locator).to_be_enabled(timeout=timeout))
