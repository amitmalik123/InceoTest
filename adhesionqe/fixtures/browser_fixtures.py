"""
Browser and Context Configuration Fixtures

This module contains:
- browser_context_args fixture (parallel execution support)
- new_context fixture (multi-session scenarios)
- new_page fixture (multi-tab scenarios)
- multi_user_contexts fixture (admin/user testing)

These fixtures handle browser/context configuration and multi-context scenarios.
"""

from collections.abc import Callable, Generator

import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, request) -> dict:
    """
    Configure browser context with worker-specific output directories for parallel execution
    """
    import os

    # Get worker ID for parallel execution
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")

    # Make output directories worker-specific to avoid conflicts
    if worker_id != "master":
        record_video_dir = f"reports/videos/{worker_id}"

    else:
        record_video_dir = "reports/videos"

    # Base browser context args
    """
    {
        "viewport": {...},
         "baseURL": "...",
         "record_video_dir": "...",
         "ignore_https_errors": True
    }
    """
    context_args = {
        **browser_context_args,
        "ignore_https_errors": True,
    }

    # Add video recording if configured
    if record_video_dir:
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
