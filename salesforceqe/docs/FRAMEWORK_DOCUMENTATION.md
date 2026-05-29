# Salesforce QE Automation Framework

End-to-end UI automation framework for the Salesforce platform built on
**pytest + Playwright (sync API) + pytest-bdd**, following the **Page Object
Model (POM)**.

This document describes the actual layout of the `salesforceqe/` project and
the conventions every page, feature, step and fixture must follow.

---

## 1. Tech Stack

| Concern                | Tool / Library                                    |
| ---------------------- | ------------------------------------------------- |
| Test runner            | `pytest`                                          |
| Browser automation     | `playwright` (sync API)                           |
| BDD                    | `pytest-bdd` (Gherkin features + step modules)    |
| Salesforce API / SOQL  | `simple-salesforce` (data seeding & verification) |
| Data-driven tests      | `openpyxl` (Excel/CSV)                            |
| Parallel execution     | `pytest-xdist`                                    |
| Reporting              | Allure, `pytest-html`, JUnit XML, InfluxDB        |
| Auth state reuse / MFA | Playwright storage state + TOTP                   |
| CI/CD                  | Azure Pipelines (`azure-pipelines/salesforce.yml`)|

---

## 2. Project Structure

Single-domain layout (`salesforce/`) — no multi-team subfolders.

```text
salesforceqe/
|
|-- conftest.py                 # Registers fixtures as a pytest plugin
|-- pytest.ini                  # Markers, pythonpath
|-- pyproject.toml
|-- requirements.txt
|-- sonar-project.properties
|-- README.md
|-- report.html                 # Latest pytest-html report
|
|-- pages/
|   |-- __init__.py
|   \-- salesforce/
|       |-- __init__.py
|       |-- loginPage.py
|       |-- homePage.py
|       |-- setupPage.py
|       |-- leadsPage_Fields.py
|       |-- leadsPage_HappyPath.py
|       |-- leadsPage_PicklistValues.py
|       \-- leadsPage_ValidationErrors.py
|
|-- tests/
|   |-- __init__.py
|   |-- conftest.py
|   |-- features/
|   |   \-- salesforce/
|   |       |-- Lead_Conversion.feature
|   |       \-- Lead_Page_Validation.feature
|   \-- steps/
|       \-- salesforce/
|           |-- common_steps.py
|           |-- test_lead_conversion_bdd.py
|           \-- test_lead_page_validation_bdd.py
|
|-- fixtures/
|   |-- __init__.py
|   \-- salesforce/
|       |-- __init__.py
|       \-- salesforce_fixtures.py
|
|-- data/
|   \-- salesforce/
|       \-- credentials.json    # Org URL, username, password, security token, TOTP
|
|-- utils/
|   |-- __init__.py
|   |-- logger.py
|   |-- settings.py
|   |-- allure_helpers.py
|   |-- auth_state_manager.py
|   |-- screenshot_helper.py
|   |-- test_data_loader.py
|   |-- influx_reporter.py
|   |-- randomString.py
|   |-- bdd_migration_helper.py
|   \-- enhanced_interactive_flow_designer.py
|
|-- azure-pipelines/
|   |-- salesforce.yml                    # Main pipeline
|   \-- templates/
|       \-- team-stage-salesforce.yml     # Reusable stage (params: environment, marker, workers, browser)
|
|-- config/                     # Environment configs (placeholder)
|-- queries/                    # SOQL query files
|-- reports/                    # JUnit / lint / security / Allure output
|                               #   reports/salesforce/allure-results
|                               #   reports/salesforce/allure-report
|                               #   reports/salesforce/pytest-report.html
|-- src/testScript/
|-- tools/
|
\-- docs/
    |-- README.md
    |-- FRAMEWORK_DOCUMENTATION.md   (this file)
    |-- BDD_GUIDE.md
    |-- TESTING_GUIDE.md
    |-- ENVIRONMENT_GUIDE.md
    |-- DEBUGGING_GUIDE.md
    |-- AZURE_PIPELINE_GUIDE.md
    |-- TAG_USAGE_GUIDE.md
    |-- CODE_QUALITY_REPORT.md
    \-- SETUP_SUMMARY.md
```

---

## 3. Page Object Model

Each Salesforce screen lives in `pages/salesforce/`. The Leads screen is
deliberately **split into multiple POMs** by responsibility so each file
stays focused and parallel-safe:

| File                              | Responsibility                                  |
| --------------------------------- | ----------------------------------------------- |
| `loginPage.py`                    | Login flow, MFA/TOTP entry                      |
| `homePage.py`                     | App launcher, global nav, search                |
| `setupPage.py`                    | Setup tree navigation                           |
| `leadsPage_Fields.py`             | Field-level locators & input methods            |
| `leadsPage_HappyPath.py`          | Create / convert lead happy-path actions        |
| `leadsPage_PicklistValues.py`     | Picklist value retrieval & selection            |
| `leadsPage_ValidationErrors.py`   | Inline validation & error-message assertions    |

### Conventions (enforced by `.github/instructions/salesforceqe.instructions.md`)

- **Lightning-safe selectors** — prefer `getByRole`, `getByLabel`,
  `getByText`; avoid brittle CSS / auto-generated ids.
- **Assertions** — use Playwright `expect()` with auto-waiting, not bare
  `assert`.
- **Iframes / Visualforce** — resolve via `frame_locator()` inside the POM,
  never in the step file.
- **Credentials** — read **only** from `data/salesforce/credentials.json`.
  Never hard-code.
- **POM split rule** — keep page files focused (locators + actions). Business
  flow orchestration belongs in step modules.

---

## 4. BDD Layout

Features and steps mirror each other under a `salesforce/` subfolder.

| Feature                          | Step module                          |
| -------------------------------- | ------------------------------------ |
| `Lead_Conversion.feature`        | `test_lead_conversion_bdd.py`        |
| `Lead_Page_Validation.feature`   | `test_lead_page_validation_bdd.py`   |

`common_steps.py` holds shared Given/When/Then (login, navigation, teardown)
reused by every scenario.

Each step module declares its scenarios with:

```python
from pytest_bdd import scenarios
scenarios("../../features/salesforce/Lead_Conversion.feature")
```

See [`BDD_GUIDE.md`](BDD_GUIDE.md) for authoring rules.

---

## 5. Fixtures

Fixtures live **outside** `tests/` so pytest cannot auto-discover them. The
root `conftest.py` registers them as a plugin:

```python
# salesforceqe/conftest.py
pytest_plugins = [
    "fixtures.salesforce.salesforce_fixtures",
]
```

`fixtures/salesforce/salesforce_fixtures.py` provides:

- Playwright `browser` / `context` / `page` fixtures
- Authenticated context with reused storage state (auth-state reuse)
- Salesforce REST/Bulk API client (`simple-salesforce`) for seeding/cleanup
- Per-worker data isolation helpers for `pytest-xdist`

---

## 6. Markers

Defined in `pytest.ini`. The current marker set is broad (inherited from the
STP-JOURNALS catalogue) and includes priorities, scopes, and capability
tags such as `bdd`, `e2e`, `smoke`, `critical`, `high`, `cross_browser`,
`data_driven`, `load_test`.

Run by marker:

```powershell
pytest -m "bdd and critical"
```

See [`TAG_USAGE_GUIDE.md`](TAG_USAGE_GUIDE.md) for the full marker catalogue
and selection patterns.

---

## 7. Reporting

| Output            | Location                                                |
| ----------------- | ------------------------------------------------------- |
| Allure HTML       | `reports/salesforce/allure-report/index.html`           |
| pytest-html       | `reports/salesforce/pytest-report.html`                 |
| JUnit XML         | `reports/salesforce/junit/junit-report.xml`             |
| Lint / security   | `reports/flake8-report.txt`, `reports/bandit-report.json` |
| Playwright traces | per-test under `test-results/` (on failure)             |
| InfluxDB metrics  | via `utils/influx_reporter.py` (opt-in)            |

See [`DEBUGGING_GUIDE.md`](DEBUGGING_GUIDE.md) for trace viewing and
[`CODE_QUALITY_REPORT.md`](CODE_QUALITY_REPORT.md) for lint outputs.

---

## 8. Environments & Credentials

- All environment-specific values resolve through `utils/settings.py`.
- Salesforce sign-in details live in `data/salesforce/credentials.json`
  (org URL, username, password, security token, TOTP secret for MFA).
- See [`ENVIRONMENT_GUIDE.md`](ENVIRONMENT_GUIDE.md).

---

## 9. CI/CD

- Pipeline entry point: `azure-pipelines/salesforce.yml`
- Reusable stage template: `azure-pipelines/templates/team-stage-salesforce.yml`
  - Parameters: `environment`, `marker`, `workers`, `browser`
- See [`AZURE_PIPELINE_GUIDE.md`](AZURE_PIPELINE_GUIDE.md).

---

## 10. Related Documentation

- [`README.md`](README.md) — quick start
- [`SETUP_SUMMARY.md`](SETUP_SUMMARY.md) — local setup
- [`TESTING_GUIDE.md`](TESTING_GUIDE.md) — how to run / write tests
- [`BDD_GUIDE.md`](BDD_GUIDE.md) — feature & step authoring
- [`ENVIRONMENT_GUIDE.md`](ENVIRONMENT_GUIDE.md) — env / credentials
- [`DEBUGGING_GUIDE.md`](DEBUGGING_GUIDE.md) — traces & troubleshooting
- [`TAG_USAGE_GUIDE.md`](TAG_USAGE_GUIDE.md) — pytest markers
- [`AZURE_PIPELINE_GUIDE.md`](AZURE_PIPELINE_GUIDE.md) — CI/CD
- [`CODE_QUALITY_REPORT.md`](CODE_QUALITY_REPORT.md) — lint / security
