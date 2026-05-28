# BDD Guide

> **Behavior-Driven Development for Billing SGM Automation**

---

## Table of Contents

1. [What is BDD in this Framework?](#what-is-bdd)
2. [Gherkin Structure](#gherkin-structure)
3. [Feature Files — Where and How](#feature-files)
4. [Step Definitions — Writing & Matching](#step-definitions)
5. [Runner Files — Binding Scenarios to pytest](#runner-files)
6. [Adding a New Scenario](#adding-a-new-scenario)
7. [Adding a New Feature](#adding-a-new-feature)
8. [Step Re-use and Shared Steps](#step-re-use)
9. [Common Pitfalls](#common-pitfalls)

---

## What is BDD in this Framework?

This framework uses **pytest-bdd** to bridge Gherkin `.feature` files with Python step definitions. The flow is:

```
CSV data row
    ↓
pytest parametrize (runner file)
    ↓
@scenario(feature_path, scenario_title)
    ↓
Gherkin scenario steps
    ↓
@given/@when/@then functions (step files)
    ↓
Page Object methods (pages/)
    ↓
Playwright browser actions
```

---

## Gherkin Structure

All feature files follow this structure:

```gherkin
Feature: <Module Name>
  As a <role>
  I want to <goal>
  So that <business value>

  Background:
    Given the user is logged into the application
    And the user verifies login is successful

  @<marker1> @<marker2>
  Scenario: <Scenario Title>
    When  the user navigates to Strategist Group Model
    And   ...
    Then  ...
    And   the user logs out
```

**Background** steps run before every scenario in that feature — used here for login.

---

## Feature Files — Where and How

All Billing SGM `.feature` files live in:

```
tests/features/billing/platformrevenuedashboard/strategistgroupmodel/
├── create_family.feature
├── approve_reject_family.feature
├── edit_family.feature
├── search_family.feature
├── approve_reject_model.feature
├── edit_model.feature
└── search_model.feature
```

**Rules:**
- Feature files contain **no Python** — pure Gherkin only
- One `.feature` file per functional area
- Scenario titles must exactly match the string in the corresponding runner's `@scenario(...)` call
- Markers are declared in `.feature` files using `@marker_name` above the Scenario

---

## Step Definitions — Writing & Matching

Step definitions are Python functions decorated with `@given`, `@when`, or `@then`. They live in:

```
tests/steps/billing/platformrevenuedashboard/
├── revenue_dashboard_common_steps.py      # Login, navigate, submit, logout
└── strategistgroupmodel/
    ├── common_steps.py                    # SGM-level re-exports
    ├── create_family_steps.py
    ├── approve_reject_family_steps.py
    ├── edit_family_steps.py
    ├── search_family_steps.py
    ├── approve_reject_model_steps.py
    ├── edit_model_steps.py
    └── search_model_steps.py
```

### Step Matching Rules

pytest-bdd matches the Gherkin text **exactly** to a decorated function:

```python
# In search_family_steps.py
@when("the user executes all search family validations from test data")
def execute_search_family_validations(search_family_page, search_family_data_row):
    search_family_page.execute_search_validations(search_family_data_row)
```

```gherkin
# In search_family.feature
When the user executes all search family validations from test data
```

> ⚠️ **Exact match required** — whitespace, capitalisation, and punctuation must match the Gherkin step string precisely.

### Parametrized Steps (Tables)

For data-table steps, the step function receives a `datatable` argument:

```python
@when("the user fills in the family form with the following data:")
def fill_family_form(create_family_page, create_family_data_row, datatable):
    create_family_page.create_family(create_family_data_row)
```

---

## Runner Files — Binding Scenarios to pytest

Runner files live in `tests/runners/` and glue everything together:

```python
# tests/runners/billing/platformrevenuedashboard/strategistgroupmodel/test_create_family_bdd_runner.py

REPO_ROOT = Path(__file__).resolve().parents[5]
FEATURE_DIR = REPO_ROOT / "tests" / "features" / "billing" / "platformrevenuedashboard" / "strategistgroupmodel"

_ROWS = _load_rows()   # CSV loaded at import time

@pytest.mark.create
@pytest.mark.family
@pytest.mark.regression
@pytest.mark.parametrize("create_family_data_row", _ROWS, indirect=True)
@scenario(str(FEATURE_DIR / "create_family.feature"), "Create Model Family with valid data")
def test_create_model_family_with_valid_data(create_family_data_row):
    pass
```

**Key points:**
- `REPO_ROOT` is calculated using `parents[5]` — always resolves to `billingqe/`
- `FEATURE_DIR` is an absolute path — feature files are not co-located with runners
- Each runner has **one test function per feature scenario**
- The function body is always `pass` — all logic is in steps and page objects

---

## Adding a New Scenario

1. **Add the Gherkin scenario** to the relevant `.feature` file with correct markers
2. **Implement any missing steps** in the relevant `*_steps.py` file
3. **Add a new test function** in the corresponding runner file:
   ```python
   @pytest.mark.my_marker
   @pytest.mark.regression
   @pytest.mark.parametrize("my_data_row", _ROWS, indirect=True)
   @scenario(str(FEATURE_DIR / "my_feature.feature"), "Exact Scenario Title")
   def test_my_scenario(my_data_row):
       pass
   ```
4. **Add test data rows** to the CSV file
5. **Run collection** to verify: `pytest tests/runners/ --collect-only`

---

## Adding a New Feature

1. Create a new `.feature` file in `tests/features/billing/platformrevenuedashboard/strategistgroupmodel/`
2. Create a new `*_steps.py` in `tests/steps/billing/platformrevenuedashboard/strategistgroupmodel/`
3. Create a new page object in `pages/billing/platformrevenuedashboard/strategistgroupmodel/`
4. Create a new `test_*_bdd_runner.py` in `tests/runners/billing/platformrevenuedashboard/strategistgroupmodel/`
5. Add a CSV data file in `data/billing/platformrevenuedashboard/strategistgroupmodel/`
6. Import the step file and add the page-object fixture in `tests/conftest.py`
7. Register any new markers in `pytest.ini`

---

## Step Re-use and Shared Steps

Shared steps (login, navigation, submit, logout) are defined **once** in `revenue_dashboard_common_steps.py` and available to all SGM tests through the root conftest.py's `import *`.

| Step | Defined In |
|------|------------|
| `Given the user is logged into the application` | `revenue_dashboard_common_steps.py` |
| `When the user navigates to Strategist Group Model` | `revenue_dashboard_common_steps.py` |
| `When the user submits the form` | `revenue_dashboard_common_steps.py` |
| `Then the user logs out` | `revenue_dashboard_common_steps.py` |

Never redefine a shared step in a feature-specific step file — pytest-bdd will raise a duplicate step error.

---

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `StepDefinitionNotFoundError` | Step text mismatch | Ensure exact character match with Gherkin |
| `FileNotFoundError` on feature | Wrong `FEATURE_DIR` path | Check `parents[N]` depth in runner |
| Stale test data | CSV cached at import | Restart pytest after CSV changes |
| `PluginValidationError` for hook | Wrong hook argument name | Hook args must match pytest-bdd hookspec exactly |
| Cross-repo import shadowing | `applicationqe` on `sys.path` | Handled automatically in `tests/conftest.py` |
| `DuplicateFixtureError` | Same fixture defined twice | Remove duplicate from conftest or fixture module |

---

*Last updated: May 2026*
