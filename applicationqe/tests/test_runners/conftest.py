"""
Conftest for model-management test runners.

Provides a session-scoped authenticated browser context.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Generator

import pytest
import yaml
from playwright.sync_api import Browser, BrowserContext

_APP_ROOT = Path(__file__).resolve().parents[2]
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_WRAPPERMODEL_CONFIG_DIR = (
    _APP_ROOT / "config" / "model-management" / "wrappermodel"
)

_SSO_KEYWORDS = (
    "test-login.assetmark.com",
    "okta",
    "/login",
    "signin",
)


def _load_wrappermodel_config(env: str) -> dict:
    """Load env YAML; fall back to test01 when the requested env file is absent."""
    config_file = _WRAPPERMODEL_CONFIG_DIR / f"env.{env}.yaml"
    if not config_file.exists():
        config_file = _WRAPPERMODEL_CONFIG_DIR / "env.test01.yaml"
    with open(config_file) as fh:
        return yaml.safe_load(fh)


def _dismiss_accept_all_popup(page) -> None:
    """Click 'Accept All' (or equivalent) consent popup if it appears.

    Non-fatal: if no popup is found within a short timeout the call returns silently.
    """
    candidates = [
        "button:has-text('Accept All')",
        "button:has-text('Accept all')",
        "button:has-text('Accept All Cookies')",
        "button:has-text('Accept Cookies')",
        "button:has-text('Accept')",
        "#onetrust-accept-btn-handler",
        "[id*='accept'][role='button']",
    ]
    for selector in candidates:
        try:
            btn = page.locator(selector).first
            btn.wait_for(state="visible", timeout=3000)
            btn.click()
            print(f"[conftest] Dismissed popup via selector: {selector!r}")
            page.wait_for_timeout(500)
            return
        except Exception:
            continue


def _do_okta_login(page, username: str, password: str) -> bool:
    """Fill Okta login form and submit. Returns True on apparent success."""
    try:
        page.wait_for_selector("input#okta-signin-username", timeout=20_000)
        page.fill("input#okta-signin-username", username)
        page.fill("input#okta-signin-password", password)
        page.click("input#okta-signin-submit")
        page.wait_for_function(
            "() => !window.location.hostname.includes('test-login')",
            timeout=60_000,
        )
        page.wait_for_load_state("networkidle", timeout=30_000)
        _dismiss_accept_all_popup(page)
        return True
    except Exception as exc:
        print(f"\n[conftest] Okta login failed: {exc}")
        return False


# ---------------------------------------------------------------------------
# Session-scoped authenticated context
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def context(
    browser: Browser,
    browser_context_args: dict,
    request,
) -> Generator[BrowserContext, None, None]:
    """Session-scoped browser context with SSO login performed once."""
    env = request.config.getoption("--env", default="test01")
    config = _load_wrappermodel_config(env)

    username: str = config.get("internal_admin", {}).get("username", "")
    password: str = config.get("internal_admin", {}).get("password", "")
    login_url: str = (
        config.get("application", {}).get("login_url")
        or "https://app.test01.assetmark.com/models"
    )

    ctx: BrowserContext = browser.new_context(**browser_context_args)
    auth_page = ctx.new_page()

    try:
        print(f"\n[conftest] Navigating to {login_url!r} …")
        auth_page.goto(login_url, wait_until="domcontentloaded", timeout=60_000)
        # Wait for Okta redirect (JS auth-check fires AFTER domcontentloaded).
        # If the redirect doesn't happen within 20 s the app is already accessible.
        try:
            auth_page.wait_for_url("*test-login*", timeout=20_000)
        except Exception:
            pass  # no SSO redirect — app accessible without login
        current_url = auth_page.url.lower()
        print(f"[conftest] Landed on: {auth_page.url}")
        if any(kw in current_url for kw in _SSO_KEYWORDS):
            print(f"[conftest] SSO detected → logging in as {username!r}")
            ok = _do_okta_login(auth_page, username, password)
            print(f"[conftest] Login {'OK' if ok else 'FAILED'}. URL: {auth_page.url}")
    except Exception as exc:
        print(f"[conftest] session auth error: {exc}")
    finally:
        auth_page.close()

    yield ctx
    ctx.close()
