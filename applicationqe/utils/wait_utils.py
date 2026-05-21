"""
Custom Wait Utilities

Provides flexible waiting mechanisms beyond standard Playwright waits.
"""

import logging
import time
from typing import Any, Callable, Optional, TypeVar

from playwright.sync_api import Locator, Page

logger = logging.getLogger(__name__)

T = TypeVar("T")


class WaitTimeoutError(Exception):
    """Raised when wait condition times out"""


def wait_for_condition(
    condition: Callable[[], bool],
    timeout: float = 30.0,
    poll_interval: float = 0.5,
    error_message: str = "Condition not met within timeout",
) -> bool:
    """
    Wait for a custom condition to be true.

    Args:
        condition: Callable that returns boolean
        timeout: Maximum time to wait in seconds
        poll_interval: Time between condition checks
        error_message: Error message if timeout

    Returns:
        True if condition met

    Raises:
        WaitTimeoutError: If condition not met within timeout

    Example:
        wait_for_condition(
            lambda: page.locator("#count").inner_text() == "10",
            timeout=10.0
        )
    """
    start_time = time.time()
    last_exception = None

    while (time.time() - start_time) < timeout:
        try:
            if condition():
                elapsed = time.time() - start_time
                logger.debug(f"Condition met after {elapsed:.2f}s")
                return True
        except Exception as e:
            last_exception = e
            logger.debug(f"Condition check raised: {e}")

        time.sleep(poll_interval)

    elapsed = time.time() - start_time
    error_msg = f"{error_message} (waited {elapsed:.2f}s)"
    if last_exception:
        error_msg += f". Last error: {str(last_exception)}"

    logger.error(error_msg)
    raise WaitTimeoutError(error_msg)


def wait_for_value(
    getter: Callable[[], T],
    expected_value: T,
    timeout: float = 30.0,
    poll_interval: float = 0.5,
    error_message: Optional[str] = None,
) -> T:
    """
    Wait for a value to match expected value.

    Args:
        getter: Callable that returns a value
        expected_value: Expected value to match
        timeout: Maximum time to wait
        poll_interval: Time between checks
        error_message: Custom error message

    Returns:
        The expected value

    Example:
        count = wait_for_value(
            lambda: int(page.locator("#count").inner_text()),
            expected_value=100,
            timeout=10.0
        )
    """
    if error_message is None:
        error_message = f"Value did not match {expected_value}"

    def condition():
        value = getter()
        return value == expected_value

    wait_for_condition(condition, timeout, poll_interval, error_message)
    return expected_value


def wait_for_element_count(
    locator: Locator, count: int, timeout: float = 30.0, poll_interval: float = 0.5
) -> bool:
    """
    Wait for specific number of elements.

    Args:
        locator: Playwright locator
        count: Expected element count
        timeout: Maximum time to wait
        poll_interval: Time between checks

    Returns:
        True if count matches

    Example:
        wait_for_element_count(page.locator(".item"), count=5)
    """
    return wait_for_condition(
        lambda: locator.count() == count,
        timeout=timeout,
        poll_interval=poll_interval,
        error_message=f"Element count did not reach {count}",
    )


def wait_for_text_to_contain(
    locator: Locator, text: str, timeout: float = 30.0, case_sensitive: bool = True
) -> bool:
    """
    Wait for element text to contain specific text.

    Args:
        locator: Playwright locator
        text: Text to wait for
        timeout: Maximum time to wait
        case_sensitive: Case-sensitive comparison

    Returns:
        True if text found

    Example:
        wait_for_text_to_contain(page.locator("#status"), "Success")
    """

    def condition():
        actual_text = locator.inner_text()
        if case_sensitive:
            return text in actual_text
        return text.lower() in actual_text.lower()

    return wait_for_condition(
        condition, timeout=timeout, error_message=f"Text '{text}' not found in element"
    )


def wait_for_text_to_change(
    locator: Locator, initial_text: Optional[str] = None, timeout: float = 30.0
) -> str:
    """
    Wait for element text to change from initial value.

    Args:
        locator: Playwright locator
        initial_text: Initial text (if None, will be fetched)
        timeout: Maximum time to wait

    Returns:
        New text value

    Example:
        new_text = wait_for_text_to_change(page.locator("#counter"))
    """
    if initial_text is None:
        initial_text = locator.inner_text()

    def condition():
        return locator.inner_text() != initial_text

    wait_for_condition(condition, timeout=timeout, error_message="Text did not change")

    return locator.inner_text()


def wait_for_attribute_value(
    locator: Locator, attribute: str, value: str, timeout: float = 30.0
) -> bool:
    """
    Wait for element attribute to have specific value.

    Args:
        locator: Playwright locator
        attribute: Attribute name
        value: Expected attribute value
        timeout: Maximum time to wait

    Returns:
        True if attribute matches

    Example:
        wait_for_attribute_value(page.locator("#input"), "disabled", "true")
    """
    return wait_for_condition(
        lambda: locator.get_attribute(attribute) == value,
        timeout=timeout,
        error_message=f"Attribute '{attribute}' did not match '{value}'",
    )


def wait_for_class_to_contain(locator: Locator, class_name: str, timeout: float = 30.0) -> bool:
    """
    Wait for element to have specific CSS class.

    Args:
        locator: Playwright locator
        class_name: CSS class name to wait for
        timeout: Maximum time to wait

    Returns:
        True if class found

    Example:
        wait_for_class_to_contain(page.locator("#button"), "active")
    """

    def condition():
        class_attr = locator.get_attribute("class") or ""
        return class_name in class_attr.split()

    return wait_for_condition(
        condition, timeout=timeout, error_message=f"Class '{class_name}' not found"
    )


def wait_for_url_to_match(
    page: Page, pattern: str, timeout: float = 30.0, exact: bool = False
) -> bool:
    """
    Wait for page URL to match pattern.

    Args:
        page: Playwright page
        pattern: URL pattern to match
        timeout: Maximum time to wait
        exact: Exact match vs contains

    Returns:
        True if URL matches

    Example:
        wait_for_url_to_match(page, "/dashboard", timeout=10.0)
    """

    def condition():
        current_url = page.url
        if exact:
            return current_url == pattern
        return pattern in current_url

    return wait_for_condition(
        condition, timeout=timeout, error_message=f"URL did not match '{pattern}'"
    )


def wait_for_download(page: Page, trigger_action: Callable, timeout: float = 30.0) -> Any:
    """
    Wait for download to start.

    Args:
        page: Playwright page
        trigger_action: Action that triggers download
        timeout: Maximum time to wait

    Returns:
        Download object

    Example:
        download = wait_for_download(
            page,
            lambda: page.click("#download-btn"),
            timeout=10.0
        )
    """
    with page.expect_download(timeout=timeout * 1000) as download_info:
        trigger_action()
    return download_info.value


def wait_for_network_idle(page: Page, timeout: float = 30.0, idle_time: float = 0.5) -> bool:
    """
    Wait for network to be idle (no requests for specified time).

    Args:
        page: Playwright page
        timeout: Maximum time to wait
        idle_time: Time with no requests to consider idle

    Returns:
        True when network is idle

    Example:
        wait_for_network_idle(page, timeout=10.0)
    """
    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout * 1000)
        return True
    except Exception as e:
        logger.warning(f"Network idle wait failed: {str(e).splitlines()[0]}")
        return False


def wait_for_console_message(
    page: Page, text_pattern: str, timeout: float = 30.0, message_type: Optional[str] = None
) -> bool:
    """
    Wait for console message matching pattern.

    Args:
        page: Playwright page
        text_pattern: Text pattern to match
        timeout: Maximum time to wait
        message_type: Filter by type (log, error, warning)

    Returns:
        True if message found

    Example:
        wait_for_console_message(page, "API call successful", timeout=5.0)
    """
    message_found = False

    def on_console(msg):
        nonlocal message_found
        if message_type and msg.type != message_type:
            return
        if text_pattern in msg.text:
            message_found = True

    page.on("console", on_console)

    try:
        wait_for_condition(
            lambda: message_found,
            timeout=timeout,
            error_message=f"Console message '{text_pattern}' not found",
        )
        return True
    finally:
        page.remove_listener("console", on_console)


class WaitContext:
    """
    Context manager for custom waits with automatic cleanup.

    Example:
        with WaitContext(timeout=10.0, poll_interval=0.5) as wait:
            wait.until(lambda: element.is_visible())
            wait.until_text_contains(locator, "Complete")
    """

    def __init__(self, timeout: float = 30.0, poll_interval: float = 0.5):
        self.timeout = timeout
        self.poll_interval = poll_interval

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def until(self, condition: Callable[[], bool], error_message: str = "Condition not met"):
        """Wait until condition is true"""
        return wait_for_condition(
            condition,
            timeout=self.timeout,
            poll_interval=self.poll_interval,
            error_message=error_message,
        )

    def until_visible(self, locator: Locator):
        """Wait until element is visible"""
        return self.until(lambda: locator.is_visible(), error_message="Element not visible")

    def until_hidden(self, locator: Locator):
        """Wait until element is hidden"""
        return self.until(lambda: not locator.is_visible(), error_message="Element not hidden")

    def until_enabled(self, locator: Locator):
        """Wait until element is enabled"""
        return self.until(lambda: locator.is_enabled(), error_message="Element not enabled")

    def until_text_contains(self, locator: Locator, text: str):
        """Wait until element text contains text"""
        return self.until(
            lambda: text in locator.inner_text(), error_message=f"Text '{text}' not found"
        )


def wait_for_element_stable(
    locator: Locator,
    timeout: float = 15.0,
    check_animations: bool = True,
    check_enabled: bool = False,
) -> Locator:
    """
    Wait for a Playwright locator to be fully stable (attached, visible, animations done).

    Args:
        locator: Playwright Locator to wait on
        timeout: Maximum time in seconds
        check_animations: Whether to wait for CSS animations to finish
        check_enabled: Whether to also wait for the element to be enabled

    Returns:
        The same locator once stable
    """
    logger.debug(f"Waiting for element to be stable: {locator}")

    try:
        locator.wait_for(state="attached", timeout=timeout * 1000)

        wait_for_condition(
            lambda: locator.is_visible(),
            timeout=timeout,
            poll_interval=0.5,
            error_message="Element not visible after being attached",
        )

        if check_animations:
            wait_for_condition(
                lambda: locator.evaluate("el => el.getAnimations().length === 0"),
                timeout=5.0,
                poll_interval=0.3,
                error_message="Element animations did not complete",
            )

        if check_enabled:
            wait_for_condition(
                lambda: locator.is_enabled(),
                timeout=timeout,
                poll_interval=0.5,
                error_message="Element not enabled",
            )

        logger.info("Element is stable and ready for interaction")
        return locator

    except Exception as e:
        logger.error(f"Element stability check failed: {str(e)}")
        raise WaitTimeoutError(f"Element did not become stable: {str(e)}")


def wait_for_spa_ready(page: Page, timeout: float = 30.0) -> bool:
    """
    Wait for a Single Page Application to finish loading.

    Checks DOM load state, network idle, and common loading spinner selectors.

    Args:
        page: Playwright Page
        timeout: Maximum time in seconds

    Returns:
        True if ready, False if a non-critical check failed
    """
    logger.debug("Waiting for SPA to be ready")

    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout * 1000)
        wait_for_network_idle(page, timeout=timeout)

        common_loading_selectors = [
            "[data-testid='loading-spinner']",
            ".loading-spinner",
            ".spinner",
            "[aria-busy='true']",
            ".loader",
        ]

        for selector in common_loading_selectors:
            loader = page.locator(selector)
            if loader.count() > 0:
                wait_for_condition(
                    lambda: not loader.is_visible(),
                    timeout=10.0,
                    poll_interval=0.5,
                    error_message=f"Loading indicator {selector} did not disappear",
                )

        logger.info("SPA is ready for interaction")
        return True

    except Exception as e:
        logger.warning(f"SPA ready check encountered issue: {e}")
        return False


def wait_for_dynamic_element(
    page: Page,
    selector: str,
    max_attempts: int = 5,
    attempt_timeout: float = 5.0,
    wait_between_attempts: float = 1.0,
) -> Locator:
    """
    Retry locating and stabilising a dynamically rendered element.

    Args:
        page: Playwright Page
        selector: CSS/XPath selector
        max_attempts: Number of retries before raising
        attempt_timeout: Per-attempt timeout in seconds
        wait_between_attempts: Sleep between retries in seconds

    Returns:
        Stable Playwright Locator
    """
    logger.debug(f"Waiting for dynamic element: {selector} (max attempts: {max_attempts})")
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            locator = page.locator(selector).first
            wait_for_element_stable(locator, timeout=attempt_timeout)
            logger.info(f"Dynamic element found and stable on attempt {attempt}")
            return locator
        except Exception as e:
            last_error = e
            logger.debug(f"Attempt {attempt}/{max_attempts} failed: {str(e)}")
            if attempt < max_attempts:
                time.sleep(wait_between_attempts)
                wait_for_network_idle(page, timeout=5.0)

    raise WaitTimeoutError(
        f"Element '{selector}' did not become stable after {max_attempts} attempts. "
        f"Last error: {last_error}"
    )
