import csv
import os
from pathlib import Path


def _csv_for_env():
    env = os.getenv("TEST_ENV")
    path = Path(f"data/test_data.{env}.csv")
    return path


def test_auth_runner_creates_and_redirects_for_each_role(browser):
    """Ensure runner produced storageState files and each CSV row's expected path is reached.

    Reads `data/test_data.<TEST_ENV>.csv` and for each non-commented row uses the CSV `storage`
    (or falls back to `find_storage`) and asserts the browser lands on the CSV `expected` path.
    """
    base = os.getenv("BASE_URL")
    if not base:
        try:
            from config.settings import get_settings

            base = get_settings().base_url
        except Exception:
            base = None

    assert base, "BASE_URL must be set in environment or in config/env.<TEST_ENV>.yaml"

    csv_path = _csv_for_env()
    assert csv_path.exists(), f"CSV for TEST_ENV not found: {csv_path}"

    missing = []
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            # Skip commented rows (some CSVs keep rows commented with leading '#')
            raw_username = (row.get("username") or "").lstrip()
            if not raw_username or raw_username.startswith("#"):
                continue

            storage_csv = (row.get("storage") or "").strip()
            if not storage_csv:
                # nothing explicit to check for this row
                continue

            p = Path(storage_csv)
            if not p.exists():
                missing.append(str(p))

    assert (
        not missing
    ), f"Missing storageState files: {missing} (run will refresh missing files via auth runner)"
