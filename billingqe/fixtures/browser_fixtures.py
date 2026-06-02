"""Browser-related pytest fixtures for Billing UI automation."""

import os

import pytest


@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig):
    """Configure Playwright browser launch settings."""
    headed_requested = bool(pytestconfig.getoption("--headed"))
    try:
        headless_requested = bool(pytestconfig.getoption("--headless"))
    except Exception:
        headless_requested = False

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
    """Override default browser context settings."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }
