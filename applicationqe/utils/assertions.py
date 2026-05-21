"""
Custom Assertion Utilities

Provides both hard and soft assertion capabilities for test validation.
Hard assertions fail immediately, while soft assertions collect all failures.
"""

import logging
from typing import Any, Callable, List, Optional

import allure
from playwright.sync_api import Locator, Page, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class SoftAssertionError(AssertionError):
    """Raised by SoftAssertions.assert_all() when one or more soft checks fail.

    Inherits from the built-in ``AssertionError`` so that pytest treats it as a
    test *failure* (not an unexpected error) and rich assertion introspection
    still works.
    """


class SoftAssertions:
    """
    Collect multiple assertion failures before raising.

    Use as context manager or manually call assert_all().

    Example:
        with SoftAssertions() as soft:
            soft.assert_equal(actual, expected, "Value mismatch")
            soft.assert_true(condition, "Condition failed")
            # All failures reported together
    """

    def __init__(self):
        self.errors: List[str] = []
        self._assertion_count = 0

    def __enter__(self):
        """Enter context manager"""
        self.errors.clear()
        self._assertion_count = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and raise if failures exist"""
        if exc_type is None:  # Only check assertions if no other exception
            self.assert_all()
        return False

    def _record_failure(self, message: str):
        """Record a failed assertion"""
        self._assertion_count += 1
        error_msg = f"Assertion #{self._assertion_count}: {message}"
        self.errors.append(error_msg)

        # Log to both standard logger and Allure report
        logger.warning(f"Soft assertion failed: {message}")
        allure.attach(
            message,
            name=f"Soft Assertion Failure #{self._assertion_count}",
            attachment_type=allure.attachment_type.TEXT,
        )

    def assert_all(self):
        """
        Raise exception if any assertions failed.

        Raises:
            SoftAssertionError: With all collected failures
        """
        if self.errors:
            error_summary = f"\n{len(self.errors)} soft assertion(s) failed:\n"
            error_summary += "\n".join(f"  {i + 1}. {err}" for i, err in enumerate(self.errors))

            # Log error summary
            logger.error(error_summary)

            # Attach summary to Allure report
            allure.attach(
                error_summary,
                name="Soft Assertions Summary",
                attachment_type=allure.attachment_type.TEXT,
            )

            raise SoftAssertionError(error_summary)

    def assert_equal(self, actual: Any, expected: Any, message: Optional[str] = None):
        """Assert two values are equal"""
        if actual != expected:
            msg = message or f"Expected '{expected}', but got '{actual}'"
            self._record_failure(msg)

    def assert_not_equal(self, actual: Any, expected: Any, message: Optional[str] = None):
        """Assert two values are not equal"""
        if actual == expected:
            msg = message or f"Expected values to be different, but both are '{actual}'"
            self._record_failure(msg)

    def assert_true(self, condition: bool, message: Optional[str] = None):
        """Assert condition is True"""
        if not condition:
            msg = message or "Expected condition to be True, but was False"
            self._record_failure(msg)

    def assert_false(self, condition: bool, message: Optional[str] = None):
        """Assert condition is False"""
        if condition:
            msg = message or "Expected condition to be False, but was True"
            self._record_failure(msg)

    def assert_in(self, item: Any, container: Any, message: Optional[str] = None):
        """Assert item is in container"""
        if item not in container:
            msg = message or f"Expected '{item}' to be in '{container}'"
            self._record_failure(msg)

    def assert_not_in(self, item: Any, container: Any, message: Optional[str] = None):
        """Assert item is not in container"""
        if item in container:
            msg = message or f"Expected '{item}' to not be in '{container}'"
            self._record_failure(msg)

    def assert_greater(self, actual: Any, expected: Any, message: Optional[str] = None):
        """Assert actual > expected"""
        if not actual > expected:
            msg = message or f"Expected {actual} > {expected}"
            self._record_failure(msg)

    def assert_greater_equal(self, actual: Any, expected: Any, message: Optional[str] = None):
        """Assert actual >= expected"""
        if not actual >= expected:
            msg = message or f"Expected {actual} >= {expected}"
            self._record_failure(msg)

    def assert_less(self, actual: Any, expected: Any, message: Optional[str] = None):
        """Assert actual < expected"""
        if not actual < expected:
            msg = message or f"Expected {actual} < {expected}"
            self._record_failure(msg)

    def assert_less_equal(self, actual: Any, expected: Any, message: Optional[str] = None):
        """Assert actual <= expected"""
        if not actual <= expected:
            msg = message or f"Expected {actual} <= {expected}"
            self._record_failure(msg)

    def assert_is_none(self, value: Any, message: Optional[str] = None):
        """Assert value is None"""
        if value is not None:
            msg = message or f"Expected None, but got '{value}'"
            self._record_failure(msg)

    def assert_is_not_none(self, value: Any, message: Optional[str] = None):
        """Assert value is not None"""
        if value is None:
            msg = message or "Expected value to not be None"
            self._record_failure(msg)

    def assert_contains_text(
        self, text: str, substring: str, message: Optional[str] = None, case_sensitive: bool = True
    ):
        """Assert text contains substring"""
        if case_sensitive:
            contains = substring in text
        else:
            contains = substring.lower() in text.lower()

        if not contains:
            msg = message or f"Expected '{text}' to contain '{substring}'"
            self._record_failure(msg)

    def assert_starts_with(self, text: str, prefix: str, message: Optional[str] = None):
        """Assert text starts with prefix"""
        if not text.startswith(prefix):
            msg = message or f"Expected '{text}' to start with '{prefix}'"
            self._record_failure(msg)

    def assert_ends_with(self, text: str, suffix: str, message: Optional[str] = None):
        """Assert text ends with suffix"""
        if not text.endswith(suffix):
            msg = message or f"Expected '{text}' to end with '{suffix}'"
            self._record_failure(msg)

    def assert_length(self, container: Any, expected_length: int, message: Optional[str] = None):
        """Assert container has expected length"""
        actual_length = len(container)
        if actual_length != expected_length:
            msg = message or f"Expected length {expected_length}, but got {actual_length}"
            self._record_failure(msg)

    def assert_empty(self, container: Any, message: Optional[str] = None):
        """Assert container is empty"""
        if len(container) != 0:
            msg = message or f"Expected empty container, but has {len(container)} items"
            self._record_failure(msg)

    def assert_not_empty(self, container: Any, message: Optional[str] = None):
        """Assert container is not empty"""
        if len(container) == 0:
            msg = message or "Expected non-empty container"
            self._record_failure(msg)

    # Playwright-specific soft assertions
    def assert_visible(self, locator: Locator, message: Optional[str] = None):
        """Assert element is visible"""
        try:
            if not locator.is_visible():
                msg = message or f"Expected element to be visible: {locator}"
                self._record_failure(msg)
        except Exception as e:
            self._record_failure(f"Error checking visibility: {str(e)}")

    def assert_hidden(self, locator: Locator, message: Optional[str] = None):
        """Assert element is hidden"""
        try:
            if locator.is_visible():
                msg = message or f"Expected element to be hidden: {locator}"
                self._record_failure(msg)
        except Exception as e:
            self._record_failure(f"Error checking visibility: {str(e)}")

    def assert_enabled(self, locator: Locator, message: Optional[str] = None):
        """Assert element is enabled"""
        try:
            if not locator.is_enabled():
                msg = message or f"Expected element to be enabled: {locator}"
                self._record_failure(msg)
        except Exception as e:
            self._record_failure(f"Error checking enabled state: {str(e)}")

    def assert_disabled(self, locator: Locator, message: Optional[str] = None):
        """Assert element is disabled"""
        try:
            if locator.is_enabled():
                msg = message or f"Expected element to be disabled: {locator}"
                self._record_failure(msg)
        except Exception as e:
            self._record_failure(f"Error checking enabled state: {str(e)}")

    def assert_text(self, locator: Locator, expected_text: str, message: Optional[str] = None):
        """Assert element has exact text"""
        try:
            actual_text = locator.inner_text()
            if actual_text != expected_text:
                msg = message or f"Expected text '{expected_text}', but got '{actual_text}'"
                self._record_failure(msg)
        except Exception as e:
            self._record_failure(f"Error getting text: {str(e)}")

    def assert_text_contains(self, locator: Locator, text: str, message: Optional[str] = None):
        """Assert element text contains substring"""
        try:
            actual_text = locator.inner_text()
            if text not in actual_text:
                msg = message or f"Expected text to contain '{text}', but got '{actual_text}'"
                self._record_failure(msg)
        except Exception as e:
            self._record_failure(f"Error getting text: {str(e)}")

    def assert_attribute(
        self,
        locator: Locator,
        attribute: str,
        expected_value: str,
        message: Optional[str] = None,
    ):
        """Assert element attribute has expected value"""
        try:
            actual_value = locator.get_attribute(attribute)
            if actual_value != expected_value:
                msg = (
                    message
                    or f"Expected attribute '{attribute}' to be '{expected_value}', but got '{actual_value}'"
                )
                self._record_failure(msg)
        except Exception as e:
            self._record_failure(f"Error getting attribute: {str(e)}")

    def assert_count(self, locator: Locator, expected_count: int, message: Optional[str] = None):
        """Assert element count matches expected"""
        try:
            actual_count = locator.count()
            if actual_count != expected_count:
                msg = message or f"Expected {expected_count} elements, but found {actual_count}"
                self._record_failure(msg)
        except Exception as e:
            self._record_failure(f"Error getting count: {str(e)}")

    def assert_url(
        self, page: Page, expected_url: str, message: Optional[str] = None, exact: bool = True
    ):
        """Assert page URL matches expected"""
        try:
            actual_url = page.url
            if exact:
                matches = actual_url == expected_url
            else:
                matches = expected_url in actual_url

            if not matches:
                msg = message or f"Expected URL '{expected_url}', but got '{actual_url}'"
                self._record_failure(msg)
        except Exception as e:
            self._record_failure(f"Error getting URL: {str(e)}")

    def assert_title(self, page: Page, expected_title: str, message: Optional[str] = None):
        """Assert page title matches expected"""
        try:
            actual_title = page.title()
            if actual_title != expected_title:
                msg = message or f"Expected title '{expected_title}', but got '{actual_title}'"
                self._record_failure(msg)
        except Exception as e:
            self._record_failure(f"Error getting title: {str(e)}")


class Assertions:
    """
    Hard assertions that fail immediately.
    Wrapper around standard assertions with better error messages.
    Logs every assertion result to Allure as 'Assertion Passed/Failed'.

    Example:
        Assertions.assert_equal(actual, expected, "Values should match")
        Assertions.assert_equals("Client name", expected="John", actual="John")
    """

    @staticmethod
    def _log(message: str, passed: bool) -> None:
        status = "Passed" if passed else "Failed"
        step_title = f"Assertion {status}:  '{message}'"
        (logger.info if passed else logger.error)(step_title)
        with allure.step(step_title):
            pass

    @staticmethod
    def assert_equal(actual: Any, expected: Any, message: Optional[str] = None):
        """Assert two values are equal (fails immediately)"""
        msg = message or f"Expected '{expected}', but got '{actual}'"
        assert actual == expected, msg

    @staticmethod
    def assert_not_equal(actual: Any, expected: Any, message: Optional[str] = None):
        """Assert two values are not equal"""
        msg = message or f"Expected values to be different, but both are '{actual}'"
        Assertions._log(msg, actual != expected)
        assert actual != expected, msg

    @staticmethod
    def assert_true(condition: bool, message: Optional[str] = None):
        """Assert condition is True"""
        msg = message or "Expected condition to be True, but was False"
        Assertions._log(msg, bool(condition))
        assert condition, msg

    @staticmethod
    def assert_false(condition: bool, message: Optional[str] = None):
        """Assert condition is False"""
        msg = message or "Expected condition to be False, but was True"
        Assertions._log(msg, not condition)
        assert not condition, msg

    @staticmethod
    def assert_in(item: Any, container: Any, message: Optional[str] = None):
        """Assert item is in container"""
        msg = message or f"Expected '{item}' to be in '{container}'"
        Assertions._log(msg, item in container)
        assert item in container, msg

    @staticmethod
    def assert_not_in(item: Any, container: Any, message: Optional[str] = None):
        """Assert item is not in container"""
        msg = message or f"Expected '{item}' to not be in '{container}'"
        Assertions._log(msg, item not in container)
        assert item not in container, msg

    @staticmethod
    def assert_greater(actual: Any, expected: Any, message: Optional[str] = None):
        """Assert actual > expected"""
        msg = message or f"Expected {actual} > {expected}"
        Assertions._log(msg, actual > expected)
        assert actual > expected, msg

    @staticmethod
    def assert_less(actual: Any, expected: Any, message: Optional[str] = None):
        """Assert actual < expected"""
        msg = message or f"Expected {actual} < {expected}"
        Assertions._log(msg, actual < expected)
        assert actual < expected, msg

    @staticmethod
    def assert_is_none(value: Any, message: Optional[str] = None):
        """Assert value is None"""
        msg = message or f"Expected None, but got '{value}'"
        Assertions._log(msg, value is None)
        assert value is None, msg

    @staticmethod
    def assert_is_not_none(value: Any, message: Optional[str] = None):
        """Assert value is not None"""
        msg = message or "Expected value to not be None"
        Assertions._log(msg, value is not None)
        assert value is not None, msg

    @staticmethod
    def assert_contains_text(
        text: str, substring: str, message: Optional[str] = None, case_sensitive: bool = True
    ):
        """Assert text contains substring"""
        if case_sensitive:
            contains = substring in text
        else:
            contains = substring.lower() in text.lower()
        msg = message or f"Expected '{text}' to contain '{substring}'"
        Assertions._log(msg, contains)
        assert contains, msg

    @staticmethod
    def assert_length(container: Any, expected_length: int, message: Optional[str] = None):
        """Assert container has expected length"""
        actual_length = len(container)
        msg = message or f"Expected length {expected_length}, but got {actual_length}"
        Assertions._log(msg, actual_length == expected_length)
        assert actual_length == expected_length, msg

    @staticmethod
    def assert_equals(message: str = "", expected: Any = None, actual: Any = None) -> None:
        """Assert expected == actual (case-insensitive for strings). Java AssertService style."""
        exp, act = str(expected).strip(), str(actual).strip()
        match = exp.lower() == act.lower()
        detail = f"{message} : Actual = '{act}', Expected = '{exp}'" if message else f"'{exp}'(expected) {'==' if match else '!='} '{act}'(actual)"
        Assertions._log(detail, match)
        assert match, detail

    @staticmethod
    def fail(message: str) -> None:
        Assertions._log(message, False)
        assert False, message

    @staticmethod
    def assert_element_text(locator: Locator, expected_text: str, exact: bool = False) -> bool:
        actual_text = (locator.text_content() or "").strip()
        if exact:
            result = actual_text == expected_text
        else:
            result = expected_text.lower() in actual_text.lower()
        msg = f"Expected text '{expected_text}' not found. Got: '{actual_text}'"
        Assertions._log(msg, result)
        assert result, msg
        return True

    @staticmethod
    def assert_element_visible(locator: Locator, should_be_visible: bool = True, timeout: int = 5000) -> bool:
        try:
            locator.wait_for(state="visible", timeout=timeout)
            is_visible = True
        except PlaywrightTimeoutError:
            is_visible = False
        msg = f"Element visibility: expected visible={should_be_visible}, got={is_visible}"
        Assertions._log(msg, is_visible == should_be_visible)
        assert is_visible == should_be_visible, msg
        return True

    @staticmethod
    def assert_page_loaded(required_elements: list) -> bool:
        all_visible = True
        for locator in required_elements:
            try:
                locator.wait_for(state="visible", timeout=5000)
            except PlaywrightTimeoutError:
                all_visible = False
        msg = "Not all required page elements loaded"
        Assertions._log(msg, all_visible)
        assert all_visible, msg
        return True

    # Playwright-specific hard assertions (using Playwright's expect)
    @staticmethod
    def assert_visible(locator: Locator, message: Optional[str] = None, timeout: int = 5000):
        """Assert element is visible"""
        try:
            expect(locator).to_be_visible(timeout=timeout)
        except AssertionError:
            msg = message or f"Expected element to be visible: {locator}"
            raise AssertionError(msg)

    @staticmethod
    def assert_hidden(locator: Locator, message: Optional[str] = None, timeout: int = 5000):
        """Assert element is hidden"""
        try:
            expect(locator).to_be_hidden(timeout=timeout)
        except AssertionError:
            msg = message or f"Expected element to be hidden: {locator}"
            raise AssertionError(msg)

    @staticmethod
    def assert_enabled(locator: Locator, message: Optional[str] = None, timeout: int = 5000):
        """Assert element is enabled"""
        try:
            expect(locator).to_be_enabled(timeout=timeout)
        except AssertionError:
            msg = message or f"Expected element to be enabled: {locator}"
            raise AssertionError(msg)

    @staticmethod
    def assert_text(
        locator: Locator, expected_text: str, message: Optional[str] = None, timeout: int = 5000
    ):
        """Assert element has exact text"""
        try:
            expect(locator).to_have_text(expected_text, timeout=timeout)
        except AssertionError:
            actual = locator.inner_text()
            msg = message or f"Expected text '{expected_text}', but got '{actual}'"
            raise AssertionError(msg)

    @staticmethod
    def assert_text_contains(
        locator: Locator, text: str, message: Optional[str] = None, timeout: int = 5000
    ):
        """Assert element text contains substring"""
        try:
            expect(locator).to_contain_text(text, timeout=timeout)
        except AssertionError:
            actual = locator.inner_text()
            msg = message or f"Expected text to contain '{text}', but got '{actual}'"
            raise AssertionError(msg)

    @staticmethod
    def assert_count(
        locator: Locator, expected_count: int, message: Optional[str] = None, timeout: int = 5000
    ):
        """Assert element count matches expected"""
        try:
            expect(locator).to_have_count(expected_count, timeout=timeout)
        except AssertionError:
            actual = locator.count()
            msg = message or f"Expected {expected_count} elements, but found {actual}"
            raise AssertionError(msg)

    @staticmethod
    def assert_url(
        page: Page, expected_url: str, message: Optional[str] = None, timeout: int = 5000
    ):
        """Assert page URL matches expected"""
        try:
            expect(page).to_have_url(expected_url, timeout=timeout)
        except AssertionError:
            actual = page.url
            msg = message or f"Expected URL '{expected_url}', but got '{actual}'"
            raise AssertionError(msg)

    @staticmethod
    def assert_title(
        page: Page, expected_title: str, message: Optional[str] = None, timeout: int = 5000
    ):
        """Assert page title matches expected"""
        try:
            expect(page).to_have_title(expected_title, timeout=timeout)
        except AssertionError:
            actual = page.title()
            msg = message or f"Expected title '{expected_title}', but got '{actual}'"
            raise AssertionError(msg)


def verify_all(assertions: Callable[[SoftAssertions], None]):
    """
    Decorator for running multiple soft assertions.

    Example:
        @verify_all
        def verify_dashboard(soft: SoftAssertions):
            soft.assert_visible(page.locator("#header"))
            soft.assert_text(page.locator("#title"), "Dashboard")
            soft.assert_count(page.locator(".widget"), 5)
    """

    def wrapper():
        with SoftAssertions() as soft:
            assertions(soft)

    return wrapper
