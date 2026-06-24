"""pytest-bdd hooks aligned to base fixture layout.

Provides BDD step lifecycle hooks with Allure step wrapping and screenshot
capture while preserving local screenshot configuration behavior.
"""

import contextlib
import inspect
import os

import allure

from config.settings import get_settings
from fixtures.browser_fixtures import id_tracker
from utils.allure_logger import get_allure_logger, get_step_screenshot_config

_active_allure_steps: dict[str, object] = {}


def _resolve_page_from_request(request):
    """Resolve a Playwright page from pytest request fixtures when available."""
    page = None

    try:
        page = request.getfixturevalue("page")
    except Exception:
        pass

    if page is None:
        try:
            page = request.getfixturevalue("authenticated_page")
        except Exception:
            pass

    if page is None and hasattr(request, "node") and hasattr(request.node, "funcargs"):
        funcargs = request.node.funcargs
        page = funcargs.get("page") or funcargs.get("authenticated_page")

        if page is None:
            for fixture_value in funcargs.values():
                candidate_page = getattr(fixture_value, "page", None)
                if candidate_page is not None and hasattr(candidate_page, "screenshot"):
                    page = candidate_page
                    break

    return page


def _step_uses_custom_logger(step_func) -> bool:
    """Detect whether step function already wraps actions with logger.step(...)."""
    try:
        candidate_funcs = [inspect.unwrap(step_func), step_func]
    except Exception:
        candidate_funcs = [step_func]

    for candidate in candidate_funcs:
        try:
            source = inspect.getsource(candidate)
            if "logger.step(" in source:
                return True
        except Exception:
            continue

    return False


def pytest_bdd_before_step(request, feature, scenario, step, step_func) -> None:
    """Start an Allure step context before each BDD step executes."""
    step_name = f"{step.keyword} {step.name}"

    # Set scenario name on the ID tracker (idempotent within the same scenario)
    id_tracker.set_scenario(scenario.name)

    allure_step_context = allure.step(step_name)
    allure_step_context.__enter__()

    step_key = f"{id(request.node)}_{step.name}"
    _active_allure_steps[step_key] = allure_step_context


def pytest_bdd_after_step(request, feature, scenario, step, step_func) -> None:
    """Capture step screenshot when enabled and close Allure step context."""
    settings_instance = get_settings()
    config = get_step_screenshot_config()

    screenshot_enabled = (
        os.getenv("SCREENSHOT_EACH_STEP", "").lower() in ("true", "1", "yes", "on")
        or settings_instance.screenshot_each_step
        or config.enabled
    )

    page = _resolve_page_from_request(request)

    # Avoid duplicate screenshots when step function already uses logger.step(..., page=...)
    has_custom_step_screenshot = _step_uses_custom_logger(step_func)

    if page and screenshot_enabled and not has_custom_step_screenshot:
        try:
            config.step_counter += 1
            screenshot = page.screenshot()
            step_name = f"{step.keyword} {step.name}"
            screenshot_name = f"Step {config.step_counter} ✓ {step_name}"
            allure.attach(
                screenshot,
                name=screenshot_name,
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as exc:
            logger = get_allure_logger(__name__)
            logger.warning(f"Could not capture screenshot: {exc}", attach_to_allure=False)

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
                shadow_text = page.evaluate(
                    """() => {
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
                }"""
                )
                if shadow_text:
                    id_tracker.scan(shadow_text)
            except Exception:
                pass
        except Exception:
            pass


def pytest_bdd_step_error(
    request, feature, scenario, step, step_func, step_func_args, exception
) -> None:
    """Capture failure screenshot and close Allure step context with error."""
    page = _resolve_page_from_request(request)
    has_custom_step_screenshot = _step_uses_custom_logger(step_func)

    if page and not has_custom_step_screenshot:
        try:
            screenshot = page.screenshot()
            allure.attach(
                screenshot,
                name="FAILED Screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as exc:
            logger = get_allure_logger(__name__)
            logger.warning(f"Failure screenshot failed: {exc}", attach_to_allure=False)

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
