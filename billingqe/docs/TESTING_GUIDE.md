# Testing Guide

> **Running, Filtering, and Validating Billing SGM Tests**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Running Tests](#running-tests)
3. [Test Selection by Marker](#test-selection-by-marker)
4. [Data-Driven Testing](#data-driven-testing)
5. [Headed vs Headless Mode](#headed-vs-headless-mode)
6. [Parallel Execution](#parallel-execution)
7. [Test Ordering](#test-ordering)
8. [Reports and Logs](#reports-and-logs)
9. [CI vs Local Execution](#ci-vs-local-execution)

---

## Prerequisites

Before running any test:

```bash
# 1. Virtual environment activated
.venv\Scripts\Activate.ps1

# 2. Dependencies installed
pip install -r requirements.txt
playwright install chromium

# 3. Credentials configured (see ENVIRONMENT_GUIDE.md)
# env.qa.local.yaml must exist with valid username/password
```

---

## Running Tests

### All SGM tests
```bash
pytest tests/runners/ -v
```

### A specific runner file
```bash
pytest tests/runners/billing/platformrevenuedashboard/strategistgroupmodel/test_search_family_bdd_runner.py -v
```

### All tests with a specific marker
```bash
pytest tests/runners/ -m "family" -v
pytest tests/runners/ -m "regression" -v
pytest tests/runners/ -m "create" -v
```

### Dry run — list tests without executing
```bash
pytest tests/runners/ --collect-only -q
```

### Run with short output
```bash
pytest tests/runners/ -q
```

---

## Test Selection by Marker

All markers are registered in `pytest.ini` under `markers =`. Use `-m` with standard boolean expressions:

| Command | Tests Selected |
|---------|---------------|
| `pytest -m family` | All Family-related tests (create, approve, edit, search) |
| `pytest -m "family and create"` | Create Family only |
| `pytest -m "family and search"` | Search Family only |
| `pytest -m "family and edit"` | Edit Family only |
| `pytest -m "family and approve_reject"` | Approve/Reject Family only |
| `pytest -m model` | All Model-related tests |
| `pytest -m "model and search_model"` | Search Model only |
| `pytest -m "model and edit_model"` | Edit Model only |
| `pytest -m regression` | All tests tagged regression |
| `pytest -m "not regression"` | All non-regression tests |

See [TAG_USAGE_GUIDE.md](TAG_USAGE_GUIDE.md) for the complete marker reference.

---

## Data-Driven Testing

Each test scenario is parametrized by a CSV file. One CSV row = one test case.

```
data/billing/platformrevenuedashboard/strategistgroupmodel/
├── create_family_data.csv          → test_create_family_bdd_runner.py
├── approve_reject_family_data.csv  → test_approve_reject_family_bdd_runner.py
├── edit_family_data.csv            → test_edit_family_bdd_runner.py
├── search_family_data.csv          → test_search_family_bdd_runner.py
├── approve_reject_model_data.csv   → test_approve_reject_model_bdd_runner.py
├── edit_model_data.csv             → test_edit_model_bdd_runner.py
└── search_model_data.csv           → test_search_model_bdd_runner.py
```

**CSV format conventions:**

| Convention | Rule |
|-----------|------|
| Header row | Required — column names map to form field names |
| `case_id` column | Used as test ID in pytest output |
| Blank cell | Skip that field — no error raised |
| Boolean fields | Accept `Y`/`N`, `true`/`false`, `1`/`0` |
| Multiple rows | Each generates an independent parametrized test node |

**After editing a CSV**, restart pytest — data is loaded at import time and cached in `_ROWS`.

---

## Headed vs Headless Mode

| Mode | Command | Use Case |
|------|---------|----------|
| Headless (default) | `pytest tests/runners/` | CI runs, fast local runs |
| Headed | `pytest tests/runners/ --headed` | Local debugging, watching the browser |
| Force headless | `pytest tests/runners/ --headless` | Explicit override |

When running **headed**, `slow_mo=200` is applied automatically to make actions visible.

In CI environments (`CI=true`), the framework defaults to headless regardless of flags.

---

## Parallel Execution

The framework supports parallel execution via `pytest-xdist`:

```bash
# Run with 4 parallel workers
pytest tests/runners/ -n 4

# Auto-detect CPU count
pytest tests/runners/ -n auto
```

> ⚠️ **Note:** Family workflow tests have a prescribed order (create → approve → edit → search). Run the full family suite **without parallelism** to preserve that ordering, or run individual family tests independently.

---

## Test Ordering

Family-tagged tests are automatically reordered by `pytest_collection_modifyitems` in `tests/conftest.py`:

```
1. test_create_family_bdd_runner.py      (priority 0)
2. test_approve_reject_family_bdd_runner.py (priority 1)
3. test_edit_family_bdd_runner.py        (priority 2)
4. test_search_family_bdd_runner.py      (priority 3)
```

This ordering is enforced any time you run `pytest -m "family"`, ensuring the workflow makes sense end-to-end.

Non-family tests are not reordered — they run in discovery order.

---

## Reports and Logs

All reports are generated automatically at `reports/billing/platformrevenuedashboard/strategistgroupmodel/`:

### HTML Report
Self-contained report with test results, durations, and pass/fail breakdown:
```
reports/.../pytest_report.html
```
Open in any browser — no server needed.

### Allure Report
Interactive report with step breakdown, screenshots, and trends:
```bash
# View current run
allure serve reports/billing/platformrevenuedashboard/strategistgroupmodel/allure-results

# Generate static HTML
allure generate reports/.../allure-results -o reports/.../allure-html --clean
```

### Log File
Full DEBUG-level log of every test run:
```
reports/.../pytest.log
```

### Failure Screenshots
Captured automatically on any step failure:
```
reports/.../screenshots/FAIL_<scenario>_<step>_<timestamp>.png
```

---

## CI vs Local Execution

| Aspect | Local | CI (Azure Pipelines) |
|--------|-------|----------------------|
| Browser mode | Headed (default) | Headless (auto-detected via `CI=true`) |
| Credentials | `env.qa.local.yaml` | Environment variables (`BILLING_USERNAME`, `BILLING_PASSWORD`) |
| Report output | Local `reports/` folder | Published as pipeline artifacts |
| Trigger | Manual | Scheduled (8:30 AM UTC daily) or manual |
| Pool | Developer machine | `ubuntu2204-qa` agent pool |

For CI credential setup, see [ENVIRONMENT_GUIDE.md](ENVIRONMENT_GUIDE.md).

---

*Last updated: May 2026*
