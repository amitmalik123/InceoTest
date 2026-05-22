"""Local conftest for the PMT SDT ISC suite.

This conftest is the single home for every fixture and helper used by
``tests/features/pmt/sdt_isc.feature``. It is intentionally self-contained
and scoped to ``tests/features/pmt/`` only:

  - Test11 environment config loaded from ``config/pmt/env.test11.yaml``
  - Per-scenario CSV-backed credentials/test data
  - ``authenticated_page`` (EWM/Okta login)
  - ``test_data`` / ``test_context``
  - Page-object fixtures: ``account_list_page``, ``clients_page``,
    ``account_detail_page``, ``change_investments_page``, ``docusign_page``,
    ``tracking_center_page``, ``sdt_isc_page``
  - PMT SQL-query helpers: ``pmt_sql_queries``, ``pmt_query``, ``pmt_db_config``

Nothing here leaks to other test trees (BAW, STP, etc.); they have their own
conftests or rely on the minimal root ``tests/conftest.py``.
"""

from __future__ import annotations

import csv
import os
import time
from pathlib import Path

import pytest
import yaml

from utils.settings import settings


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_APPLICATIONQE_ROOT = Path(__file__).resolve().parents[3]
_PMT_CONFIG_DIR = _APPLICATIONQE_ROOT / "config" / "pmt"
_PMT_QUERIES_FILE = _APPLICATIONQE_ROOT / "queries" / "pmt" / "sql_queries.yaml"


# ---------------------------------------------------------------------------
# Config / data loaders (PMT-scoped)
# ---------------------------------------------------------------------------


def _load_pmt_env_config() -> dict:
    """Load the PMT env config for the active environment, falling back to test11."""
    env_name = os.getenv("TEST_ENV", "test11")
    candidates = [
        _PMT_CONFIG_DIR / f"env.{env_name}.yaml",
        _PMT_CONFIG_DIR / "env.test11.yaml",
    ]
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                return yaml.safe_load(fh) or {}
    return {}


def _load_test_data_rows(cfg: dict) -> list:
    csv_rel = (cfg.get("data") or {}).get("test_data_csv", "")
    if not csv_rel:
        return []
    csv_path = _APPLICATIONQE_ROOT / csv_rel
    with open(csv_path, "r", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _resolve_scenario_name(request) -> str:
    node = request.node
    obj = getattr(node, "obj", None)
    scenario = getattr(obj, "__scenario__", None) if obj else None
    if scenario is not None:
        return scenario.name
    return node.name.replace("test_", "").replace("_", " ")


def _load_pmt_sql_queries() -> dict:
    """Load the PMT SQL queries YAML (``queries/pmt/sql_queries.yaml``)."""
    if not _PMT_QUERIES_FILE.exists():
        return {}
    with _PMT_QUERIES_FILE.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


# ---------------------------------------------------------------------------
# Authentication and per-scenario data
# ---------------------------------------------------------------------------


@pytest.fixture
def authenticated_page(browser, browser_context_args, test_data, request):
    """Real EWM authentication.

    URL comes from ``config/pmt/env.test11.yaml``; username/password come
    from the CSV row whose ``scenario`` matches the executing scenario name.
    """
    from pages.pmt.sdt_isc_page import LoginPage

    cfg = _load_pmt_env_config()
    ewm = cfg["applications"]["ewm"]
    login_url = ewm["login_url"]
    home_url = ewm["home_url"]

    username = test_data.get("username") or os.getenv("EWM_USERNAME")
    password = test_data.get("password") or os.getenv("EWM_PASSWORD")
    if not username or not password:
        raise RuntimeError(
            "EWM credentials missing: provide them via the configured "
            "test_data CSV (scenario row) or EWM_USERNAME / EWM_PASSWORD env vars."
        )

    context = browser.new_context(**browser_context_args)
    page = context.new_page()

    login_page = LoginPage(page)
    try:
        login_page.complete_login(username, password, login_url)
    except Exception:
        # SSO/Okta flows often don't reach 'networkidle'; tolerate and continue.
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass

    # Okta may land on /signin/refresh-auth-state/... and auto-redirect back
    # to EWM after a short delay. Poll until we either reach the EWM host or
    # exhaust the budget.
    deadline = time.time() + 90
    ewm_host = "ewealthmanager.com"
    while time.time() < deadline:
        current = page.url.lower()
        if ewm_host in current and "ewmlogin/account/login" not in current:
            break
        try:
            page.wait_for_load_state("domcontentloaded", timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(1500)

    def _on_okta_login() -> bool:
        url = page.url.lower()
        if "okta" in url or "assetmark.com/oauth2" in url or "prompt=login" in url:
            return True
        try:
            return page.locator("input#okta-signin-username").is_visible(timeout=1500)
        except Exception:
            return False

    def _submit_okta_credentials() -> None:
        try:
            page.wait_for_selector(
                "input#okta-signin-username", state="visible", timeout=15000
            )
            page.fill("input#okta-signin-username", username)
            page.fill("input#okta-signin-password", password)
            page.click("input#okta-signin-submit[type='submit']")
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as exc:  # pragma: no cover - defensive
            print(f"Okta re-login attempt failed: {exc}")

    # Final attempt: explicitly navigate to home, re-authenticating at Okta
    # if EWM bounces us back to the sign-in page (prompt=login flow).
    for _ in range(3):
        try:
            page.goto(home_url, timeout=30000, wait_until="domcontentloaded")
        except Exception:
            pass
        try:
            page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception:
            pass
        page.wait_for_timeout(2000)

        if _on_okta_login():
            _submit_okta_credentials()
            page.wait_for_timeout(2000)
            continue

        if ewm_host in page.url.lower() and "ewmlogin/account/login" not in page.url.lower():
            break

    if ewm_host not in page.url.lower() or "ewmlogin/account/login" in page.url.lower():
        context.close()
        raise RuntimeError(f"EWM login failed; final URL: {page.url}")

    try:
        yield page
    finally:
        context.close()


@pytest.fixture
def test_data(request):
    """CSV row keyed by the BDD scenario name."""
    cfg = _load_pmt_env_config()
    rows = _load_test_data_rows(cfg)
    scenario_name = _resolve_scenario_name(request)
    for row in rows:
        if row.get("scenario", "").strip() == scenario_name.strip():
            return row
    # Fallback: first row
    return rows[0] if rows else {}


@pytest.fixture
def test_context(test_data):
    """Per-scenario mutable context dictionary used by step definitions."""
    return {"test_data": dict(test_data)}


# ---------------------------------------------------------------------------
# Page-object fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def account_list_page(authenticated_page):
    from pages.pmt.sdt_isc_page import AccountListPage

    return AccountListPage(authenticated_page)


@pytest.fixture
def clients_page(authenticated_page):
    from pages.pmt.sdt_isc_page import ClientsPage

    return ClientsPage(authenticated_page)


@pytest.fixture
def account_detail_page(authenticated_page):
    from pages.pmt.sdt_isc_page import AccountDetailPage

    return AccountDetailPage(authenticated_page)


@pytest.fixture
def change_investments_page(authenticated_page):
    from pages.pmt.sdt_isc_page import ChangeInvestmentsPage

    return ChangeInvestmentsPage(authenticated_page)


@pytest.fixture
def docusign_page(authenticated_page):
    from pages.pmt.sdt_isc_page import DocusignPage

    return DocusignPage(authenticated_page)


@pytest.fixture
def tracking_center_page(authenticated_page):
    from pages.pmt.sdt_isc_page import TrackingCenterPage

    return TrackingCenterPage(authenticated_page)


@pytest.fixture
def sdt_isc_page(authenticated_page):
    """PMT-scoped ``sdt_isc_page`` fixture using ``pages.pmt.sdt_isc_page``."""
    from pages.pmt.sdt_isc_page import SdtIscPage

    cfg = _load_pmt_env_config()
    baw_cfg = (cfg.get("applications", {}) or {}).get("baw_process_portal", {}) or {}
    base_url = baw_cfg.get("base_url", "")

    try:
        if isinstance(settings.config, dict):
            settings.config["baw_process_portal"] = baw_cfg
    except Exception:
        pass

    return SdtIscPage(authenticated_page, base_url=base_url)


# ---------------------------------------------------------------------------
# PMT SQL-query helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def pmt_sql_queries() -> dict:
    """Full PMT SQL queries YAML as a dict.

    Sourced from :file:`applicationqe/queries/pmt/sql_queries.yaml`. PMT steps
    should depend on this fixture (rather than any BAW path) so the queries
    folder used by the PMT suite stays under ``queries/pmt/``.
    """
    return _load_pmt_sql_queries()


@pytest.fixture
def pmt_query(pmt_sql_queries):
    """Resolve a named query under a category from the PMT queries YAML.

    Usage in a step::

        sql = pmt_query("am_billing", "sdt_isc_apl_account")
    """

    def _resolve(category: str, query_name: str) -> str:
        section = pmt_sql_queries.get(category, {}) or {}
        queries = section.get("queries", {}) or {}
        if query_name not in queries:
            raise KeyError(
                f"Query '{query_name}' not found under category '{category}' in "
                f"{_PMT_QUERIES_FILE}"
            )
        return queries[query_name]

    return _resolve


@pytest.fixture
def pmt_db_config(pmt_sql_queries):
    """Return the DB connection metadata for a query category in PMT queries YAML."""

    def _resolve(category: str) -> dict:
        section = dict(pmt_sql_queries.get(category, {}) or {})
        section.pop("queries", None)
        if not section:
            raise KeyError(
                f"Category '{category}' not found in {_PMT_QUERIES_FILE}"
            )
        return section

    return _resolve
