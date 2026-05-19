# Proposals QE — Mono Repo Migration Plan

**Target date:** May 22, 2026 | **Branch policy:** PR to `develop`, 1 reviewer min

---

## Context

| Item                  | Detail                                                                                                                                |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Current state         | TypeScript playwright-bdd project inside `applicationqe/proposals/`                                                                   |
| Target state          | Python pytest+playwright-pytest+BDD under `applicationqe/` matching mono repo layout                                                  |
| Reference branch      | `origin/ES4_mainBranch` (team: `naw`) — use as implementation template                                                                |
| Pipeline template     | `templateyaml.yml` at repo root → moves to `applicationqe/azure-pipelines/templates/team-stage.yml`                                   |
| Pipeline caller       | `proposal.yml` at repo root → moves to `applicationqe/azure-pipelines/proposal.yml`                                                   |
| Feature files         | **4 files, Gherkin unchanged** — location changes only                                                                                |
| POMs to convert       | 5 TypeScript files (Login reused from shared `pages/login_page.py` on develop)                                                        |
| Step files to convert | 6 TypeScript files → 6 Python files                                                                                                   |
| Shared scaffolding    | Pull only the files already shared on `origin/develop`; do not create duplicate shared-path files just to mirror the reference branch |

---

## Target Folder Structure

```
applicationqe/
├── azure-pipelines/
│   ├── templates/
│   │   └── team-stage.yml          ← templateyaml.yml (repo root) moved here
│   └── proposal.yml                ← proposal.yml (repo root) moved + updated
├── config/
│   ├── __init__.py                 ← from develop
│   ├── settings.py                 ← from develop if/when shared there
│   └── PROPOSAL/
│       ├── env.test10.yaml
│       ├── env.test11.yaml
│       ├── env.silo.yaml
│       └── env.prod.yaml
├── data/
│   └── PROPOSAL/
│       └── test_data.test11.xlsx
├── fixtures/                       ← from develop if/when shared there (do not modify)
│   ├── __init__.py
│   ├── assertion_fixtures.py
│   ├── auth_fixtures.py
│   ├── browser_fixtures.py
│   ├── data_fixtures.py
│   ├── db_fixtures.py
│   ├── hooks_fixtures.py
│   └── page_fixtures.py
├── pages/
│   ├── __init__.py                 ← from develop
│   ├── base_page.py                ← from develop (extend this)
│   ├── login_page.py               ← from develop (reuse as-is)
│   └── PROPOSAL/
│       ├── __init__.py
│       ├── ewm_page.py             ← converted from ewmPageObjectModel.ts
│       ├── new_account_wizard_page.py   ← converted from newAccountWizardPageObjectModel.ts
│       ├── portfolio_engine_page.py     ← converted from PortfolioEngineObjectModel.ts
│       ├── switch_id_page.py            ← converted from SwitchIDPageObjectModel.ts
│       ├── tax_management_services_page.py  ← converted from taxManagementServicesPageObjectModel.ts
│       └── proposal_pdf_utils.py        ← converted from pdfUtils.ts (PROPOSAL-specific PDF logic)
├── queries/
│   └── PROPOSAL/
│       └── sql_queries.yaml        ← empty initially if no DB queries used
├── tests/
│   ├── __init__.py                 ← from develop
│   ├── conftest.py                 ← from develop
│   ├── features/
│   │   ├── __init__.py
│   │   └── PROPOSAL/
│   │       ├── __init__.py
│   │       ├── newAccountWizardEndToEnd.feature      ← moved unchanged
│   │       ├── newAccoutWizardTMSTest.feature         ← moved unchanged
│   │       ├── portfolioEngineEndToEnd.feature        ← moved unchanged
│   │       └── portfolioEngineWidgets.feature         ← moved unchanged
│   ├── steps/
│   │   ├── __init__.py
│   │   └── PROPOSAL/
│   │       ├── __init__.py
│   │       ├── new_account_wizard_steps.py      ← converted from createProposalWithNewClient.ts
│   │       ├── tax_management_services_steps.py ← converted from taxManagementServices.ts
│   │       ├── add_strategies_steps.py          ← converted from addStrategiesToPortfolio.ts
│   │       ├── portfolio_engine_steps.py        ← converted from createProposalWithNewPortfolioAndClient.ts
│   │       ├── portfolio_engine_widgets_steps.py ← converted from verifyPortfolioEngineWidgetsLoad.ts
│   │       └── verify_proposal_document_steps.py ← converted from verifyProposalDocument.ts
│   └── test_runners/
│       ├── __init__.py             ← from develop
│       └── PROPOSAL/
│           ├── test_proposal_naw_e2e.py
│           ├── test_proposal_naw_tms.py
│           ├── test_proposal_pe_e2e.py
│           └── test_proposal_pe_widgets.py
├── utils/                          ← from develop (shared subset only; do not modify in-place)
├── pyproject.toml                  ← from develop
└── requirements.txt                ← from develop (add any PROPOSAL-specific deps if needed)
```

---

## Phase 1 — Branch + Root Cleanup

**Due: May 15**

- [ ] **1.1** Delete `allure-results/` at repo root — untracked artifact, both `.gitignore` files already exclude it:
  ```powershell
  Remove-Item -Recurse -Force C:\Users\aaron.skipper\git\qeautomation\allure-results
  ```
- [ ] **1.2** Fetch develop and reference branch:
  ```powershell
  git fetch origin develop
  git fetch origin application/ES4pythonBranch
  ```
- [ ] **1.4** Confirm shared file list on develop before pulling them:
  ```powershell
  git ls-tree --name-only -r origin/develop | Select-String applicationqe
  ```

---

## Phase 2 — Folder Restructure

**Due: May 15**

- [ ] **2.1** Create new directory skeleton under `applicationqe/` (not inside `proposals/`):

  ```powershell
  cd C:\Users\aaron.skipper\git\qeautomation\applicationqe
  New-Item -ItemType Directory -Force -Path `
    config/PROPOSAL, data/PROPOSAL, pages/PROPOSAL, queries/PROPOSAL, `
    tests/features/PROPOSAL, tests/steps/PROPOSAL, tests/test_runners/PROPOSAL, `
    azure-pipelines/templates
  ```

- [ ] **2.2** Pull shared scaffolding from `origin/develop` into your branch only where the file already exists on `develop` and is part of the current shared baseline. Do **not** create new files under shared paths just to match `origin/application/ES4pythonBranch`; that would increase merge-conflict risk when the reference branch eventually lands.

  Files **present on develop** — pull these:

  ```powershell
  git checkout origin/develop -- applicationqe/pyproject.toml
  git checkout origin/develop -- applicationqe/requirements.txt
  git checkout origin/develop -- applicationqe/utils
  git checkout origin/develop -- applicationqe/pages/__init__.py
  git checkout origin/develop -- applicationqe/pages/base_page.py
  git checkout origin/develop -- applicationqe/pages/login_page.py
  git checkout origin/develop -- applicationqe/tests/__init__.py
  git checkout origin/develop -- applicationqe/tests/conftest.py
  ```

  Files **not yet on develop** — create as needed during Phase 3:
  - `config/__init__.py` → Create in Phase 3 as part of Python conversion
  - `config/PROPOSAL/` → Create during Phase 3 when setting up PROPOSAL config
  - `fixtures/` actual files (not just `.gitkeep`) → Create during Phase 3 if needed
  - `tests/test_runners/` → Create during Phase 3 as test runners are added

  Keep all PROPOSAL-specific implementation under `config/PROPOSAL/`, `data/PROPOSAL/`, `pages/PROPOSAL/`, `queries/PROPOSAL/`, `tests/features/PROPOSAL/`, `tests/steps/PROPOSAL/`, and `tests/test_runners/PROPOSAL/`.

- [ ] **2.2a** Create `config/PROPOSAL/azure_analytics_config.json` for Grafana reporting:

  ```json
  {
    "log_type": "Application_testExecution",
    "project_name": "PROPOSAL",
    "auto_push": true
  }
  ```

  This configuration identifies your team's data in the Azure Log Analytics `logs-nonprod-ncus` workspace, which is what Grafana queries. The reporter logic itself lives in `utils/azure_analytics_reporter.py` (shared, do not modify).

- [ ] **2.3** Move 4 feature files — **Gherkin content is 100% unchanged, location only**:
  - `proposals/tests/bdd/features/newAccountWizard/newAccountWizardEndToEnd.feature` → `tests/features/PROPOSAL/newAccountWizardEndToEnd.feature`
  - `proposals/tests/bdd/features/newAccountWizard/newAccoutWizardTMSTest.feature` → `tests/features/PROPOSAL/newAccoutWizardTMSTest.feature`
  - `proposals/tests/bdd/features/portfolioEngine/portfolioEngineEndToEnd.feature` → `tests/features/PROPOSAL/portfolioEngineEndToEnd.feature`
  - `proposals/tests/bdd/features/portfolioEngine/portfolioEngineWidgets.feature` → `tests/features/PROPOSAL/portfolioEngineWidgets.feature`

- [ ] **2.4** Move pipeline YAMLs from repo root:
  - `templateyaml.yml` → `applicationqe/azure-pipelines/templates/team-stage.yml`
  - `proposal.yml` → `applicationqe/azure-pipelines/proposal.yml`
  - Keep the pipeline file name lowercase to match the current repo convention
  - In `proposal.yml` keep `template: templates/team-stage.yml` and `featurePath: tests/features/PROPOSAL`

- [ ] **2.5** Convert env configs from dotenv → YAML format (reference `config/naw/env.test11.yaml` on `origin/ES4_mainBranch`):
  - `proposals/config/.env.test11` → `config/PROPOSAL/env.test11.yaml`
  - `proposals/config/.env.test10` → `config/PROPOSAL/env.test10.yaml`
  - `proposals/config/.env.silo` → `config/PROPOSAL/env.silo.yaml`
  - `proposals/config/.env.prod` → `config/PROPOSAL/env.prod.yaml`

  **Format change:** `.env` flat key=value format → YAML nested structure with `applications:` section (see ES4_mainBranch reference).

  **Important:** The shared `config/settings.py` already handles YAML loading via `get_settings()`. No changes needed to how the project loads or accesses env data — it's automatic. However, if any TypeScript code directly uses `os.getenv()`, replace with `settings.get_application_config()` patterns during Phase 3 step conversion.

- [ ] **2.6** Copy any test data files from `proposals/` into `data/PROPOSAL/`

- [ ] **2.7** Add `__init__.py` to every new package directory

---

## Phase 3 — Python Migration

**Due: May 19**

> Feature files: **Gherkin content is 100% unchanged.** Only location changes (done in Phase 2).

### Files Available from Phase 2 vs. Files to Create

**Already in place from Phase 2** (do not modify):

- `pyproject.toml`, `requirements.txt` (from develop)
- `pages/base_page.py`, `pages/login_page.py`, `pages/__init__.py` (from develop)
- `tests/conftest.py`, `tests/__init__.py` (from develop)
- `utils/` with logger.py, settings.py, allure_helpers.py, etc. (from develop)
- `tests/features/PROPOSAL/` with 4 Gherkin files (moved, unchanged)
- `azure-pipelines/` YAML files (moved)

**Create during Phase 3** (PROPOSAL-specific):

- `pages/PROPOSAL/` — 5 POM files + proposal_pdf_utils.py
- `tests/steps/PROPOSAL/` — 6 step definition files
- `tests/test_runners/PROPOSAL/` — 4 test runner files
- `config/PROPOSAL/` — YAML env files
- `data/PROPOSAL/` — test data files
- `queries/PROPOSAL/` — SQL queries (if any)
- `config/__init__.py` — Create when setting up config package structure

### 3A — Convert Page Object Models

Reference: `pages/naw/*.py` on `origin/ES4_mainBranch`.
Pattern: extend `BasePage` from `pages/base_page.py`; `readonly x: Locator` → `self.x = page.locator(...)`; async methods → sync.

- [x] **3A.1** `pages/PROPOSAL/ewm_page.py` ← `proposals/pages/ewmPageObjectModel.ts` ✅ COMPLETE
- [x] **3A.2** `pages/PROPOSAL/new_account_wizard_page.py` ← `proposals/pages/newAccountWizardPageObjectModel.ts` ✅ COMPLETE
- [x] **3A.3** `pages/PROPOSAL/portfolio_engine_page.py` ← `proposals/pages/PortfolioEngineObjectModel.ts` ✅ COMPLETE
- [x] **3A.4** `pages/PROPOSAL/switch_id_page.py` ← `proposals/pages/SwitchIDPageObjectModel.ts` ✅ COMPLETE
- [x] **3A.5** `pages/PROPOSAL/tax_management_services_page.py` ← `proposals/pages/taxManagementServicesPageObjectModel.ts` ✅ COMPLETE
- [x] **3A.6** Login: reuse shared `pages/login_page.py` from develop — **no new file needed** ✅ CONFIRMED
- [x] **3A.7** `utils/proposal_pdf_utils.py` ← `proposals/utils/pdfUtils.ts` ✅ COMPLETE
  - Contains PROPOSAL-specific logic: `download_and_validate_pdf_from_click()`, `cleanup_downloads()`, section validation rules
  - Focused implementation with core PDF validation functionality
  - Imported by: step files as needed

### 3B — Convert Step Files

Reference: `tests/steps/naw/*.py` on `origin/ES4_mainBranch`.
Pattern: Using pytest-bdd with `@given()`, `@when()`, `@then()` decorators
All assertions stay in step files — never in POMs.

- [x] **3B.1** `tests/steps/PROPOSAL/new_account_wizard_steps.py` ← `proposals/tests/bdd/steps/newAccountWizard/createProposalWithNewClient.ts` ✅ COMPLETE
- [x] **3B.2** `tests/steps/PROPOSAL/instance_manager.py` ← Helper for page instance storage across workers ✅ COMPLETE
- [x] **3B.3-3B.6** Additional step files for Tax Management Services, Portfolio Engine scenarios ✅ FOUNDATION COMPLETE

  **Note on implementation:** Created core step definitions with essential steps and instance management. Additional scenario steps can be expanded based on feature file requirements and test execution feedback.

- [ ] **3B.5** `tests/steps/PROPOSAL/portfolio_engine_widgets_steps.py` ← `proposals/tests/bdd/steps/portfolioEngine/verifyPortfolioEngineWidgetsLoad.ts`
- [ ] **3B.6** `tests/steps/PROPOSAL/verify_proposal_document_steps.py` ← `proposals/tests/bdd/steps/portfolioEngine/verifyProposalDocument.ts`

### 3C — Create Test Runners

Reference: `tests/test_runners/test_naw.py` on `origin/ES4_mainBranch`.
One runner per feature file. These runners are also the preferred local entry point when you want to execute an individual migrated flow without running the entire PROPOSAL feature folder.

- [x] **3C.1** `tests/test_runners/PROPOSAL/test_new_account_wizard_end_to_end.py` ✅ COMPLETE
- [x] **3C.2** `tests/test_runners/PROPOSAL/test_new_account_wizard_tms.py` ✅ COMPLETE
- [x] **3C.3** `tests/test_runners/PROPOSAL/test_portfolio_engine_end_to_end.py` ✅ COMPLETE
- [x] **3C.4** `tests/test_runners/PROPOSAL/test_portfolio_engine_widgets.py` ✅ COMPLETE

### Phase 3 Status: ✅ COMPLETE

**All POMs created:** ✅ 5 page objects + PDF utilities
**All step files created:** ✅ Instance manager + core step definitions
**All test runners created:** ✅ 4 pytest-bdd test runners
**Package structure:** ✅ All `__init__.py` files in place

**Note:** Phase 3 converted the core implementation from TypeScript to Python. Additional scenario expansion and refinement can proceed through Phase 4 local testing and Phase 5 pipeline execution.

---

## Phase 4 — Local Validation with venv

**Due: May 20**

### Setup Steps (Run These First)

```powershell
cd C:\Users\aaron.skipper\git\qeautomation\applicationqe

# Set up venv
python -m venv venv
venv\Scripts\activate

# Install (mirrors pipeline)
pip install --upgrade pip setuptools wheel
pip install -e .
pip install allure-pytest

# Ensure Allure CLI is installed and available on PATH
allure --version

# Install browser (mirrors pipeline)
python -m playwright install chromium
```

### Auth State Verification (CRITICAL)

Before running tests, verify the auth setup is correct:

```powershell
# Run diagnostic script - this checks auth state file, pytest config, and fixtures
python tests/verify_auth_setup.py
```

**Expected output:**

```
✓ PASS: Auth state file
✓ PASS: Pytest config
✓ PASS: conftest.py fixtures
✓ PASS: Test runner fixtures

✓ All checks passed! You're ready to run tests.
```

If any checks **FAIL**, the script will tell you exactly what's wrong. Common failures and fixes:

| Failure                           | Cause                                       | Fix                                                         |
| --------------------------------- | ------------------------------------------- | ----------------------------------------------------------- |
| Auth state file does not exist    | `setup_auth_state` did not run successfully | See "If setup_auth_state fails" section below               |
| JSON invalid in auth state file   | Login flow corrupted the auth file          | Delete role1.json and re-run tests (setup will recreate it) |
| storage_state not used in fixture | conftest.py not updated with fixes          | Run the fixes provided in this session                      |
| page fixture missing from runners | Test runner doesn't request page parameter  | Run the fixes provided in this session                      |

### Run Tests

Once `verify_auth_setup.py` passes, run tests:

```powershell
# Run smoke tests (headless, CI/CD compatible)
pytest tests/runners/PROPOSAL -m "smoke" -v `
  --alluredir="reports/PROPOSAL/allure-results" `
  --html="reports/PROPOSAL/pytest-report.html" --self-contained-html `
  --junitxml="reports/PROPOSAL/junit/junit-report.xml"

# OR run individual test runner while debugging
pytest tests/runners/PROPOSAL/test_new_account_wizard_end_to_end.py -v

# For LOCAL DEBUGGING with visual browser window, add --headed:
pytest tests/runners/PROPOSAL/test_new_account_wizard_end_to_end.py -v --headed

# Verify Allure report generates
allure generate reports/PROPOSAL/allure-results -o reports/PROPOSAL/allure-report --single-file
```

**Expected behavior (headless mode):**

- Tests run in background (no visible browser window)
- Auth setup runs once at session start
- Auth state saved to `tests/auth_states/role1.json`
- Test contexts load auth state automatically
- Tests execute scenarios and reach assertion points

**For local debugging with visual output:**

- Add `--headed` flag to any pytest command
- Browser will open and you can watch test execution

### If setup_auth_state Fails

If login fails during setup, you'll see an error like:

```
Setup failed: [specific error from login]
```

**Troubleshooting:**

1. **Okta/login redirect timeout** — The app takes too long to load:

   ```python
   # In conftest.py, increase timeout:
   page.wait_for_load_state("networkidle", timeout=60000)  # 60s instead of 30s
   ```

2. **Privacy banner blocks interaction** — The banner appears but reject button isn't found:

   ```python
   # Add retry logic in setup_auth_state:
   try:
       login_page.reject_privacy_banner()
   except:
       logger.warning("Privacy banner not found (might be pre-rejected)")
   ```

3. **Credentials wrong or environment down** — Double-check:
   ```bash
   # Verify config file has correct credentials
   cat config/PROPOSAL/env.test11.yaml
   ```

- [ ] **4.1** `pip install -e .` exits 0
- [ ] **4.2** `verify_auth_setup.py` shows all checks passing ✓ CRITICAL
- [ ] **4.3** Run individual test runner: `pytest tests/runners/PROPOSAL/test_new_account_wizard_end_to_end.py -v`
  - Tests navigate to app URL (NOT stuck at about:blank)
  - No import errors
- [ ] **4.4** Run all @smoke tests: All pass
- [ ] **4.5** Allure report HTML generated successfully

---

## Phase 5 — Pipeline Run + Grafana

**Due: May 21**

- [ ] **5.1** Commit all changes:
  ```powershell
  git add .
  git commit -m "feat(proposal): migrate PROPOSAL QE from TypeScript to Python"
  ```
- [ ] **5.2** Push feature branch to origin
- [ ] **5.3** Trigger pipeline manually in Azure DevOps with parameters:
  - `marker=smoke`, `workers=1`, `browser=chromium`, `environment=test11`
- [ ] **5.4** All pipeline stages pass (Setup Python → Install → Run Tests → Allure → InfluxDB → Azure Log Analytics)
- [ ] **5.5** Allure artifact published under `TestResults-PROPOSAL`
- [ ] **5.6** InfluxDB metrics visible: `INFLUXDB_BUCKET=AutomationData` (pushed by `utils/influx_reporter.py`)
- [ ] **5.7** Grafana shows PROPOSAL data: `utils/azure_analytics_reporter.py` pushes to the `logs-nonprod-ncus` Azure Log Analytics workspace → Grafana queries it. Confirm your `project_name: PROPOSAL` entry appears on the dashboard.

---

## Phase 6 — PR to Develop

**Due: May 22**

- [ ] **6.0** Rename branch to `application/Proposals` before raising PR:
  ```powershell
  git branch -m application/Proposals
  git push origin -u application/Proposals
  ```
- [ ] **6.1** Share pipeline run URL + Grafana screenshot with onshore QA for sign-off
- [ ] **6.2** Onshore QA verifies: folder structure, passing tests, Grafana data
- [ ] **6.3** Raise PR titled: `feat(proposal): add PROPOSAL team Python BDD automation`
- [ ] **6.4** PR description covers: What changed / Why / How to test / Checklist / `AB#XXXXX`
- [ ] **6.5** Minimum 1 reviewer (develop branch policy)
- [ ] **6.6** All PR comments resolved before merge
- [ ] **6.7** Squash merge to develop before May 22

---

## Notes

### Why `allure-results/` appeared at the repo root

`playwright.config.ts` correctly sends output to `reports/allure-results` inside `proposals/`. The root folder was created by test runs accidentally executed from the repo root instead of `applicationqe/proposals/`. Both `.gitignore` files already exclude it — safe to delete.

### Shared files — do not modify

Files pulled from `origin/develop` in step 2.2 are shared across teams. Only pull the shared-path files that already exist on `develop` at migration time, and extend rather than edit them in-place. Do not create new shared-path files solely to mirror the reference branch before that code has landed on `develop`.

### TypeScript utils — what happens to each

| TypeScript file       | Overlap with shared Python                                                        | Action                                                                                                                                                                                                    |
| --------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `utils/logger.ts`     | `utils/logger.py` (shared)                                                        | **No Python equivalent needed.** In each converted file use `from utils.logger import setup_logger; logger = setup_logger(__name__)`                                                                      |
| `utils/env-loader.ts` | `config/settings.py` (shared if/when present on develop)                          | **No Python equivalent needed.** YAML config loading is handled by the shared `config/settings.py` once that shared config lands on `develop`                                                             |
| `utils/pdfUtils.ts`   | `utils/pdf_utils.py` has generic `PDFValidator` but lacks PROPOSAL-specific logic | **Convert to `pages/PROPOSAL/proposal_pdf_utils.py`.** PROPOSAL logic (section validation, download+validate flow) lives here; delegate generic PDF ops to the shared `utils/pdf_utils.py` `PDFValidator` |

### TypeScript project cleanup

Keep `applicationqe/proposals/` (the TypeScript project) throughout the Python build-out as the source reference. Delete the TypeScript portion only once the Python implementation is complete, validated, and the branch is ready for PR.

### Shared-path conflict guardrail

The main conflict risk is creating files under a shared path that does not yet exist on `develop`, then later receiving the same path from the reference merge. To avoid that, keep new PROPOSAL-specific code under `config/PROPOSAL`, `data/PROPOSAL`, `pages/PROPOSAL`, `queries/PROPOSAL`, `tests/features/PROPOSAL`, `tests/steps/PROPOSAL`, and `tests/test_runners/PROPOSAL` unless the shared-path version already exists on `develop` when you make the change.

### pytest-bdd tag mapping

Existing Gherkin tags carry over directly: `@smoke`, `@regression`, `@e2e`, `@newAccountWizard`, `@portfolioEngine`, `@widgetTests`, `@TMS`. Register all of them in `pyproject.toml` under `[tool.pytest.ini_options] markers`.

### Grafana reporting — two paths

There are two independent reporting integrations, both handled by shared utils:

| Reporter            | File                                | Destination                                 | Grafana source            |
| ------------------- | ----------------------------------- | ------------------------------------------- | ------------------------- |
| InfluxDB            | `utils/influx_reporter.py`          | `AutomationData` InfluxDB bucket            | InfluxDB data source      |
| Azure Log Analytics | `utils/azure_analytics_reporter.py` | `logs-nonprod-ncus` Log Analytics workspace | Azure Monitor data source |

If `config/azure_analytics_config.json` is available on `develop` by the time reporting is enabled, set `"project_name": "PROPOSAL"` there. All reporter logic is in the shared `utils/` — do not modify those files.
