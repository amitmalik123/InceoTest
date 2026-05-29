# Tag Usage Guide

> **pytest Markers Reference for Billing SGM Automation**

---

## Table of Contents

1. [What Are Markers?](#what-are-markers)
2. [Billing SGM Markers](#billing-sgm-markers)
3. [Using Markers in Feature Files](#using-markers-in-feature-files)
4. [Using Markers in Runner Files](#using-markers-in-runner-files)
5. [Filtering Tests by Marker](#filtering-tests-by-marker)
6. [Marker Combinations](#marker-combinations)
7. [Registering New Markers](#registering-new-markers)

---

## What Are Markers?

Markers are labels attached to pytest test functions (and Gherkin scenarios) that let you **select, group, and filter** tests without modifying code.

This framework uses `--strict-markers` (configured in `pytest.ini`), which means **every marker must be registered** in `pytest.ini` before use. Using an unregistered marker will cause a collection error.

---

## Billing SGM Markers

### Workflow Markers (run groups)

| Marker | Applies To | Description |
|--------|-----------|-------------|
| `family` | All Family tests | Entire Family workflow (create → approve → edit → search) |
| `model` | All Model tests | Entire Model workflow |
| `regression` | All tests | Full regression suite marker |

### Feature-Specific Markers

| Marker | Runner File | Feature |
|--------|------------|--------|
| `create` | `test_create_family_bdd_runner.py` | Create Model Family |
| `approve_reject` | `test_approve_reject_family_bdd_runner.py`, `test_approve_reject_model_bdd_runner.py` | Approve or Reject Family/Model |
| `edit` | `test_edit_family_bdd_runner.py`, `test_edit_model_bdd_runner.py` | Edit Family / Edit Model |
| `search` | `test_search_family_bdd_runner.py` | Search Family |
| `search_model` | `test_search_model_bdd_runner.py` | Search Model |
| `edit_model` | `test_edit_model_bdd_runner.py` | Edit Model |

### Marker ↔ Test Coverage Matrix

| Runner File | Markers Applied |
|------------|----------------|
| `test_create_family_bdd_runner.py` | `create`, `family`, `regression` |
| `test_approve_reject_family_bdd_runner.py` | `approve_reject`, `family`, `regression` |
| `test_edit_family_bdd_runner.py` | `edit`, `family`, `regression` |
| `test_search_family_bdd_runner.py` | `search`, `family`, `regression` |
| `test_approve_reject_model_bdd_runner.py` | `approve_reject`, `model`, `regression` |
| `test_edit_model_bdd_runner.py` | `edit_model`, `edit`, `regression` |
| `test_search_model_bdd_runner.py` | `search_model`, `search`, `regression` |

---

## Using Markers in Feature Files

Declare markers in the `.feature` file using `@` syntax above the Scenario:

```gherkin
Feature: Create Model Family

  @create @family @regression
  Scenario: Create Model Family with valid data
    Given ...
```

> ⚠️ Markers in `.feature` files must also exist on the corresponding runner function. Both must match for pytest-bdd to collect properly.

---

## Using Markers in Runner Files

Apply markers using `@pytest.mark.<name>` decorators on the test function:

```python
@pytest.mark.create
@pytest.mark.family
@pytest.mark.regression
@pytest.mark.parametrize("create_family_data_row", _ROWS, indirect=True)
@scenario(str(FEATURE_DIR / "create_family.feature"), "Create Model Family with valid data")
def test_create_model_family_with_valid_data(create_family_data_row):
    pass
```

---

## Filtering Tests by Marker

### Run a single functional group

```bash
# All Family tests (ordered: create → approve → edit → search)
pytest tests/runners/ -m "family" -v

# All Model tests
pytest tests/runners/ -m "model" -v

# Full regression suite
pytest tests/runners/ -m "regression" -v
```

### Run a single feature

```bash
pytest tests/runners/ -m "create" -v              # Create Family only
pytest tests/runners/ -m "approve_reject" -v      # Approve/Reject (Family + Model)
pytest tests/runners/ -m "search" -v              # Search Family + Search Model
pytest tests/runners/ -m "search_model" -v        # Search Model only
pytest tests/runners/ -m "edit_model" -v          # Edit Model only
```

### Boolean combinations

```bash
# Only Family + search tests
pytest tests/runners/ -m "family and search" -v

# Approve/Reject for Family only
pytest tests/runners/ -m "family and approve_reject" -v

# Exclude regression (hypothetical smoke subset)
pytest tests/runners/ -m "family and not regression" -v

# All search tests (Family + Model)
pytest tests/runners/ -m "search or search_model" -v
```

---

## Marker Combinations Quick Reference

| Goal | Command |
|------|--------|
| Full SGM regression | `pytest tests/runners/ -m regression` |
| Family workflow end-to-end | `pytest tests/runners/ -m family` |
| Only Create | `pytest tests/runners/ -m "family and create"` |
| Only Approve/Reject | `pytest tests/runners/ -m approve_reject` |
| Only Edit | `pytest tests/runners/ -m edit` |
| Only Search | `pytest tests/runners/ -m search` |
| Model workflow end-to-end | `pytest tests/runners/ -m model` |
| All Search tests | `pytest tests/runners/ -m "search or search_model"` |
| Everything except Edit | `pytest tests/runners/ -m "regression and not edit"` |

---

## Registering New Markers

1. Open `pytest.ini`
2. Add a new entry under `markers =`:
   ```ini
   markers =
       ...
       # ── BILLING SGM markers ───────
       my_new_marker: Description of the new marker
   ```
3. Apply `@pytest.mark.my_new_marker` to the relevant runner function
4. Add `@my_new_marker` to the relevant Gherkin scenario
5. Run `pytest tests/runners/ --collect-only` to verify no marker validation errors

---

*Last updated: May 2026*
