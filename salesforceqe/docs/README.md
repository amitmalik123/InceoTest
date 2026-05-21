# salesforceqe — Documentation Index

Test automation framework for **Salesforce** (Monarch Console / FSC) built on
**pytest + Playwright (sync API)** with **pytest-bdd** for Gherkin scenarios and
**Allure** for reporting.

## Project at a glance

| Area | Path |
|---|---|
| Page Objects | [pages/salesforce/](../pages/salesforce/) |
| Feature files (Gherkin) | [tests/features/salesforce/](../tests/features/salesforce/) |
| Step definitions | [tests/steps/salesforce/](../tests/steps/salesforce/) |
| Fixtures | [fixtures/salesforce/salesforce_fixtures.py](../fixtures/salesforce/salesforce_fixtures.py) |
| Test data / credentials | [data/salesforce/credentials.json](../data/salesforce/credentials.json) |
| Utilities | [utils/](../utils/) |
| Azure Pipeline | [azure-pipelines/salesforce.yml](../azure-pipelines/salesforce.yml) |
| Pytest config | [pytest.ini](../pytest.ini) |
| Root conftest | [conftest.py](../conftest.py) |

## Documents in this folder

| File | Purpose |
|---|---|
| [FRAMEWORK_DOCUMENTATION.md](FRAMEWORK_DOCUMENTATION.md) | Folder layout and module responsibilities |
| [SETUP_SUMMARY.md](SETUP_SUMMARY.md) | One-page quickstart |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | How to run tests (markers, workers, browsers) |
| [BDD_GUIDE.md](BDD_GUIDE.md) | Authoring features, steps, and fixtures |
| [ENVIRONMENT_GUIDE.md](ENVIRONMENT_GUIDE.md) | Environments, credentials, auth state |
| [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md) | Traces, screenshots, logs, Allure |
| [AZURE_PIPELINE_GUIDE.md](AZURE_PIPELINE_GUIDE.md) | CI pipeline structure and parameters |
| [TAG_USAGE_GUIDE.md](TAG_USAGE_GUIDE.md) | Using pytest markers / BDD tags |
| [CODE_QUALITY_REPORT.md](CODE_QUALITY_REPORT.md) | flake8 / bandit / SonarQube setup |

## Quickstart

```powershell
cd salesforceqe
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
pytest -m smoke
```

See [SETUP_SUMMARY.md](SETUP_SUMMARY.md) for full setup.
