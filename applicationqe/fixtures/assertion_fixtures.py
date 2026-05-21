"""Assertion and test utility fixtures in base-branch location.

Keeps existing local assertion behavior and base fixture naming.
"""

from collections.abc import Generator

import pytest

from utils.allure_logger import reset_step_counter
from utils.assertions import SoftAssertions


@pytest.fixture
def soft_assert() -> Generator[SoftAssertions, None, None]:
    """Auto-validating soft assertions fixture."""
    soft = SoftAssertions()
    yield soft
    soft.assert_all()


@pytest.fixture(autouse=True)
def reset_step_screenshot_counter() -> Generator[None, None, None]:
    """Automatically reset step counter before each test."""
    reset_step_counter()
    yield
