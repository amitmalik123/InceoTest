# Migration Plan: `application/ModelManagement_SMI` → `ModelManagement_SMI` (Monorepo)

**Date:** May 18, 2026  
**Author:** GitHub Copilot  
**Source Branch:** `origin/application/ModelManagement_SMI` (commit `8e0214fcc`)  
**Target Branch:** `ModelManagement_SMI` (local) → PR into `develop`  
**Reference Template:** STP-Journals implementation

---

## Table of Contents

1. [High-Level Migration Strategy](#1-high-level-migration-strategy)
2. [Folder / Module Differences](#2-folder--module-differences)
3. [Dependency Changes](#3-dependency-changes)
4. [Build / Configuration Updates](#4-build--configuration-updates)
5. [CI/CD Impact](#5-cicd-impact)
6. [Shared Library Integration](#6-shared-library-integration)
7. [Potential Merge Conflicts & Breaking Changes](#7-potential-merge-conflicts--breaking-changes)
8. [Required Refactoring Steps](#8-required-refactoring-steps)
9. [Recommended Migration Order](#9-recommended-migration-order)
10. [Validation / Testing Strategy](#10-validation--testing-strategy)
11. [Rollback Considerations](#11-rollback-considerations)
12. [Pre-Migration Blockers (Critical)](#12-pre-migration-blockers-critical)

---

## 1. High-Level Migration Strategy

The source branch (`origin/application/ModelManagement_SMI`) contains existing Model Management
Playwright/pytest tests written in a flat, pre-monorepo directory layout. The target branch
(`ModelManagement_SMI`) is a fresh branch off `develop` that already has the monorepo skeleton in
place (empty `.gitkeep` placeholder directories for model-management under every relevant folder).

The migration follows a **lift-and-adapt** approach:

1. **Fetch & Inventory** — Pull the source branch and catalogue every file before touching anything.
2. **Scaffold** — Create the missing monorepo directories following the STP-Journals reference pattern.
3. **Migrate Code** — Copy source files into the correct monorepo locations and adapt imports/structure.
4. **Fix Configuration** — Resolve the five pre-migration blockers identified below.
5. **Validate** — Run pytest collection, lint, and a smoke suite before raising the PR.

No code is deleted from the remote source branch at any stage. `develop` is not touched until
the full validation passes on the local feature branch.

---

## 2. Folder / Module Differences

### Current State (target branch — monorepo placeholders only)

```
applicationqe/
├── config/model-management/          # .gitkeep only
├── data/model-management/            # .gitkeep only
├── pages/                            # no model-management sub-directory
├── queries/model-management/         # .gitkeep only
├── reports/                          # no model-management sub-directory
├── tests/
│   ├── features/model-management/   # .gitkeep only
│   └── steps/model-management/      # .gitkeep only
```

### Source Branch (pre-monorepo, flat layout — to be mapped)

```
(flat / custom structure — exact inventory determined in Phase 0 git diff)
├── pages/          ← MM page objects (flat, no locators/ sub-dir)
├── tests/          ← feature files + step definitions combined
├── config/         ← single config file or hardcoded values
└── data/           ← test data files (CSV / JSON / Excel)
```

### Target State After Migration (follows STP-Journals pattern)

```
applicationqe/
├── config/model-management/
│   ├── env.test11.yaml
│   ├── env.test12.yaml
│   ├── env.qa.yaml
│   ├── env.silo.yaml
│   └── env.prod.yaml
├── data/model-management/
│   ├── test_data.test11.csv
│   ├── test_data.test12.csv
│   ├── test_data.qa.csv
│   ├── test_data.silo.csv
│   ├── test_data.prod.csv
│   └── runtime/
├── pages/model-management/
│   ├── __init__.py
│   ├── base_page.py
│   ├── <mm_specific_page>.py
│   └── locators/
│       ├── __init__.py
│       └── <mm_specific_locators>.py
├── queries/model-management/
│   └── <mm_queries>.sql              # if any
├── reports/model-management/
│   └── allure-results/               # auto-created by pytest
├── tests/
│   ├── features/model-management/
│   │   ├── conftest.py
│   │   └── e2e/
│   │       └── *.feature
│   └── steps/model-management/
│       ├── __init__.py
│       ├── flows/
│       │   ├── __init__.py
│       │   └── <mm_flow>.py
│       └── validations/
│           ├── __init__.py
│           └── <mm_validations>.py
```

### Structural Mapping Table

| Source Branch Path | Target Monorepo Path |
|---|---|
| `pages/*.py` | `applicationqe/pages/model-management/*.py` |
| Inline locators / selectors | `applicationqe/pages/model-management/locators/*.py` |
| `tests/*.feature` | `applicationqe/tests/features/model-management/e2e/*.feature` |
| `tests/steps/*.py` (flow logic) | `applicationqe/tests/steps/model-management/flows/*.py` |
| `tests/steps/*.py` (assertion logic) | `applicationqe/tests/steps/model-management/validations/*.py` |
| `config/*.yaml` | `applicationqe/config/model-management/env.{env}.yaml` |
| `data/*.csv / *.json` | `applicationqe/data/model-management/test_data.{env}.csv` |
| `queries/*.sql` | `applicationqe/queries/model-management/*.sql` |

---

## 3. Dependency Changes

### Current `requirements.txt` (target branch)

```
pytest>=8.0.0,<9.0.0
pytest-playwright==0.4.4
pytest-asyncio==0.21.1
pytest-html>=4.1.1
pytest-xdist>=3.5.0
pytest-bdd>=7.0.0
playwright>=1.42.0
allure-pytest>=2.13.0
pyyaml>=6.0
openpyxl>=3.1.0
influxdb-client>=1.38.0
black>=24.2.0
flake8>=7.0.0
mypy>=1.8.0
pytest-cov>=4.1.0
```

### Action Required

1. **Phase 0 (inventory):** Extract `requirements.txt` or dependency list from source branch.
2. Compare against current `requirements.txt`.
3. Add any MM-specific packages not already present (e.g., additional API clients, data-processing
   libraries used by MM tests).
4. Run `pip check` after adding to verify no version conflicts.
5. Re-pin any packages that conflict with existing pinned versions.

> **Risk:** Medium — source branch may use a different pinned version of `pytest-playwright`.
> Resolution: prefer the **higher** compatible version; run the full STP-Journals smoke suite
> after updating to confirm no regression.

---

## 4. Build / Configuration Updates

### 4.1 `pytest.ini` — Add Model Management Markers

All 80+ current markers target STP-Journals. The following MM-specific markers must be added:

```ini
# Add inside [pytest] markers section:
model_management: Model Management BDD marker
model_management_smoke: Model Management smoke test marker
wrapper_model: MM wrapper model test marker
smi: SMI-specific Model Management marker
portfolio_rebalancing: Portfolio rebalancing flow marker
model_creation: Model creation workflow marker
model_update: Model update workflow marker
model_deletion: Model deletion workflow marker
```

Exact marker names depend on what tags are used in the source branch `.feature` files
(confirm in Phase 0 inventory).

### 4.2 `utils/settings.py` — Make Config Path Team-Agnostic

**Current (hardcoded to STP-Journals):**

```python
team_config = repo_root / "config" / "stp" / "stp-journals" / f"env.{env}.yaml"
```

**Required change — introduce `TEAM_NAME` env variable:**

```python
team_name = os.getenv("TEAM_NAME", "stp/stp-journals")
team_config = repo_root / "config" / team_name / f"env.{env}.yaml"
```

MM tests would then set `TEAM_NAME=model-management` before running.  
The existing `TEST_CONFIG_PATH` override continues to work as an escape hatch.  
Default `stp/stp-journals` preserves all current STP-Journals behavior — **no regression**.

### 4.3 `config/model-management/env.{env}.yaml` — New Config Files

Create one file per environment following the STP-Journals YAML schema:

```yaml
# Example: config/model-management/env.test11.yaml
environment: test11

application:
  base_url: "https://test11.<mm-app-domain>.com/"
  login_url: "https://test11.<mm-app-domain>.com/login"
  timeout: 30000

browser:
  browser_type: "chromium"
  headless: false
  slow_mo: 0
  viewport:
    width: 1280
    height: 720
  args:
    - "--start-maximized"

test:
  screenshot_on_failure: true
  video: "on"
  trace: "retain-on-failure"

reporting:
  allure_results: "reports/model-management/allure-results"
  html_report: "reports/model-management/pytest_report.html"

data:
  test_data_csv: "data/model-management/test_data.test11.csv"
```

Populate actual URLs and settings from the source branch config.

### 4.4 `pyproject.toml` — Currently Empty

No action required unless the source branch uses it for tool configuration (e.g., mypy, black).
Check in Phase 0 and populate if needed.

### 4.5 `sonar-project.properties` — Currently Empty

If SonarQube scanning is required for MM, add:

```properties
sonar.projectKey=qeautomation-model-management
sonar.sources=applicationqe/pages/model-management,applicationqe/tests/steps/model-management
sonar.tests=applicationqe/tests/features/model-management
sonar.python.coverage.reportPaths=reports/model-management/coverage.xml
```

---

## 5. CI/CD Impact

### 5.1 Issues in Current `model-management.yml`

| Issue | Current Value | Required Fix |
|---|---|---|
| Path triggers use spaces | `'data/Model Management/**'` | `'applicationqe/data/model-management/**'` |
| No `applicationqe/` prefix | `'tests/features/Model Management/**'` | `'applicationqe/tests/features/model-management/**'` |
| Pool agent mismatch | `vmImage: ubuntu-latest` | pool label `ubuntu2204-qa` (matches `team-stage.yml`) |
| `featurePath` parameter | `tests/features/Model Management` | `tests/features/model-management` |
| Missing manual trigger params | none | Add `environment`, `marker`, `workers`, `browser` parameters |

### 5.2 Corrected `model-management.yml` Structure

```yaml
name: model-management-$(Date:yyyyMMdd)$(Rev:.r)

parameters:
  - name: environment
    displayName: Environment
    type: string
    default: test11
  - name: marker
    displayName: Test Marker
    type: string
    default: smoke
  - name: workers
    displayName: Parallel Workers
    type: string
    default: '1'
  - name: browser
    displayName: Browser
    type: string
    default: chromium

trigger:
  branches:
    include:
      - main
      - develop
  paths:
    include:
      - 'applicationqe/data/model-management/**'
      - 'applicationqe/config/model-management/**'
      - 'applicationqe/tests/features/model-management/**'
      - 'applicationqe/tests/steps/model-management/**'
      - 'applicationqe/pages/model-management/**'
      - 'applicationqe/queries/model-management/**'
      - 'applicationqe/azure-pipelines/templates/**'
      - 'applicationqe/requirements.txt'

pr:
  branches:
    include:
      - main
      - develop
  paths:
    include:
      - 'applicationqe/data/model-management/**'
      - 'applicationqe/config/model-management/**'
      - 'applicationqe/tests/features/model-management/**'
      - 'applicationqe/tests/steps/model-management/**'
      - 'applicationqe/pages/model-management/**'
      - 'applicationqe/queries/model-management/**'
      - 'applicationqe/azure-pipelines/templates/**'
      - 'applicationqe/requirements.txt'

pool:
  name: ubuntu2204-qa

stages:
  - template: templates/team-stage.yml
    parameters:
      stageName: MODEL_MANAGEMENT
      teamDisplay: Model Management
      featurePath: tests/features/model-management
      environment: ${{ parameters.environment }}
      marker: ${{ parameters.marker }}
      workers: ${{ parameters.workers }}
      browser: ${{ parameters.browser }}
```

### 5.3 Full Regression Pipeline

Check `azure-pipelines/full_regression.yml` — if it already references STP stages, add the
`MODEL_MANAGEMENT` stage in the same pattern.

### 5.4 Impact on Other Pipelines

No other pipeline files are affected. Path-based triggers ensure that:
- A change under `applicationqe/data/model-management/` only triggers `model-management.yml`.
- Changes under `applicationqe/data/stp/` only trigger STP pipelines.

---

## 6. Shared Library Integration Considerations

| Utility | Current Behavior | MM Compatibility | Action |
|---|---|---|---|
| `utils/settings.py` | Hardcoded to `stp/stp-journals` path | **Incompatible** | Refactor with `TEAM_NAME` env var (see §4.2) |
| `utils/test_data_loader.py` | CSV dot-notation format | Compatible if MM CSV uses same schema | Verify column format in Phase 0; extend if schema differs |
| `utils/auth_state_manager.py` | Generic auth state caching | Compatible if MM uses same auth flow | Verify MM app login mechanism; extend if OAuth or SSO differs |
| `utils/allure_helpers.py` | Team-agnostic Allure wrappers | Compatible — no changes needed | None |
| `utils/influx_reporter.py` | Team-agnostic InfluxDB reporting | Compatible — no changes needed | None |
| `utils/logger.py` | Team-agnostic logging | Compatible — no changes needed | None |
| `pages/base_page.py` | Root base page | Compatible | MM page objects should inherit from `pages/ewm/base_page.py` (richer logging) |
| `pages/ewm/base_page.py` | Enhanced base page (ewm-scoped) | **Preferred base for MM pages** | MM page objects extend this class; move to `pages/base_page.py` long-term |

---

## 7. Potential Merge Conflicts & Breaking Changes

| Risk | Severity | Details | Mitigation |
|---|---|---|---|
| `settings.py` refactor breaks STP-Journals tests | **High** | Changing the config path logic affects all existing teams using the singleton `settings` instance | Default `TEAM_NAME` to `stp/stp-journals`; run STP smoke suite after the change |
| Source branch `conftest.py` conflicts with root `tests/conftest.py` | **Medium** | Source may define fixtures with the same names (e.g., `browser_context_args`) | Scope MM fixtures to `tests/features/model-management/conftest.py` — pytest fixture scoping handles collision automatically |
| Playwright locator strategy differs from EWM pattern | **Medium** | Source may use fragile CSS/XPath instead of role/text selectors | Review all locators in Phase 0; standardize to Playwright recommended selectors |
| `requirements.txt` version conflicts | **Medium** | MM source may pin older/newer versions of shared packages | Run `pip check` and `pytest --collect-only` in a clean venv after updating |
| Step text in feature files has no matching step definition | **Low** | Source step phrasing may not match any step in the monorepo | Run `pytest --collect-only` — unmatched steps surface as `StepDefinitionNotFoundError` |
| MM pipeline triggers on wrong paths after migration | **Low** | Space-vs-hyphen mismatch means pipeline may never trigger | Fix path triggers in Phase 3 before merging |
| Duplicate markers in `pytest.ini` | **Low** | MM markers may accidentally match STP test scope | Use distinct MM-specific marker names (prefix `model_management_`) |

---

## 8. Required Refactoring Steps

### 8.1 Page Objects

- Flatten page objects into `pages/model-management/` (one file per page).
- Extract all inline CSS/XPath/text selectors into `pages/model-management/locators/` files.
- Replace any `page.locator("...")` calls hardcoded inside page methods with named locator properties.
- Ensure every page class inherits from `pages.ewm.base_page.BasePage`.

### 8.2 Step Definitions

- Separate step files into two categories:
  - **Flows** (`flows/`): Steps that orchestrate multi-page sequences (calls page object methods in order).
  - **Validations** (`validations/`): Steps that assert/verify UI state (calls `expect()` or `allure_helpers`).
- Each flow/validation file should be focused on one functional area (login, model creation, review, etc.).

### 8.3 Import Paths

All imports in migrated files must use monorepo-relative paths:

```python
# BEFORE (source branch — flat layout)
from pages.model_page import ModelPage
from utils import settings

# AFTER (monorepo layout)
from pages.model_management.model_page import ModelPage
from utils.settings import settings
```

Ensure `sys.path` is set correctly — `tests/conftest.py` already inserts `project_root`
(`applicationqe/`) into `sys.path`, so relative imports from `applicationqe/` root work
without additional path manipulation.

### 8.4 Feature File Tags

Audit all `@tag` annotations in source feature files:
- Remove any tags referencing the old branch name or non-standard conventions.
- Add `@model_management` as the base tag on every MM scenario.
- Add `@smoke` to the minimal set required for CI pipeline smoke run.
- Add `@regression` to the full suite.

### 8.5 `__init__.py` Files

Every new Python package directory requires an `__init__.py`:

```
pages/model-management/__init__.py
pages/model-management/locators/__init__.py
tests/steps/model-management/__init__.py
tests/steps/model-management/flows/__init__.py
tests/steps/model-management/validations/__init__.py
```

---

## 9. Recommended Migration Order

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 0: Fetch & Inventory (prerequisite — no code changes) │
│  git fetch origin application/ModelManagement_SMI            │
│  git diff develop..origin/application/ModelManagement_SMI    │
│    --name-only --diff-filter=A                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────┐
│  PHASE 1: Directory Scaffolding       │
│  Create all new dirs + __init__.py    │
│  Remove .gitkeep from populated dirs  │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐   ┌───────────────────────────────────┐
│  PHASE 2: Code Migration              │   │  PHASE 4: Shared Library Review   │
│  Copy & adapt page objects            │   │  (can run in parallel with Ph 2)  │
│  Copy & adapt feature files           │   │  Audit utils/ compatibility       │
│  Split steps → flows/ + validations/  │   │  Verify auth_state_manager        │
│  Fix all import paths                 │   │  Verify test_data_loader schema    │
└───────────────┬───────────────────────┘   └───────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  PHASE 3: Configuration Fixes         │
│  Fix model-management.yml (5 issues)  │
│  Refactor settings.py (TEAM_NAME)     │
│  Add MM markers to pytest.ini         │
│  Create config/model-management/      │
│  Update requirements.txt if needed    │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  PHASE 5: Validation                  │
│  pytest --collect-only (MM only)      │
│  flake8 lint on new code              │
│  Pipeline YAML syntax check           │
│  Smoke run vs test11                  │
│  STP regression check (no breakage)   │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  PR: ModelManagement_SMI → develop    │
└───────────────────────────────────────┘
```

---

## 10. Validation / Testing Strategy

### Phase 5 Checklist

| Check | Command | Pass Criteria |
|---|---|---|
| Pytest discovery | `pytest applicationqe/tests/features/model-management/ --collect-only` | 0 errors, all scenarios collected |
| Import resolution | `python -c "from pages.model_management.<page> import <Class>"` | No `ModuleNotFoundError` |
| Flake8 lint | `flake8 applicationqe/pages/model-management/ applicationqe/tests/steps/model-management/` | 0 errors (warnings acceptable) |
| Config loading | `TEAM_NAME=model-management TEST_ENV=test11 python -c "from utils.settings import settings; print(settings.base_url)"` | Prints correct MM test11 URL |
| MM smoke run | `pytest -m "model_management_smoke" --env test11` | All smoke tests pass |
| STP regression check | `pytest -m "smoke" applicationqe/tests/features/stp/ --collect-only` | 0 collection errors (settings.py refactor has no regression) |
| Pipeline YAML | `az pipelines create --yaml-path applicationqe/azure-pipelines/model-management.yml` or offline linter | Valid YAML, no schema errors |
| Path trigger check | Commit a change to `applicationqe/data/model-management/` | Only `model-management` pipeline triggers, not STP pipelines |

---

## 11. Rollback Considerations

| Scenario | Rollback Mechanism | Risk to `develop` |
|---|---|---|
| Migration causes import errors across all tests | `git reset --hard origin/develop` on local branch | None — `develop` untouched |
| `settings.py` refactor breaks STP-Journals | Revert `settings.py` to use hardcoded `stp/stp-journals` path | None — PR is not yet merged |
| MM pipeline triggers STP test runs | Revert `model-management.yml` path changes | None — pipeline YAML is branch-scoped until PR |
| `requirements.txt` changes break venv | `pip install -r requirements.txt` with previous version | None — rollback restores pinned versions |
| Source branch code cannot be adapted (architecture too different) | Leave MM placeholder dirs with `.gitkeep`, re-architect MM tests from scratch using STP-Journals as the template | None — placeholder dirs already in `develop` |

The source branch `origin/application/ModelManagement_SMI` is **never deleted or modified** — it
remains available on the remote as a full reference and fallback.

---

## 12. Pre-Migration Blockers (Critical)

These must be resolved **before any PR to `develop`** can be raised:

| # | Blocker | File | Fix |
|---|---|---|---|
| 1 | Pipeline path triggers use spaces (`Model Management`) instead of hyphens | `azure-pipelines/model-management.yml` | Change all path strings to `model-management`; add `applicationqe/` prefix |
| 2 | `settings.py` hardcoded to `stp/stp-journals` config path | `utils/settings.py` | Introduce `TEAM_NAME` env variable |
| 3 | No Model Management markers in `pytest.ini` | `pytest.ini` | Add MM-specific `@pytest.mark` entries |
| 4 | Pipeline uses `ubuntu-latest` pool, `team-stage.yml` expects `ubuntu2204-qa` | `azure-pipelines/model-management.yml` | Change pool configuration |
| 5 | `pages/model-management/` directory does not exist | `pages/` | Create with `__init__.py` and `locators/` sub-directory |

---

*Next step: Run `git fetch origin application/ModelManagement_SMI` and `git diff develop..origin/application/ModelManagement_SMI --name-only` to execute Phase 0 (inventory). Review this plan, confirm, then proceed with implementation.*
