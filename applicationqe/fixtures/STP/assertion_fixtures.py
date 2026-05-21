"""
Assertion and Test Utility Fixtures

This module contains:
- soft_assert fixture (auto-validating soft assertions)
- reset_step_screenshot_counter fixture (screenshot counter reset)

These fixtures provide assertion utilities and test setup helpers.
"""

import pytest

from utils.allure_logger import reset_step_counter
from utils.assertions import SoftAssertions


@pytest.fixture
def soft_assert():
    """
    Auto-validating soft assertions fixture.

    Collects multiple assertion failures and raises them all together
    at the end of the test. No need to manually call assert_all().

    Usage:
        def test_profile(page, soft_assert):
            page.goto("/profile")

            # All assertions are collected
            soft_assert.assert_equal(page.locator("#name").inner_text(), "John")
            soft_assert.assert_equal(page.locator("#email").inner_text(), "john@test.com")
            soft_assert.assert_true(page.locator("#verified").is_visible())

            # Automatically validates all assertions at test end
            # If any failed, raises AssertionError with all failures listed

    Available methods:
        - assert_equal(actual, expected, message=None)
        - assert_not_equal(actual, expected, message=None)
        - assert_true(condition, message=None)
        - assert_false(condition, message=None)
        - assert_in(item, container, message=None)
        - assert_not_in(item, container, message=None)
    """
    soft = SoftAssertions()
    yield soft
    # Automatically validate all assertions after test completes
    soft.assert_all()


@pytest.fixture(autouse=True)
def reset_step_screenshot_counter():
    """Automatically reset step counter before each test"""
    reset_step_counter()
    yield
