"""
Assertion and Test Utility Fixtures

This module contains:
- soft_assert fixture (auto-validating soft assertions)
- reset_step_screenshot_counter fixture (screenshot counter reset)

These fixtures provide assertion utilities and test setup helpers.
"""

from collections.abc import Generator

import pytest

from utils.allure_logger import reset_step_counter
from utils.soft_assertions_enhanced import EnhancedSoftAssertions


@pytest.fixture
def soft_assert() -> Generator[EnhancedSoftAssertions, None, None]:
    """
    Auto-validating soft assertions fixture.

    Collects multiple assertion failures and raises them all together
    at the end of the test. No need to manually call assert_all().

    Usage:
        def test_profile(authenticated_page, soft_assert):
            authenticated_page.goto("/profile")

            # All assertions are collected
            soft_assert.assert_equal(authenticated_page.locator("#name").inner_text(), "John")
            soft_assert.assert_equal(authenticated_page.locator("#email").inner_text(), "john@test.com")
            soft_assert.assert_true(authenticated_page.locator("#verified").is_visible())

            # Automatically validates all assertions at test end
            # If any failed, raises SoftAssertionWarning (test stays PASSED with yellow warning)

    Available methods:
        - assert_equal(actual, expected, message=None)
        - assert_not_equal(actual, expected, message=None)
        - assert_true(condition, message=None)
        - assert_false(condition, message=None)
        - assert_in(item, container, message=None)
        - assert_not_in(item, container, message=None)
        - assert_visible(locator, message=None)
        - assert_count(locator, expected_count, message=None)
        - assert_text_contains(locator, text, message=None)
    """
    soft = EnhancedSoftAssertions()
    yield soft
    # Automatically validate all assertions after test completes
    soft.assert_all()


@pytest.fixture(autouse=True)
def reset_step_screenshot_counter() -> Generator[None, None, None]:
    """Automatically reset step counter before each test"""
    reset_step_counter()
    yield
