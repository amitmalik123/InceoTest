"""Soft assertion fixtures for Billing tests."""

import logging
from collections.abc import Generator

import pytest


logger = logging.getLogger(__name__)


class SoftAssertions:
    """Collect multiple assertion failures and report them together."""

    def __init__(self):
        self._failures: list[str] = []

    def check(self, condition: bool, message: str = "") -> None:
        if not condition:
            failure = message or "Assertion failed (no message provided)"
            self._failures.append(failure)
            logger.warning("  [soft] FAIL: %s", failure)
        else:
            logger.debug("  [soft] PASS: %s", message)

    def assert_all(self) -> None:
        if self._failures:
            combined = "\n  - ".join(self._failures)
            raise AssertionError(
                f"{len(self._failures)} soft assertion(s) failed:\n  - {combined}"
            )

    @property
    def failure_count(self) -> int:
        return len(self._failures)

    def reset(self) -> None:
        self._failures.clear()


@pytest.fixture
def soft_assert() -> Generator[SoftAssertions, None, None]:
    """Auto-validating soft assertion fixture."""
    assertions = SoftAssertions()
    yield assertions
    assertions.assert_all()
