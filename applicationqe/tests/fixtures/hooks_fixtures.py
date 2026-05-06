"""
pytest-bdd Hooks for Allure Integration

This module contains:
- BDD step lifecycle hooks (before/after step)
- BDD error handling hooks
- Automatic screenshot capture with Allure
- Step context management

These hooks integrate pytest-bdd with Allure reporting and screenshot capture.
"""

import contextlib
import os

import allure

from config.settings import get_settings
from tests.fixtures.browser_fixtures import id_tracker
from utils.allure_logger import get_allure_logger

# Global storage for active allure step contexts
_active_allure_steps = {}


def pytest_bdd_before_step(request, feature, scenario, step, step_func) -> None:
    """
    Hook that runs BEFORE each BDD step executes.
    Starts an Allure step context that will wrap the entire step execution.
    """
    step_name = f"{step.keyword} {step.name}"

    # Set scenario name on the ID tracker (idempotent within the same scenario)
    id_tracker.set_scenario(scenario.name)

    # Create and enter allure step context
    allure_step_context = allure.step(step_name)
    allure_step_context.__enter__()

    # Store it keyed by request node id + step name for retrieval in after_step
    step_key = f"{id(request.node)}_{step.name}"
    _active_allure_steps[step_key] = allure_step_context


def pytest_bdd_after_step(request, feature, scenario, step, step_func) -> None:
    """
    Hook that runs AFTER each BDD step completes.
    Takes screenshot and closes the Allure step context.
    """
    # Check screenshot setting from config/env var
    settings_instance = get_settings()
    screenshot_enabled = (
        os.getenv("SCREENSHOT_EACH_STEP", "").lower() in ("true", "1", "yes", "on")
        or settings_instance.screenshot_each_step
    )

    # Get page object from pytest request fixture
    page = None
    try:
        # Try to get 'authenticated_page' fixture from request
        page = request.getfixturevalue("authenticated_page")
    except Exception:
        # If that fails, try funcargs
        if hasattr(request, "node") and hasattr(request.node, "funcargs"):
            page = request.node.funcargs.get("authenticated_page")

    # Take screenshot BEFORE closing the step context (so it's inside the step)
    if page and screenshot_enabled:
        try:
            screenshot = page.screenshot()
            allure.attach(
                screenshot,
                name="Screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as e:
            logger = get_allure_logger(__name__)
            logger.warning(f"Screenshot failed: {e}", attach_to_allure=False)

    # Now close the allure step context
    step_key = f"{id(request.node)}_{step.name}"
    if step_key in _active_allure_steps:
        allure_step_context = _active_allure_steps.pop(step_key)
        with contextlib.suppress(Exception):
            allure_step_context.__exit__(None, None, None)

    # Scan page content for IDs (all frames + shadow DOM)
    if page:
        try:
            # Main frame + all child frames (iframes)
            for frame in page.frames:
                try:
                    frame_text = frame.content()
                    if frame_text:
                        id_tracker.scan(frame_text)
                except Exception:
                    pass

            # Shadow DOM — JS walks all shadow roots and collects textContent
            try:
                shadow_text = page.evaluate("""() => {
                    const texts = [];
                    function walk(root) {
                        for (const el of root.querySelectorAll('*')) {
                            if (el.shadowRoot) {
                                texts.push(el.shadowRoot.textContent || '');
                                walk(el.shadowRoot);
                            }
                        }
                    }
                    walk(document);
                    return texts.join(' ');
                }""")
                if shadow_text:
                    id_tracker.scan(shadow_text)
            except Exception:
                pass
        except Exception:
            pass


def pytest_bdd_step_error(
    request, feature, scenario, step, step_func, step_func_args, exception
) -> None:
    """
    Hook that runs when a BDD step fails.
    Takes failure screenshot and closes the step context with error.
    
    IMPORTANT: This hook should NOT re-raise fixture initialization errors
    that would mask the ORIGINAL step failure.
    """
    logger = get_allure_logger(__name__)
    page = None
    
    # PRIORITY 1: Try to get 'authenticated_page' from funcargs FIRST
    # This should have the already-initialized page from the test
    # (if test made it far enough to reach a BDD step, fixture must have succeeded)
    try:
        if hasattr(request, "node") and hasattr(request.node, "funcargs"):
            page = request.node.funcargs.get("authenticated_page")
            if page:
                print("[STEP ERROR] Retrieved page from funcargs (already initialized)")
    except Exception as e:
        print(f"[STEP ERROR] Error getting page from funcargs: {e}")

    # PRIORITY 2: Try to get 'authenticated_page' fixture from request
    # Only if not found in funcargs
    # Wrap in try-except to prevent auth errors from masking the step failure
    if not page:
        try:
            page = request.getfixturevalue("authenticated_page")
            print("[STEP ERROR] Retrieved page via getfixturevalue")
        except Exception as e:
            # Log fixture error but DON'T re-raise
            # Re-raising would mask the original step failure
            logger.warning(
                f"Could not get authenticated_page for screenshot: {type(e).__name__}: {e}",
                attach_to_allure=False
            )
            print(f"[STEP ERROR] Could not get authenticated_page: {type(e).__name__}: {e}")

    # Take failure screenshot
    if page:
        try:
            screenshot = page.screenshot()
            allure.attach(
                screenshot,
                name="FAILED Screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
            print("[STEP ERROR] Screenshot attached to report")
        except Exception as e:
            logger.warning(
                f"Failure screenshot failed: {type(e).__name__}: {e}",
                attach_to_allure=False
            )
            print(f"[STEP ERROR] Screenshot failed: {e}")
    else:
        print("[STEP ERROR] No page available for screenshot")

    # Close the step context with exception
    step_key = f"{id(request.node)}_{step.name}"
    if step_key in _active_allure_steps:
        allure_step_context = _active_allure_steps.pop(step_key)
        with contextlib.suppress(Exception):
            allure_step_context.__exit__(type(exception), exception, exception.__traceback__)


def pytest_bdd_after_scenario(request, feature, scenario) -> None:
    """
    Hook that runs AFTER each BDD scenario completes.
    Flushes any captured A/B/D IDs to the log file.
    """
    id_tracker.flush()
