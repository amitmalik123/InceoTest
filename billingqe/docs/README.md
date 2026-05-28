# Billing QE Automation Framework

> **Platform Revenue Dashboard — Strategist Group Model (SGM)**  
> End-to-end UI automation suite built with Python · Playwright · pytest-bdd

---

## Overview

The **Billing QE Automation Framework** is a production-grade, BDD-first test automation framework designed to validate the **Billing Platform Revenue Dashboard**, specifically the **Strategist Group Model (SGM)** module. It covers the complete lifecycle of Model Families and Models — from creation and approval through editing and search.

The framework is built on a clean three-layer architecture:

| Layer | Technology |
|-------|-----------|
| Browser Automation | Playwright (sync API) |
| BDD Test Orchestration | pytest-bdd + Gherkin `.feature` files |
| Test Runner / Reporting | pytest + Allure + HTML reports |

---

## Module Coverage

| Feature | Scenarios |
|---------|-----------|
| Create Family | Create Model Family with valid data |
| Approve / Reject Family | Approve and Reject Family workflows |
| Edit Family | Edit Family fields with valid data |
| Search Family | Matrix search with ALL / Pending / Rejected filters |
| Approve / Reject Model | Approve and Reject Model workflows |
| Edit Model | Edit Model entry to update Family Name |
| Search Model | Search with status-action validation and no-record handling |

---

## Repository Structure

```
billingqe/
├── azure-pipelines/          # CI/CD pipeline definitions
│   ├── prd_sgm.yml           # Billing team pipeline
│   └── templates/            # Shared stage templates
├── config/
│   └── billing/
│       └── platformrevenuedashboard/
│           └── strategistgroupmodel/
│               ├── env.qa.yaml          # Base QA environment config
│               └── env.qa.local.yaml    # Local overrides (git-ignored)
├── data/
│   └── billing/
│       └── platformrevenuedashboard/
│           └── strategistgroupmodel/
│               ├── create_family_data.csv
│               ├── approve_reject_family_data.csv
│               ├── edit_family_data.csv
│               ├── search_family_data.csv
│               ├── approve_reject_model_data.csv
│               ├── edit_model_data.csv
│               └── search_model_data.csv
├── docs/                     # This documentation folder
├── fixtures/                 # Modular pytest fixtures
│   ├── assertion_fixtures.py
│   ├── auth_fixtures.py
│   ├── browser_fixtures.py
│   ├── data_fixtures.py
│   ├── db_fixtures.py
│   ├── hooks_fixtures.py
│   └── page_fixtures.py
├── pages/
│   └── billing/
│       └── platformrevenuedashboard/
│           ├── common/
│           │   ├── base_page.py
│           │   ├── login_page.py
│           │   └── navigation_page.py
│           └── strategistgroupmodel/
│               ├── approve_reject_family_page.py
│               ├── approve_reject_model_page.py
│               ├── create_family_page.py
│               ├── edit_family_page.py
│               ├── edit_model_page.py
│               ├── login_page.py
│               ├── navigation_page.py
│               └── search_model_page.py
├── tests/
│   ├── conftest.py           # Single consolidated conftest
│   ├── features/
│   │   └── billing/
│   │       └── platformrevenuedashboard/
│   │           └── strategistgroupmodel/
│   │               ├── create_family.feature
│   │               ├── approve_reject_family.feature
│   │               ├── edit_family.feature
│   │               ├── search_family.feature
│   │               ├── approve_reject_model.feature
│   │               ├── edit_model.feature
│   │               └── search_model.feature
│   ├── runners/
│   │   └── billing/
│   │       └── platformrevenuedashboard/
│   │           └── strategistgroupmodel/
│   │               ├── test_create_family_bdd_runner.py
│   │               ├── test_approve_reject_family_bdd_runner.py
│   │               ├── test_edit_family_bdd_runner.py
│   │               ├── test_search_family_bdd_runner.py
│   │               ├── test_approve_reject_model_bdd_runner.py
│   │               ├── test_edit_model_bdd_runner.py
│   │               └── test_search_model_bdd_runner.py
│   └── steps/
│       └── billing/
│           └── platformrevenuedashboard/
│               ├── revenue_dashboard_common_steps.py
│               └── strategistgroupmodel/
│                   ├── common_steps.py
│                   ├── create_family_steps.py
│                   ├── approve_reject_family_steps.py
│                   ├── edit_family_steps.py
│                   ├── search_family_steps.py
│                   ├── approve_reject_model_steps.py
│                   ├── edit_model_steps.py
│                   └── search_model_steps.py
├── pytest.ini
└── requirements.txt
```

---

## Quick Start

```bash
# 1. Clone and enter the repo
cd billingqe

# 2. Activate virtual environment
.venv\Scripts\Activate.ps1          # Windows
source .venv/bin/activate           # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 4. Copy and configure credentials
cp config/billing/platformrevenuedashboard/strategistgroupmodel/env.qa.yaml \
   config/billing/platformrevenuedashboard/strategistgroupmodel/env.qa.local.yaml
# Edit env.qa.local.yaml to add username/password

# 5. Run a specific suite
pytest tests/runners/billing/platformrevenuedashboard/strategistgroupmodel/test_search_family_bdd_runner.py -v

# 6. Run the full SGM suite
pytest tests/runners/ -m "regression" -v
```

---

## Key Commands

| Command | Purpose |
|---------|---------|
| `pytest tests/runners/ -q` | Run all SGM tests |
| `pytest tests/runners/ -m "family"` | Run all Family workflow tests (ordered) |
| `pytest tests/runners/ -m "create"` | Run only Create Family tests |
| `pytest tests/runners/ -m "search"` | Run only Search tests |
| `pytest tests/runners/ --collect-only` | Dry-run: list all collected tests |
| `pytest tests/runners/ --headed` | Run in headed browser mode |

---

## Documentation Index

| File | Description |
|------|-------------|
| [SETUP_SUMMARY.md](SETUP_SUMMARY.md) | Environment setup and installation guide |
| [FRAMEWORK_DOCUMENTATION.md](FRAMEWORK_DOCUMENTATION.md) | Architecture deep-dive |
| [BDD_GUIDE.md](BDD_GUIDE.md) | How to write and run BDD scenarios |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Running tests, markers, and strategies |
| [ENVIRONMENT_GUIDE.md](ENVIRONMENT_GUIDE.md) | Config, secrets, and environment setup |
| [AZURE_PIPELINE_GUIDE.md](AZURE_PIPELINE_GUIDE.md) | CI/CD pipeline setup and triggers |
| [TAG_USAGE_GUIDE.md](TAG_USAGE_GUIDE.md) | Markers, tags, and test selection |
| [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md) | Troubleshooting and debugging tips |
| [CODE_QUALITY_REPORT.md](CODE_QUALITY_REPORT.md) | Code quality standards and metrics |

---

## Reporting

After each test run, reports are generated in:

```
reports/billing/platformrevenuedashboard/strategistgroupmodel/
├── allure-results/     # Raw Allure data
├── pytest_report.html  # Self-contained HTML report
└── pytest.log          # Detailed debug log
```

To open the Allure report:
```bash
allure serve reports/billing/platformrevenuedashboard/strategistgroupmodel/allure-results
```

---

*Last updated: May 2026*
