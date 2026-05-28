# Setup Summary

> **One-Stop Installation and Configuration Reference**

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Project Dependencies](#project-dependencies)
4. [Credential Setup](#credential-setup)
5. [IDE Setup (VS Code)](#ide-setup)
6. [Verify Installation](#verify-installation)
7. [Common Setup Issues](#common-setup-issues)

---

## System Requirements

| Requirement | Minimum Version |
|-------------|----------------|
| Python | 3.11+ |
| pip | 23.0+ |
| Git | 2.40+ |
| Chromium (via Playwright) | Latest stable |
| OS | Windows 10+, Ubuntu 20.04+, macOS 12+ |

---

## Installation Steps

### Step 1 — Clone the repository

```bash
git clone <repo-url>
cd billingqe
```

### Step 2 — Create and activate a virtual environment

```powershell
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Set execution policy if needed
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4 — Install Playwright browsers

```bash
playwright install chromium

# Optional: install system dependencies (Linux only)
playwright install-deps chromium
```

### Step 5 — Configure credentials

```bash
cp config/billing/platformrevenuedashboard/strategistgroupmodel/env.qa.yaml \
   config/billing/platformrevenuedashboard/strategistgroupmodel/env.qa.local.yaml

# Edit env.qa.local.yaml and fill in username + password
```

### Step 6 — Verify setup

```bash
pytest tests/runners/ --collect-only -q
```

Expected output: `19 tests collected` (or more depending on CSV rows).

---

## Project Dependencies

All dependencies are pinned in `requirements.txt`:

| Package | Version | Purpose |
|---------|---------|--------|
| `pytest` | ≥8.0, <9.0 | Test runner |
| `pytest-playwright` | 0.4.4 | Playwright integration for pytest |
| `pytest-bdd` | ≥7.0 | Gherkin BDD support |
| `pytest-asyncio` | 0.21.1 | Async test support |
| `pytest-html` | ≥4.1.1 | HTML test reports |
| `pytest-xdist` | ≥3.5.0 | Parallel test execution |
| `playwright` | ≥1.42.0 | Browser automation engine |
| `allure-pytest` | ≥2.13.0 | Allure report integration |
| `pyyaml` | ≥6.0 | YAML config parsing |
| `cryptography` | ≥42.0.0 | Encryption utilities |
| `openpyxl` | ≥3.1.0 | Excel data support |
| `influxdb-client` | ≥1.38.0 | Metrics reporting |
| `black` | ≥24.2.0 | Code formatter (dev) |
| `flake8` | ≥7.0.0 | Linter (dev) |
| `mypy` | ≥1.8.0 | Type checker (dev) |
| `pytest-cov` | ≥4.1.0 | Coverage reports (dev) |

---

## Credential Setup

```yaml
# config/billing/platformrevenuedashboard/strategistgroupmodel/env.qa.local.yaml
application:
  base_url: "https://app-billing-ui-test.azurewebsites.net/"

credentials:
  username: "your.email@yourcompany.com"
  password: "YourPassword123"
```

This file is listed in `.gitignore` and will never be committed.

Alternatively, use environment variables:
```bash
export BILLING_USERNAME=your.email@yourcompany.com
export BILLING_PASSWORD=YourPassword123
```

---

## IDE Setup (VS Code)

Install the following extensions for the best experience:

| Extension | Purpose |
|-----------|--------|
| Python (Microsoft) | Python language support |
| Pylance | Type checking and intellisense |
| Cucumber (Gherkin) Full Support | `.feature` file syntax highlighting |
| GitLens | Git blame and history |
| Even Better TOML | `pyproject.toml` support |

**Recommended workspace settings** (`settings.json`):

```json
{
  "python.defaultInterpreterPath": ".venv/Scripts/python.exe",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/runners"],
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

---

## Verify Installation

Run a complete sanity check:

```bash
# 1. Confirm pytest finds all tests
pytest tests/runners/ --collect-only -q
# Expected: 19 items (or more)

# 2. Confirm no import errors
pytest tests/runners/ --co --tb=short

# 3. Run a single fast smoke test
pytest tests/runners/billing/platformrevenuedashboard/strategistgroupmodel/test_search_family_bdd_runner.py -v
```

---

## Common Setup Issues

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| `ModuleNotFoundError: fixtures` | Wrong working directory | Run pytest from `billingqe/` root |
| `playwright._impl._errors.Error: Executable doesn't exist` | Chromium not installed | Run `playwright install chromium` |
| `ValueError: Missing credentials` | No local YAML or env vars | Create `env.qa.local.yaml` or export env vars |
| `StepDefinitionNotFoundError` | Step text mismatch or import missing | Check `tests/conftest.py` imports all step modules |
| `FileNotFoundError: ...search_family_data.csv` | Data file missing | Ensure CSV files exist in `data/billing/.../strategistgroupmodel/` |
| Tests collected from `applicationqe` | Stale `.pyc` bytecode | Delete all `__pycache__` dirs and re-run |
| `PluginValidationError` for BDD hook | Hook arg name mismatch | Hook function signatures must match pytest-bdd hookspec exactly |

---

*Last updated: May 2026*
