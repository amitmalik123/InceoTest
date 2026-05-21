# Setup Summary

One-page quickstart for the **salesforceqe** project.

## Prerequisites

- Python **3.10+** (3.11 recommended)
- Git
- Network access to the target Salesforce sandbox

## 1. Clone & enter the project

```powershell
git clone <repo-url>
cd qeautomation\salesforceqe
```

## 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
# Optional, for cross-browser runs
playwright install msedge
```

Dependencies (from [requirements.txt](../requirements.txt)):
- `pytest`, `pytest-playwright`, `pytest-bdd`, `pytest-xdist`, `pytest-html`
- `playwright`, `allure-pytest`
- `pyyaml`, `openpyxl`, `influxdb-client`

## 4. Configure credentials

Edit [data/salesforce/credentials.json](../data/salesforce/credentials.json) with
your sandbox URL, username and password. See
[ENVIRONMENT_GUIDE.md](ENVIRONMENT_GUIDE.md) for the file structure and
recommended ways to avoid committing real credentials.

## 5. Run a smoke test

```powershell
pytest -m smoke
```

## 6. View the report

```powershell
# HTML
start report.html

# Allure (after a run that produced allure-results)
allure serve reports\salesforce\allure-results
```

## Common run profiles

| Goal | Command |
|---|---|
| Smoke only | `pytest -m smoke` |
| Full regression | `pytest -m regression` |
| Parallel (4 workers) | `pytest -m regression -n 4` |
| Headed mode | `pytest -m smoke --headed` |
| Edge browser | `pytest -m smoke --browser msedge` |
| Single feature | `pytest tests/steps/salesforce/test_lead_conversion_bdd.py` |

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for the full matrix.
