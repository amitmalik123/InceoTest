"""
Retry Decorators and Utilities

Provides retry mechanisms with exponential backoff, jitter, and custom retry logic.
"""

import functools
import logging
import random
import time
from typing import Any, Callable, Optional, Tuple, Type

logger = logging.getLogger(__name__)


class RetryError(Exception):
    """Raised when all retry attempts are exhausted"""


def exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Add random jitter to delay
        exceptions: Tuple of exceptions to catch and retry

    Example:
        @exponential_backoff(max_retries=3, initial_delay=1.0)
        def fetch_data():
            response = requests.get('https://api.example.com')
            return response.json()
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retry_count = 0
            last_exception = None

            while retry_count <= max_retries:
                try:
                    result = func(*args, **kwargs)
                    if retry_count > 0:
                        logger.info(f"✓ {func.__name__} succeeded after {retry_count} retries")
                    return result

                except exceptions as e:
                    last_exception = e
                    retry_count += 1

                    if retry_count > max_retries:
                        logger.error(
                            f"✗ {func.__name__} failed after {max_retries} retries. "
                            f"Last error: {str(e)}"
                        )
                        raise RetryError(f"Failed after {max_retries} retries: {str(e)}") from e

                    # Calculate delay with exponential backoff
                    delay = min(initial_delay * (exponential_base ** (retry_count - 1)), max_delay)

                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay = delay * (0.5 + random.random())

                    logger.warning(
                        f"⟳ {func.__name__} attempt {retry_count}/{max_retries} failed: {str(e)}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    time.sleep(delay)

            raise RetryError(f"Failed after {max_retries} retries") from last_exception

        return wrapper

    return decorator


def retry_on_assertion(max_retries: int = 3, delay: float = 1.0, backoff: bool = True):
    """
    Retry decorator specifically for assertion errors.
    Useful for flaky tests or eventually consistent systems.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        backoff: Use exponential backoff

    Example:
        @retry_on_assertion(max_retries=5, delay=2.0)
        def test_eventually_visible():
            assert element.is_visible(), "Element not visible"
    """
    return exponential_backoff(
        max_retries=max_retries,
        initial_delay=delay,
        exponential_base=2.0 if backoff else 1.0,
        exceptions=(AssertionError,),
    )


def retry_on_exception(
    exception_type: Type[Exception] = Exception, max_retries: int = 3, delay: float = 1.0
):
    """
    Retry decorator for specific exception types.

    Args:
        exception_type: Exception type to catch and retry
        max_retries: Maximum number of retry attempts
        delay: Delay between retries

    Example:
        @retry_on_exception(TimeoutError, max_retries=3)
        def wait_for_element():
            return page.wait_for_selector("#element", timeout=5000)
    """
    return exponential_backoff(
        max_retries=max_retries, initial_delay=delay, exceptions=(exception_type,)
    )


class RetryContext:
    """
    Context manager for retry logic.

    Example:
        with RetryContext(max_retries=3, delay=1.0) as retry:
            while retry.should_retry():
                try:
                    result = unstable_operation()
                    retry.success()
                    break
                except Exception as e:
                    retry.failed(e)
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

        self.attempt = 0
        self.last_exception: Optional[Exception] = None
        self._success = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._success and self.last_exception:
            raise RetryError(f"Failed after {self.max_retries} retries") from self.last_exception
        return False

    def should_retry(self) -> bool:
        """Check if should continue retrying"""
        return self.attempt <= self.max_retries and not self._success

    def failed(self, exception: Exception):
        """Record failed attempt"""
        self.last_exception = exception
        self.attempt += 1

        if self.attempt <= self.max_retries:
            delay = min(self.initial_delay * (self.exponential_base ** (self.attempt - 1)), 60.0)

            if self.jitter:
                delay = delay * (0.5 + random.random())

            logger.warning(
                f"Attempt {self.attempt}/{self.max_retries} failed: {str(exception)}. "
                f"Retrying in {delay:.2f}s..."
            )

            time.sleep(delay)

    def success(self):
        """Mark operation as successful"""
        self._success = True
        if self.attempt > 1:
            logger.info(f"Succeeded after {self.attempt} attempts")


def retry_until_true(
    condition: Callable[[], bool],
    max_attempts: int = 10,
    delay: float = 1.0,
    timeout: Optional[float] = None,
    error_message: str = "Condition not met",
) -> bool:
    """
    Retry a condition until it returns True.

    Args:
        condition: Callable that returns boolean
        max_attempts: Maximum number of attempts
        delay: Delay between attempts
        timeout: Maximum time to wait (seconds)
        error_message: Error message if condition not met

    Returns:
        True if condition met, raises RetryError otherwise

    Example:
        retry_until_true(
            lambda: page.locator("#status").inner_text() == "Complete",
            max_attempts=10,
            delay=2.0
        )
    """
    start_time = time.time()

    for attempt in range(1, max_attempts + 1):
        try:
            if condition():
                if attempt > 1:
                    logger.info(f"Condition met after {attempt} attempts")
                return True
        except Exception as e:
            logger.debug(f"Condition check raised exception: {e}")

        # Check timeout
        if timeout and (time.time() - start_time) > timeout:
            raise RetryError(f"{error_message} (timeout after {timeout}s)")

        if attempt < max_attempts:
            logger.debug(f"Attempt {attempt}/{max_attempts} - condition not met, retrying...")
            time.sleep(delay)

    raise RetryError(f"{error_message} (after {max_attempts} attempts)")


class RetryableAction:
    """
    Wrapper for retryable actions with fluent API.

    Example:
        action = RetryableAction(lambda: page.click("#button"))
        action.with_retries(3).with_delay(1.0).execute()
    """

    def __init__(self, action: Callable):
        self.action = action
        self.max_retries = 3
        self.delay = 1.0
        self.exceptions = (Exception,)
        self.on_retry: Optional[Callable] = None

    def with_retries(self, count: int) -> "RetryableAction":
        """Set number of retries"""
        self.max_retries = count
        return self

    def with_delay(self, delay: float) -> "RetryableAction":
        """Set delay between retries"""
        self.delay = delay
        return self

    def on_exceptions(self, *exceptions: Type[Exception]) -> "RetryableAction":
        """Set exceptions to catch"""
        self.exceptions = exceptions
        return self

    def on_retry_callback(self, callback: Callable) -> "RetryableAction":
        """Set callback to call on each retry"""
        self.on_retry = callback
        return self

    def execute(self) -> Any:
        """Execute the action with retries"""
        decorator = exponential_backoff(
            max_retries=self.max_retries, initial_delay=self.delay, exceptions=self.exceptions
        )

        @decorator
        def wrapped_action():
            if self.on_retry:
                self.on_retry()
            return self.action()

        return wrapped_action()
