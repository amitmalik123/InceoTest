"""
Playwright response tracking and validation utilities for API testing.

Provides helpers to track and validate HTTP responses intercepted by Playwright pages,
eliminating boilerplate response listener code in test steps.
"""

from typing import Callable, List, Optional, Tuple

from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class PlaywrightResponseTracker:
    """
    Tracks and validates Playwright page responses matching a URL pattern.

    Usage:
        tracker = PlaywrightResponseTracker(page)
        tracker.start_tracking("/api/endpoint")
        # ... perform actions that trigger API calls ...
        tracker.stop_tracking()
        tracker.validate_all_successful()
        tracker.validate_count(expected=3)
    """

    def __init__(self, page):
        """
        Initialize tracker with a Playwright page.

        Args:
            page: Playwright Page object
        """
        self.page = page
        self.responses: List[Tuple[str, int]] = []
        self._listener: Optional[Callable] = None
        self._url_pattern: Optional[str] = None

    def start_tracking(self, url_pattern: str) -> None:
        """
        Start capturing responses matching url_pattern.

        Args:
            url_pattern: String pattern to match in response URLs
                        (e.g., "/Proposals/Editor/SaveDetails")
        """
        self._url_pattern = url_pattern
        self.responses = []

        def capture(response):
            if url_pattern in response.url:
                self.responses.append((response.url, response.status))

        self._listener = capture
        self.page.on("response", capture)
        logger.info(f"Started tracking responses matching '{url_pattern}'")

    def stop_tracking(self) -> None:
        """Stop capturing responses."""
        if self._listener:
            self.page.remove_listener("response", self._listener)
            self._listener = None
            logger.info(f"Stopped tracking responses (captured {len(self.responses)} total)")

    def validate_all_successful(self, min_count: int = 1, api_name: Optional[str] = None) -> bool:
        """
        Validate all captured responses have HTTP 200 status.

        Args:
            min_count: Minimum number of responses expected (default: 1)
            api_name: Friendly name for logging (e.g., "SearchSymbols")

        Returns:
            True if validation passes

        Raises:
            AssertionError if any response has non-200 status or count is below minimum
        """
        api_name = api_name or self._url_pattern or "API"

        # Check for failures (non-200 status codes)
        failures = [r for r in self.responses if r[1] != 200]
        if failures:
            logger.error(f"{api_name} failures detected: {failures}")
            raise AssertionError(f"{api_name} calls failed: {failures}")

        # Check count threshold
        assert len(self.responses) >= min_count, (
            f"{api_name}: Expected at least {min_count} successful call(s), "
            f"got {len(self.responses)}"
        )

        logger.info(f"Validated {len(self.responses)} {api_name} calls (all HTTP 200)")
        return True

    def validate_count(
        self, expected: int, api_name: Optional[str] = None, at_least: bool = False
    ) -> bool:
        """
        Validate captured response count matches expected.

        Args:
            expected: Expected number of responses
            api_name: Friendly name for logging
            at_least: If True, assert count >= expected; else assert count == expected

        Returns:
            True if validation passes

        Raises:
            AssertionError if count doesn't match
        """
        api_name = api_name or self._url_pattern or "API"

        if at_least:
            assert len(self.responses) >= expected, (
                f"{api_name}: Expected at least {expected} call(s), " f"got {len(self.responses)}"
            )
            logger.info(f"Validated {len(self.responses)} >= {expected} {api_name} calls")
        else:
            assert len(self.responses) == expected, (
                f"{api_name}: Expected {expected} call(s), " f"got {len(self.responses)}"
            )
            logger.info(f"Validated {len(self.responses)} {api_name} calls (exact count)")

        return True

    def get_responses(self) -> List[Tuple[str, int]]:
        """
        Get list of captured (url, status) tuples.

        Returns:
            List of captured responses
        """
        return self.responses.copy()

    def get_successful_count(self) -> int:
        """Get count of responses with HTTP 200 status."""
        return sum(1 for _, status in self.responses if status == 200)

    def get_failed_responses(self) -> List[Tuple[str, int]]:
        """Get list of responses with non-200 status."""
        return [r for r in self.responses if r[1] != 200]
