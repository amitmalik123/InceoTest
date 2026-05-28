"""Pytest-bdd lifecycle hooks for Billing scenarios."""

import logging
import re
from datetime import datetime
from pathlib import Path


logger = logging.getLogger(__name__)

_SCREENSHOT_ROOT = Path("reports/billing/platformrevenuedashboard/strategistgroupmodel/screenshots")


def _capture_failure_screenshot(page, scenario_name: str, step_name: str) -> None:
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
    try:
        return request.getfixturevalue("page")
    except Exception:
        return None


def pytest_bdd_before_scenario(request, feature, scenario) -> None:
    _ = request
    logger.info("━" * 60)
    logger.info("SCENARIO START : %s", scenario.name)
    logger.info("  Feature      : %s", feature.name)
    logger.info("━" * 60)


def pytest_bdd_after_scenario(request, feature, scenario) -> None:
    _ = request
    _ = feature
    logger.info("━" * 60)
    logger.info("SCENARIO END   : %s", scenario.name)
    logger.info("━" * 60)


def pytest_bdd_before_step(request, feature, scenario, step, step_func) -> None:
    _ = request
    _ = feature
    _ = scenario
    _ = step_func
    logger.info("  ▸ STEP: %s %s", step.keyword, step.name)


def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args=None) -> None:
    _ = request
    _ = feature
    _ = scenario
    _ = step_func
    _ = step_func_args
    logger.info("  ✓ PASS: %s %s", step.keyword, step.name)


def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception) -> None:
    _ = feature
    _ = step_func
    _ = step_func_args
    logger.error("  ✗ FAIL: %s %s — %s", step.keyword, step.name, exception)
    page = _get_page(request)
    _capture_failure_screenshot(page, scenario.name, f"{step.keyword} {step.name}")
