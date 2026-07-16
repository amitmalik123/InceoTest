"""
Fixtures for Model Management BDD tests.

Provides:
  - smi_login_page   — SMIHomePage instance wired to base_url from config
  - credentials      — internal agent credentials from test_data CSV
  - executive_credentials — executive agent credentials from test_data CSV
"""
import csv
import os
from pathlib import Path

import pytest
import yaml

from pages.model_management.smi.smi_home_page import SMIHomePage


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def _load_config() -> dict:
    """Load the model-management env config YAML for the current ENV."""
    env = os.getenv("TEST_ENV", os.getenv("ENV", "test11"))
    repo_root = Path(__file__).parent.parent.parent.parent.parent  # applicationqe/
    config_path = repo_root / "config" / "model-management" / "smi" / f"env.{env}.yaml"
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}. "
            f"Check ENV env var (current: '{env}') and config/model-management/smi/ folder."
        )
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def _load_csv_data(csv_filename: str) -> list:
    """Load all rows from a CSV in data/model-management/smi/."""
    env = os.getenv("TEST_ENV", os.getenv("ENV", "test11"))
    repo_root = Path(__file__).parent.parent.parent.parent.parent  # applicationqe/
    csv_path = repo_root / "data" / "model-management" / "smi" / csv_filename
    if not csv_path.exists():
        raise FileNotFoundError(f"Test data CSV not found: {csv_path}")
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def smi_config() -> dict:
    """Session-scoped config dict loaded from env YAML."""
    return _load_config()


@pytest.fixture
def smi_login_page(page, smi_config):
    """Return an SMIHomePage instance bound to the configured base_url."""
    base_url = smi_config.get("application", {}).get("base_url", "")
    return SMIHomePage(page, base_url=base_url)


@pytest.fixture
def credentials(request, smi_config):
    """
    Agent credentials resolved by the current test's pytest marker.

    Marker → CSV file (env suffix applied automatically):
      SMI_AdminAgent     → test_Admin_data.{env}.csv     / ADMIN_USERNAME + ADMIN_PASSWORD
      SMI_ExternalAgent  → test_External_data.{env}.csv  / EXTERNAL_USERNAME + EXTERNAL_PASSWORD
      SMI_ExecutiveAgent → test_Executive_data.{env}.csv / EXECUTIVE_USERNAME + EXECUTIVE_PASSWORD
      SMI_InternalAgent  → test_data.{env}.csv           / INTERNAL_USERNAME + INTERNAL_PASSWORD
      (default)          → test_data.{env}.csv           / INTERNAL_USERNAME + INTERNAL_PASSWORD
    """
    env = os.getenv("TEST_ENV", os.getenv("ENV", "test11"))
    marker_names = {m.name for m in request.node.iter_markers()}

    if "SMI_AdminAgent" in marker_names:
        csv_file, env_user, env_pass, label = (
            f"test_Admin_data.{env}.csv", "ADMIN_USERNAME", "ADMIN_PASSWORD", "admin",
        )
    elif "SMI_ExternalAgent" in marker_names:
        csv_file, env_user, env_pass, label = (
            f"test_External_data.{env}.csv", "EXTERNAL_USERNAME", "EXTERNAL_PASSWORD", "external",
        )
    elif "SMI_ExecutiveAgent" in marker_names:
        csv_file, env_user, env_pass, label = (
            f"test_Executive_data.{env}.csv", "EXECUTIVE_USERNAME", "EXECUTIVE_PASSWORD", "executive",
        )
    else:  # SMI_InternalAgent or untagged
        csv_file, env_user, env_pass, label = (
            f"test_data.{env}.csv", "INTERNAL_USERNAME", "INTERNAL_PASSWORD", "internal",
        )

    # Try CSV first
    try:
        rows = _load_csv_data(csv_file)
        if rows:
            return {"username": rows[0]["username"], "password": rows[0]["password"]}
    except FileNotFoundError:
        pass

    # Fallback to environment variables
    username = os.getenv(env_user, "")
    password = os.getenv(env_pass, "")
    if username and password:
        return {"username": username, "password": password}

    raise RuntimeError(
        f"No {label} agent credentials found for env '{env}'. "
        f"Provide '{csv_file}' in data/model-management/smi/ or set "
        f"{env_user} / {env_pass} environment variables."
    )


@pytest.fixture(scope="session")
def executive_credentials(smi_config):
    """
    Executive agent credentials (kept for backward compatibility).
    Prefer using the unified `credentials` fixture in new tests.
    """
    env = os.getenv("TEST_ENV", os.getenv("ENV", "test11"))
    try:
        rows = _load_csv_data(f"test_Executive_data.{env}.csv")
        if rows:
            return {"username": rows[0]["username"], "password": rows[0]["password"]}
    except FileNotFoundError:
        pass

    username = os.getenv("EXECUTIVE_USERNAME", "")
    password = os.getenv("EXECUTIVE_PASSWORD", "")
    if username and password:
        return {"username": username, "password": password}

    raise RuntimeError(
        f"No executive agent credentials found for env '{env}'. "
        "Provide a test_Executive_data CSV or set EXECUTIVE_USERNAME / EXECUTIVE_PASSWORD."
    )


@pytest.fixture
def authenticated_page(page):
    """
    SMI-specific override of authenticated_page.

    SMI tests manage their own login flow via smi_login_page. This fixture
    exists so that the global hooks (hooks_fixtures.py) can resolve a page
    object for screenshot capture without triggering EWM/Okta authentication.
    """
    return page
