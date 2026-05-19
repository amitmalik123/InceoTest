"""
Consolidated Billing Fixtures for Strategist Group Model (SGM) Tests

This file contains all fixtures used across SGM tests:
- Browser configuration (pytest-playwright integration)
- BDD lifecycle hooks (scenario/step logging, failure screenshots)
- CSV test data utilities
- Soft assertions for multi-failure collection
"""

import csv
import logging
import os
import re
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pytest

logger = logging.getLogger(__name__)

_SCREENSHOT_ROOT = Path("reports/billing/platformrevenuedashboard/strategistgroupmodel/screenshots")


# ========================
# BROWSER FIXTURES
# ========================

@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig):
    """Browser launch arguments.
    
    These are passed to playwright's browser.launch() and include:
    - Automation detection bypass
    - Shared memory disable for stability
    - Sandbox disabled for Linux environments
    
    The --headed flag is automatically handled by pytest-playwright.
    """
    headed_requested = bool(pytestconfig.getoption("--headed"))
    try:
        headless_requested = bool(pytestconfig.getoption("--headless"))
    except Exception:
        headless_requested = False

    # In CI environments (no display), always default to headless.
    # Locally, default to headed for easier debugging.
    is_ci = os.getenv("CI", "").lower() in ("true", "1", "yes")

    if headless_requested:
        headless_mode = True
    elif headed_requested:
        headless_mode = False
    elif is_ci:
        headless_mode = True
    else:
        headless_mode = False

    launch_args = {
        "headless": headless_mode,
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ],
    }

    if headed_requested:
        launch_args["slow_mo"] = 200

    return launch_args


@pytest.fixture(scope="function")
def browser_context_args(browser_context_args):
    """Override default browser context args for all tests.
    
    The browser_context_args parameter comes from pytest-playwright's default.
    We extend it with custom viewport and HTTPS error handling.
    
    Args:
        browser_context_args: Default args from pytest-playwright fixture
        
    Returns:
        Enhanced context args with custom viewport and settings
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


# ========================
# SOFT ASSERTIONS FIXTURES
# ========================

class SoftAssertions:
    """Collect multiple assertion failures and report them all at once."""

    def __init__(self):
        self._failures: List[str] = []

    def check(self, condition: bool, message: str = "") -> None:
        """Record a failure if *condition* is falsy."""
        if not condition:
            failure = message or "Assertion failed (no message provided)"
            self._failures.append(failure)
            logger.warning("  [soft] FAIL: %s", failure)
        else:
            logger.debug("  [soft] PASS: %s", message)

    def assert_all(self) -> None:
        """Raise AssertionError with all collected failures if any exist."""
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
    """Auto-validating soft assertions fixture."""
    assertions = SoftAssertions()
    yield assertions
    assertions.assert_all()


# ========================
# TEST DATA FIXTURES
# ========================

class TestDataManager:
    """Flexible CSV data manager — filter, query, iterate rows."""

    def __init__(self, data_rows: List[Dict[str, str]]):
        self._data = data_rows

    def get_by(self, **criteria) -> Optional[Dict[str, str]]:
        """Return the FIRST row where all criteria key=value pairs match."""
        for row in self._data:
            if all(str(row.get(k, "")).strip() == str(v).strip() for k, v in criteria.items()):
                return row
        return None

    def filter_by(self, **criteria) -> List[Dict[str, str]]:
        """Return ALL rows where all criteria key=value pairs match."""
        return [
            row for row in self._data
            if all(str(row.get(k, "")).strip() == str(v).strip() for k, v in criteria.items())
        ]

    def get_all(self) -> List[Dict[str, str]]:
        return list(self._data)

    def get_column_values(self, column: str) -> List[str]:
        """Return distinct non-empty values for a column."""
        return list({str(row.get(column, "")).strip() for row in self._data if row.get(column)})

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, index) -> Dict[str, str]:
        return self._data[index]

    def __iter__(self):
        return iter(self._data)

    @classmethod
    def from_csv(cls, csv_path: Path, encoding: str = "utf-8") -> "TestDataManager":
        """Load a CSV file and return a TestDataManager instance."""
        if not csv_path.exists():
            raise FileNotFoundError(f"Test data CSV not found: {csv_path}")
        with open(csv_path, "r", encoding=encoding) as fh:
            rows = list(csv.DictReader(fh))
        logger.info("Loaded %d rows from %s", len(rows), csv_path)
        return cls(rows)


@pytest.fixture
def csv_data_manager():
    """
    Factory fixture — call with a Path to get a TestDataManager.
    """
    def _factory(csv_path: Path, encoding: str = "utf-8") -> TestDataManager:
        return TestDataManager.from_csv(csv_path, encoding=encoding)

    return _factory


# ========================
# BDD LIFECYCLE HOOKS
# ========================

def _capture_failure_screenshot(page, scenario_name: str, step_name: str) -> None:
    """Save screenshot for a failing step."""
    if page is None:
        return
    try:
        _SCREENSHOT_ROOT.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = re.sub(r"[^A-Za-z0-9_-]+", "_", f"{scenario_name[:40]}_{step_name[:30]}")
        path = _SCREENSHOT_ROOT / f"FAIL_{safe}_{timestamp}.png"
        page.screenshot(path=str(path), full_page=False)
        logger.info("  📸 Failure screenshot: %s", path)
    except Exception as exc:
        logger.warning("  Screenshot capture failed: %s", exc)


def _get_page(request):
    """Retrieve the 'page' fixture without raising if unavailable."""
    try:
        return request.getfixturevalue("page")
    except Exception:
        return None


def pytest_bdd_before_scenario(request, feature, scenario) -> None:
    """Log scenario start."""
    logger.info("━" * 60)
    logger.info("SCENARIO START : %s", scenario.name)
    logger.info("  Feature      : %s", feature.name)
    logger.info("━" * 60)


def pytest_bdd_after_scenario(request, feature, scenario) -> None:
    """Log scenario end."""
    logger.info("━" * 60)
    logger.info("SCENARIO END   : %s", scenario.name)
    logger.info("━" * 60)


def pytest_bdd_before_step(request, feature, scenario, step, step_func) -> None:
    """Log step execution."""
    logger.info("  ▸ STEP: %s %s", step.keyword, step.name)


def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args=None) -> None:
    """Log successful step completion."""
    logger.info("  ✓ PASS: %s %s", step.keyword, step.name)


def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception) -> None:
    """Log step failure and capture screenshot."""
    logger.error("  ✗ FAIL: %s %s — %s", step.keyword, step.name, exception)
    page = _get_page(request)
    _capture_failure_screenshot(page, scenario.name, f"{step.keyword} {step.name}")
