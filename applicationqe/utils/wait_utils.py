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
   
    return wait_for_condition(
        lambda: locator.count() == count,
        timeout=timeout,
        poll_interval=poll_interval,
        error_message=f"Element count did not reach {count}",
    )


def wait_for_text_to_contain(
    locator: Locator, text: str, timeout: float = 30.0, case_sensitive: bool = True
) -> bool:
    

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
   
    if initial_text is None:
        initial_text = locator.inner_text()

    def condition():
        return locator.inner_text() != initial_text

    wait_for_condition(condition, timeout=timeout, error_message="Text did not change")

    return locator.inner_text()


def wait_for_attribute_value(
    locator: Locator, attribute: str, value: str, timeout: float = 30.0
) -> bool:
   
    return wait_for_condition(
        lambda: locator.get_attribute(attribute) == value,
        timeout=timeout,
        error_message=f"Attribute '{attribute}' did not match '{value}'",
    )


def wait_for_class_to_contain(locator: Locator, class_name: str, timeout: float = 30.0) -> bool:
   

    def condition():
        class_attr = locator.get_attribute("class") or ""
        return class_name in class_attr.split()

    return wait_for_condition(
        condition, timeout=timeout, error_message=f"Class '{class_name}' not found"
    )


def wait_for_url_to_match(
    page: Page, pattern: str, timeout: float = 30.0, exact: bool = False
) -> bool:
   
    def condition():
        current_url = page.url
        if exact:
            return current_url == pattern
        return pattern in current_url

    return wait_for_condition(
        condition, timeout=timeout, error_message=f"URL did not match '{pattern}'"
    )


def wait_for_download(page: Page, trigger_action: Callable, timeout: float = 30.0) -> Any:
   
    with page.expect_download(timeout=timeout * 1000) as download_info:
        trigger_action()
    return download_info.value


def wait_for_network_idle(page: Page, timeout: float = 30.0, idle_time: float = 0.5) -> bool:
    
    try:
        page.wait_for_load_state("networkidle", timeout=timeout * 1000)
        return True
    except Exception as e:
        logger.warning(f"Network idle wait failed: {e}")
        return False


def wait_for_console_message(
    page: Page, text_pattern: str, timeout: float = 30.0, message_type: Optional[str] = None
) -> bool:
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
    logger.debug(f"Waiting for element to be stable: {locator}")
    
    try:
        # Stage 1: Wait for attached to DOM
        logger.debug("Stage 1: Waiting for element to be attached to DOM")
        locator.wait_for(state="attached", timeout=timeout * 1000)
        
        # Stage 2: Wait for visible
        logger.debug("Stage 2: Waiting for element to be visible")
        wait_for_condition(
            lambda: locator.is_visible(),
            timeout=timeout,
            poll_interval=0.5,
            error_message="Element not visible after being attached"
        )
        
        # Stage 3: Wait for animations to complete (if requested)
        if check_animations:
            logger.debug("Stage 3: Waiting for animations to complete")
            wait_for_condition(
                lambda: locator.evaluate("el => el.getAnimations().length === 0"),
                timeout=5.0,  # Shorter timeout for animations
                poll_interval=0.3,
                error_message="Element animations did not complete"
            )
        
        # Stage 4: Wait for enabled (if requested)
        if check_enabled:
            logger.debug("Stage 4: Waiting for element to be enabled")
            wait_for_condition(
                lambda: locator.is_enabled(),
                timeout=timeout,
                poll_interval=0.5,
                error_message="Element not enabled"
            )
        
        logger.info(f"Element is stable and ready for interaction")
        return locator
        
    except Exception as e:
        logger.error(f"Element stability check failed: {str(e)}")
        raise WaitTimeoutError(f"Element did not become stable: {str(e)}")


def wait_for_spa_ready(page: Page, timeout: float = 30.0) -> bool:
    
    logger.debug("Waiting for SPA to be ready")
    
    try:
        # Stage 1: DOM content loaded
        logger.debug("Stage 1: Waiting for DOM content loaded")
        page.wait_for_load_state("domcontentloaded", timeout=timeout * 1000)
        
        # Stage 2: Network idle
        logger.debug("Stage 2: Waiting for network idle")
        wait_for_network_idle(page, timeout=timeout)
        
        # Stage 3: Check for common loading indicators
        logger.debug("Stage 3: Checking for loading indicators")
        common_loading_selectors = [
            "[data-testid='loading-spinner']",
            ".loading-spinner",
            ".spinner",
            "[aria-busy='true']",
            ".loader"
        ]
        
        for selector in common_loading_selectors:
            loader = page.locator(selector)
            if loader.count() > 0:
                logger.debug(f"Found loading indicator: {selector}, waiting for it to disappear")
                wait_for_condition(
                    lambda: not loader.is_visible(),
                    timeout=10.0,
                    poll_interval=0.5,
                    error_message=f"Loading indicator {selector} did not disappear"
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
    wait_between_attempts: float = 1.0
) -> Locator:
    logger.debug(f"Waiting for dynamic element: {selector} (max attempts: {max_attempts})")
    last_error = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            logger.debug(f"Attempt {attempt}/{max_attempts}")
            locator = page.locator(selector).first
            
            # Use the stable wait
            wait_for_element_stable(locator, timeout=attempt_timeout)
            
            logger.info(f"Dynamic element found and stable on attempt {attempt}")
            return locator
            
        except Exception as e:
            last_error = e
            logger.debug(f"Attempt {attempt} failed: {str(e)}")
            
            if attempt < max_attempts:
                logger.debug(f"Waiting {wait_between_attempts}s before retry")
                time.sleep(wait_between_attempts)
                
                # Re-check network idle between attempts
                wait_for_network_idle(page, timeout=5.0)
            else:
                logger.error(f"All {max_attempts} attempts failed")
    
    error_msg = f"Element '{selector}' did not become stable after {max_attempts} attempts. Last error: {last_error}"
    raise WaitTimeoutError(error_msg)

