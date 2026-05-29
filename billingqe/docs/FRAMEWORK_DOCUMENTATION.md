# Framework Documentation

> **Billing QE Automation — Architecture & Design Reference**  
> Platform Revenue Dashboard · Strategist Group Model (SGM)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Layer Breakdown](#layer-breakdown)
3. [Directory Deep-Dive](#directory-deep-dive)
4. [Fixture System](#fixture-system)
5. [Page Object Model](#page-object-model)
6. [Step Definition Design](#step-definition-design)
7. [BDD Runner Design](#bdd-runner-design)
8. [conftest.py Architecture](#conftestpy-architecture)
9. [Data Management](#data-management)
10. [Reporting Pipeline](#reporting-pipeline)
11. [Design Principles](#design-principles)

---

## Architecture Overview

The framework follows a clean **four-layer BDD architecture**:

```
┌─────────────────────────────────────────────────┐
│              Gherkin Feature Files               │  Business language — owned by QA/BA
├─────────────────────────────────────────────────┤
│           BDD Step Definitions (steps/)          │  Glue code — maps Gherkin to actions
├─────────────────────────────────────────────────┤
│           Page Object Model (pages/)             │  Browser interactions — no test logic
├─────────────────────────────────────────────────┤
│      Playwright Sync API (via pytest-playwright) │  Chrome automation engine
└─────────────────────────────────────────────────┘
```

**Orthogonal concerns** (fixtures, data, reporting) sit alongside all layers:

```
fixtures/   →  Dependency injection (browser, data, assertions, hooks)
data/       →  CSV-driven parametrize input
config/     →  Environment config (YAML) with local secret overrides
reports/    →  Allure results + HTML + log output
```

---

## Layer Breakdown

### Layer 1 — Feature Files (`tests/features/`)

Gherkin `.feature` files express test intent in human-readable language. They are **pure specification** — no Python, no selectors, no logic.

```gherkin
Feature: Create Model Family
  @create @family @regression
  Scenario: Create Model Family with valid data
    Given the user is logged into the application
    When the user navigates to Strategist Group Model
    And the user clicks Create Model Family button
    Then the user verifies family was created successfully
    And the user logs out
```

Feature files live in:
```
tests/features/platformrevenuedashboard/strategistgroupmodel/
```

### Layer 2 — BDD Runners (`tests/runners/`)

Runner files bind a Gherkin scenario to pytest parametrization. Each runner:
- Loads its test data from a CSV file at import time
- Uses `@pytest.mark.parametrize` to create one test per CSV row
- Calls `@scenario(FEATURE_PATH, SCENARIO_NAME)` using an absolute path

```python
REPO_ROOT = Path(__file__).resolve().parents[5]
FEATURE_DIR = REPO_ROOT / "tests" / "features" / "billing" / ... / "strategistgroupmodel"

@pytest.mark.family
@pytest.mark.parametrize("create_family_data_row", _ROWS, indirect=True)
@scenario(str(FEATURE_DIR / "create_family.feature"), "Create Model Family with valid data")
def test_create_model_family_with_valid_data(create_family_data_row):
    pass
```

Runner files live in:
```
tests/runners/platformrevenuedashboard/strategistgroupmodel/
```

### Layer 3 — Step Definitions (`tests/steps/`)

Step files implement the `@given`, `@when`, `@then` decorated functions. They orchestrate page-object calls. No selector logic lives here — all DOM interactions are delegated to page objects.

```python
@when("the user fills in the family form with the following data:")
def fill_family_form(create_family_page, create_family_data_row, datatable):
    create_family_page.create_family(create_family_data_row)
```

Steps are split into:
- `revenue_dashboard_common_steps.py` — shared login, navigation, submit, logout
- `strategistgroupmodel/common_steps.py` — SGM-level fixture overrides
- Per-feature step files (`create_family_steps.py`, `edit_family_steps.py`, …)

### Layer 4 — Page Object Model (`pages/`)

Each page object encapsulates all Playwright interactions for a given UI page or section. Page objects inherit from `BasePage` (located in `pages/platformrevenuedashboard/common/base_page.py`).

```python
class CreateFamilyPage(BasePage):
    def create_family(self, data: dict) -> None:
        # Fill form fields, handle dropdowns, submit
        ...
    def verify_family_created(self, expected_name: str) -> None:
        # Assert success dialog and result
        ...
```

Page objects for SGM live in:
```
pages/platformrevenuedashboard/
├── common/
│   ├── base_page.py          # Shared Playwright helpers
│   ├── login_page.py         # Azure AD login flow
│   └── navigation_page.py   # App navigation
└── strategistgroupmodel/
    ├── create_family_page.py
    ├── approve_reject_family_page.py
    ├── edit_family_page.py
    ├── search_model_page.py
    ├── approve_reject_model_page.py
    ├── edit_model_page.py
    ├── login_page.py
    └── navigation_page.py
```

---

## Directory Deep-Dive

```
billingqe/
├── config/platformrevenuedashboard/strategistgroupmodel/
│   ├── env.qa.yaml           # Base URLs (committed)
│   └── env.qa.local.yaml     # Credentials (git-ignored, local only)
│
├── data/platformrevenuedashboard/strategistgroupmodel/
│   └── *.csv                 # One CSV per scenario/feature
│
├── fixtures/
│   ├── browser_fixtures.py   # Playwright launch + context args
│   ├── assertion_fixtures.py # SoftAssertions class + soft_assert fixture
│   ├── data_fixtures.py      # TestDataManager + csv_data_manager factory
│   ├── hooks_fixtures.py     # BDD lifecycle hooks (log + screenshot)
│   ├── auth_fixtures.py      # Auth fixture placeholder
│   ├── page_fixtures.py      # Page fixture placeholder
│   └── db_fixtures.py        # DB fixture placeholder
│
├── pages/platformrevenuedashboard/
│   ├── common/base_page.py   # navigate_to, click, fill, wait helpers
│   ├── common/login_page.py  # Azure AD multi-step sign-in + logout
│   └── strategistgroupmodel/ # One page object per UI section
│
├── tests/
│   ├── conftest.py           # Single root conftest — all fixtures, hooks, steps
│   ├── features/             # .feature files only (no Python)
│   ├── runners/              # pytest parametrize + @scenario bindings
│   └── steps/                # @given/@when/@then implementations
│
├── reports/                  # Generated at runtime — not committed
├── pytest.ini                # Markers, paths, addopts, logging
└── requirements.txt          # Pinned dependencies
```

---

## Fixture System

All fixtures are modular and imported into the single `tests/conftest.py`:

| Module | Fixtures Provided |
|--------|------------------|
| `browser_fixtures.py` | `browser_type_launch_args`, `browser_context_args` |
| `assertion_fixtures.py` | `soft_assert` (auto-validating `SoftAssertions`) |
| `data_fixtures.py` | `csv_data_manager` factory, `TestDataManager` class |
| `hooks_fixtures.py` | `pytest_bdd_before_scenario/step/after/error` hooks |

### SoftAssertions

```python
def test_something(soft_assert):
    soft_assert.check(element.is_visible(), "Element should be visible")
    soft_assert.check(title == "Expected", "Title mismatch")
    # All failures collected and raised together at end of test
```

### TestDataManager

```python
manager = TestDataManager.from_csv(path)
row = manager.get_by(family_name="Acme Family")
all_rows = manager.filter_by(action="approve")
```

---

## Page Object Model

### BasePage (`common/base_page.py`)

All page objects extend `BasePage` which wraps raw Playwright calls with logging and timeout handling:

| Method | Purpose |
|--------|---------|
| `navigate_to(url)` | Navigate and log URL |
| `click(locator)` | Wait for visible, then click |
| `fill(locator, text)` | Wait for visible, then fill |
| `is_visible(locator)` | Safe visibility check |
| `wait_for_element(locator, state)` | Explicit waits |
| `screenshot(name)` | Capture screenshot bytes |

### LoginPage (`common/login_page.py`)

Handles the full Azure AD authentication flow:
1. Navigate to app URL
2. Detect if already authenticated
3. Handle username prompt with multiple selector fallbacks
4. Handle "Use another account" and sign-in option screens
5. Enter password and submit
6. Handle "Stay signed in" prompt
7. Verify app shell is loaded

### NavigationPage (`common/navigation_page.py`)

Handles in-app navigation to SGM and other modules.

---

## Step Definition Design

Steps follow a strict delegation pattern — they never contain selectors:

```
Step file                 Page Object Method
─────────────────────     ──────────────────────────
fill_family_form()    →   create_family_page.create_family(data)
verify_created()      →   create_family_page.verify_family_created(name)
click_approve()       →   approve_reject_family_page.approve_family(name)
```

Shared steps (login, navigate, submit, logout) are defined once in `revenue_dashboard_common_steps.py` and re-exported via `tests/conftest.py` for discovery by pytest-bdd.

---

## BDD Runner Design

Each runner is self-contained and responsible for:

1. **CSV loading at import time** (`_load_rows()`) — fails fast if data is missing
2. **Parametrization** — one test node per CSV data row
3. **Scenario binding** — `@scenario(abs_path, scenario_title)`
4. **No fixture logic** — all fixtures come from `tests/conftest.py`

```python
# Pattern used by all 7 runners
REPO_ROOT = Path(__file__).resolve().parents[5]
FEATURE_DIR = REPO_ROOT / "tests" / "features" / ... / "strategistgroupmodel"

@pytest.mark.<module_marker>
@pytest.mark.family
@pytest.mark.regression
@pytest.mark.parametrize("data_row", _ROWS, indirect=True)
@scenario(str(FEATURE_DIR / "feature_file.feature"), "Scenario Title")
def test_function(data_row):
    pass
```

---

## conftest.py Architecture

A single `tests/conftest.py` replaces the previous cascade of 4 conftest files. It:

1. Sets `billingqe/` as the repo root and inserts it first into `sys.path`
2. Adds SGM step and page dirs to `sys.path` for wildcard imports
3. Imports BDD lifecycle hooks from `fixtures/hooks_fixtures.py`
4. Re-exports all step definitions via `import *` (required for pytest-bdd string-based discovery)
5. Defines all page-object fixtures (`create_family_page`, `edit_family_page`, …)
6. Provides `pytest_collection_modifyitems` for deterministic family test ordering

---

## Data Management

Test data is stored in CSV files, one per feature. Each column maps to a form field or assertion value.

Example (`create_family_data.csv`):

| family_name | manager_type_code | program_name | create_style_code | is_uma_custom | … |
|-------------|-------------------|--------------|-------------------|---------------|---|
| Acme Family | CUSTOM | Core Growth | Y | N | … |

**Rules:**
- Blank fields are skipped — no mandatory field error is raised for intentionally empty data
- Boolean-like fields accept `Y`/`N`/`true`/`false`/`1`/`0`
- All rows are loaded at import time — change CSV then restart pytest to pick up changes

---

## Reporting Pipeline

| Report Type | Location | When Generated |
|-------------|----------|----------------|
| Allure XML results | `reports/…/allure-results/` | Every test run |
| HTML report | `reports/…/pytest_report.html` | Every test run |
| CLI log (INFO) | Terminal stdout | Every test run |
| File log (DEBUG) | `reports/…/pytest.log` | Every test run |
| Failure screenshots | `reports/…/screenshots/FAIL_*.png` | On step failure |

To serve the Allure dashboard locally:
```bash
allure serve reports/platformrevenuedashboard/strategistgroupmodel/allure-results
```

---

## Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Single Responsibility** | Runners bind scenarios; steps orchestrate; pages interact |
| **DRY** | Common login/nav steps defined once, re-exported everywhere |
| **Fail Fast** | CSV loading at import time; missing data raises immediately |
| **Isolation** | Each scenario gets a fresh browser context (function scope) |
| **Observability** | Every step logged at INFO; failures captured with screenshot |
| **No Magic Paths** | All file paths derived from `__file__` — no hardcoded strings |
| **Modular Fixtures** | One fixture module per concern; no monolithic file |

---

*Last updated: May 2026*


## Current Structure

```text
QEAutomation_Application/
|
|-- config/
|   |-- env.prod.yaml
|   |-- env.qa.yaml
|   |-- env.silo.yaml
|   |-- env.test11.yaml
|   |-- env.test12.yaml
|   |-- naw/
|   |-- baw/
|   |-- stp/
|   |   |-- stp-ict/
|   |   \-- stp-journals/
|   |-- oam/
|   |-- model-management/
|   |-- proposal/
|   \-- full-regression/
|
|-- data/
|   |-- test_data.prod.csv
|   |-- test_data.qa.csv
|   |-- test_data.silo.csv
|   |-- test_data.test11.csv
|   |-- test_data.test12.csv
|   |-- naw/
|   |-- baw/
|   |-- stp/
|   |   |-- stp-ict/
|   |   \-- stp-journals/
|   |-- oam/
|   |-- model-management/
|   |-- proposal/
|   \-- full-regression/
|
|-- queries/
|   |-- naw/
|   |-- baw/
|   |-- stp/
|   |   |-- stp-ict/
|   |   \-- stp-journals/
|   |-- oam/
|   |-- model-management/
|   |-- proposal/
|   \-- full-regression/
|
|-- pages/
|   |-- __init__.py
|   |-- base_page.py
|   |-- login_page.py
|   |-- clients_page.py
|   |-- account_list_page.py
|   |-- account_detail_page.py
|   |-- roth_conversion_page.py
|   |-- tracking_center_page.py
|   |-- ewm/
|   |-- baw/
|   \-- navbar/
|
|-- tests/
|   |-- __init__.py
|   |-- conftest.py
|   |-- ui/
|   |   \-- test_roth_conversion_cucumber.py
|   |-- features/
|   |   |-- roth_conversion.feature
|   |   |-- naw/
|   |   |-- baw/
|   |   |-- stp/
|   |   |   |-- stp-ict/
|   |   |   \-- stp-journals/
|   |   |-- oam/
|   |   |-- model-management/
|   |   |-- proposal/
|   |   \-- full-regression/
|   \-- steps/
|       |-- test_roth_conversion_steps.py
|       |-- naw/
|       |-- baw/
|       |-- stp/
|       |   |-- stp-ict/
|       |   \-- stp-journals/
|       |-- oam/
|       |-- model-management/
|       |-- proposal/
|       \-- full-regression/
|
|-- utils/
|   |-- __init__.py
|   |-- logger.py
|   |-- settings.py
|   \-- influx_reporter.py
|
|-- reports/
|   |-- naw/
|   |-- baw/
|   |-- stp/
|   |   |-- stp-ict/
|   |   |-- stp-journals/
|   |   |   |-- allure-results/
|   |   |   \-- allure-report/
|   |-- oam/
|   |-- model-management/
|   |-- proposal/
|   \-- full-regression/
|   |-- pytest_report.html
|   |-- junit.xml
|   |-- flake8-report.txt
|   |-- pylint-report.txt
|   \-- bandit-report.json
|
|-- test-results/
|-- fixtures/
|-- src/
|   \-- testScript/
|-- tools/
|
|-- azurePipeline.yaml
|-- pyproject.toml
|-- requirements.txt
|-- run_tests.bat
|-- generate_allure_report.bat
|-- sonar-project.properties
|
\-- docs/
	|-- README.md
	|-- FRAMEWORK_DOCUMENTATION.md
	|-- BDD_GUIDE.md
	|-- TESTING_GUIDE.md
	|-- ENVIRONMENT_GUIDE.md
	|-- DEBUGGING_GUIDE.md
	|-- AZURE_PIPELINE_GUIDE.md
	|-- TAG_USAGE_GUIDE.md
	|-- CODE_QUALITY_REPORT.md
	\-- SETUP_SUMMARY.md
```

## Notes

- `stp-ict` and `stp-journals` are nested under `stp` in each applicable folder.
- `full-regression` folder contains cross-domain regression test assets.
- All markdown documentation files are kept in the `docs` folder.
