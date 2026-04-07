"""
Browser and Context Configuration Fixtures

This module contains:
- browser_context_args fixture (parallel execution support)
- apply_route_blocks helper (allowlist-based domain filtering)
- apply_context_listeners helper (HTTP errors, JS errors, console warnings)
- new_context fixture (multi-session scenarios)
- new_page fixture (multi-tab scenarios)
- multi_user_contexts fixture (admin/user testing)

These fixtures handle browser/context configuration and multi-context scenarios.
"""

import logging
import os
import re
import sys
from collections.abc import Callable, Generator

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from pathlib import Path
from urllib.parse import urlparse

import pytest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ID Tracker – captures IDs from responses and page content
# ---------------------------------------------------------------------------

# Log file for captured IDs (same as network errors log directory)
_ID_LOG_PATH = Path("reports/network_errors.log")


def _load_id_capture_config() -> tuple[bool, re.Pattern | None]:
    """Load id-capture config from pyproject.toml [tool.id-capture]."""
    try:
        with open(_PYPROJECT_PATH, "rb") as f:
            config = tomllib.load(f)
        section = config.get("tool", {}).get("id-capture", {})
        enabled = section.get("enabled", False)
        patterns = section.get("patterns", [])
        if not enabled or not patterns:
            return False, None
        combined = "|".join(f"({p})" for p in patterns)
        return True, re.compile(combined)
    except Exception:
        return False, None


_ID_CAPTURE_ENABLED, _ID_PATTERN = _load_id_capture_config()


class IdTracker:
    """Collects unique IDs per scenario and writes a summary line."""

    def __init__(self):
        self._ids: dict[str, set[str]] = {}   # prefix → set of IDs
        self._scenario: str = ""

    def set_scenario(self, name: str) -> None:
        if name != self._scenario:
            self._scenario = name
            self._ids.clear()

    def scan(self, text: str) -> None:
        """Find all matching IDs in *text* and track unique ones."""
        if not _ID_PATTERN:
            return
        for match in _ID_PATTERN.finditer(text):
            value = match.group()
            prefix = value[0]
            self._ids.setdefault(prefix, set()).add(value)

    def flush(self) -> None:
        """Write captured IDs to the log file and reset."""
        if not self._ids:
            return
        parts = []
        for prefix in sorted(self._ids):
            ids = ", ".join(sorted(self._ids[prefix]))
            parts.append(f"#{prefix}: {ids}")
        line = f"{self._scenario} | {', '.join(parts)}"
        _write_to_id_log(line)
        logger.info(f"[ID CAPTURE] {line}")
        self._ids.clear()


def _write_to_id_log(line: str) -> None:
    """Append an ID capture line to the log file."""
    from datetime import datetime

    _ID_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(_ID_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}  [ID CAPTURE] {line}\n")


# Singleton tracker – shared with hooks_fixtures
id_tracker = IdTracker()

# Path to pyproject.toml (repo root)
_PYPROJECT_PATH = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"


def _load_route_blocking_config() -> tuple[bool, set[str], Path]:
    """Load route-blocking config from pyproject.toml [tool.route-blocking]."""
    try:
        with open(_PYPROJECT_PATH, "rb") as f:
            config = tomllib.load(f)
        section = config.get("tool", {}).get("route-blocking", {})
        enabled = section.get("enabled", True)
        domains = {d.strip().lower() for d in section.get("allowed_domains", [])}
        log_path = Path(section.get("http_error_log", "reports/http_errors.log"))
        return enabled, domains, log_path
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return False, set(), Path("reports/http_errors.log")


def _is_allowed(url: str, allowed_domains: set[str]) -> bool:
    """Check if a URL's hostname contains any allowed domain."""
    hostname = urlparse(url).hostname
    if not hostname:
        return True  # data: / blob: / about: URLs — always allow
    hostname = hostname.lower()
    return any(domain in hostname for domain in allowed_domains)


def apply_route_blocks(context) -> None:
    """
    Allow only requests to domains listed in pyproject.toml [tool.route-blocking];
    abort everything else.
    """
    enabled, allowed_domains, _ = _load_route_blocking_config()
    if not enabled or not allowed_domains:
        return

    def _handle_route(route):
        if _is_allowed(route.request.url, allowed_domains):
            route.continue_()
        else:
            route.abort()

    context.route("**/*", _handle_route)


# HTTP error log file path — loaded from pyproject.toml
_, _, _HTTP_LOG_PATH = _load_route_blocking_config()


def apply_context_listeners(context) -> None:
    """Attach listeners at the context level for observability.

    Captures:
    - Non-2xx HTTP responses (via context.on('response'))
    - JS console errors/warnings (via context.on('page') → page.on('console'))
    - Uncaught JS exceptions (via context.on('page') → page.on('pageerror'))

    Does not fail tests — only logs warnings and writes to the error log file.
    """
    # Ensure reports directory exists
    _HTTP_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # --- Response listener (context-level) ---
    def _on_response(response):
        if response.status >= 400:
            line = f"[HTTP {response.status}] {response.request.method} {response.url}"
            logger.warning(line)
            _write_to_log(line)
        elif response.status >= 300:
            line = f"[HTTP {response.status}] {response.request.method} {response.url} (redirect)"
            logger.info(line)
        #    _write_to_log(line)

        # Scan response body for IDs (if id-capture is enabled)
        if _ID_CAPTURE_ENABLED:
            try:
                content_type = response.headers.get("content-type", "")
                if any(ct in content_type for ct in ("text/", "json", "xml", "html")):
                    body = response.text()
                    if body:
                        id_tracker.scan(body)
            except Exception:
                pass  # network errors, binary responses, etc.

    context.on("response", _on_response)

    # --- Page-level listeners (auto-applied to every page including popups) ---
    def _attach_page_listeners(page):
        def _on_console(msg):
            if msg.type in ("error", "warning"):
                line = f"[CONSOLE {msg.type}] {msg.text}"
                logger.warning(line)
                _write_to_log(line)

        def _on_pageerror(error):
            line = f"[PAGE ERROR] {error}"
            logger.warning(line)
            _write_to_log(line)

     #   page.on("console", _on_console)
        page.on("pageerror", _on_pageerror)

    context.on("page", _attach_page_listeners)


def _write_to_log(line: str) -> None:
    """Append a line to the HTTP error log file (thread/worker safe via append mode)."""
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(_HTTP_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}  {line}\n")


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args) -> dict:
    """Launch browser maximized so it fills the full screen."""
    return {**browser_type_launch_args, "args": ["--start-maximized"]}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, request) -> dict:
    """
    Configure browser context with worker-specific output directories for parallel execution
    and full-screen (no fixed viewport, maximized window).
    """
    import os

    # Get worker ID for parallel execution
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")

    # Make output directories worker-specific to avoid conflicts
    if worker_id != "master":
        record_video_dir = f"reports/videos/{worker_id}"
    else:
        record_video_dir = "reports/videos"

    # Base browser context args — no_viewport allows the page to fill the window
    context_args = {
        **browser_context_args,
        "no_viewport": True,
        "ignore_https_errors": True,
    }

    # Only set record_video_dir when --video is on or retain-on-failure
    video_option = request.config.getoption("--video", default="off")
    if video_option in ("on", "retain-on-failure"):
        context_args["record_video_dir"] = record_video_dir

    return context_args


@pytest.fixture
def new_context(browser) -> Generator[Callable, None, None]:
    """
    Create additional browser contexts for multi-session scenarios.

    Usage:
        def test_multi_user(authenticated_page, new_context):
            # First user (default page)
            authenticated_page.goto("/dashboard")

            # Second user (new context)
            admin_page = new_context().new_page()
            admin_page.goto("/admin")
    """
    contexts = []

    def _create_context(**kwargs):
        context_args = {"ignore_https_errors": True, **kwargs}
        ctx = browser.new_context(**context_args)
        contexts.append(ctx)
        return ctx

    yield _create_context

    # Cleanup all created contexts
    for ctx in contexts:
        ctx.close()


@pytest.fixture
def new_page(context) -> Generator[Callable, None, None]:
    """
    Create additional pages within the same context for multi-tab scenarios.

    Usage:
        def test_multi_tab(authenticated_page, new_page):
            # Main tab
            authenticated_page.goto("/accounts")

            # Second tab (same session/cookies)
            tab2 = new_page()
            tab2.goto("/reports")

            # Work with both tabs
            assert authenticated_page.url.endswith("/accounts")
            assert tab2.url.endswith("/reports")
    """
    pages = []

    def _create_page():
        new_pg = context.new_page()
        pages.append(new_pg)
        return new_pg

    yield _create_page

    # Cleanup all created pages
    for pg in pages:
        pg.close()


@pytest.fixture
def multi_user_contexts(browser) -> Generator[dict, None, None]:
    """
    Pre-configured contexts for multi-user testing.

    Returns dict with 'admin' and 'user' contexts.

    Usage:
        def test_admin_vs_user(multi_user_contexts):
            admin_page = multi_user_contexts['admin'].new_page()
            user_page = multi_user_contexts['user'].new_page()

            # Different sessions, different cookies
            admin_page.goto("/admin/dashboard")
            user_page.goto("/user/dashboard")
    """
    contexts = {
        "admin": browser.new_context(ignore_https_errors=True, storage_state=None),  # Fresh session
        "user": browser.new_context(ignore_https_errors=True, storage_state=None),  # Fresh session
    }

    yield contexts

    # Cleanup
    for ctx in contexts.values():
        ctx.close()
