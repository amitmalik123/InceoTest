# Tag / Marker Usage Guide

Pytest markers are how we slice the **salesforceqe** suite into runnable
profiles (smoke, regression, area-specific, etc.). pytest-bdd tags in
`.feature` files are converted into pytest markers automatically.

## Where markers are declared

Every marker the suite uses must be registered in [pytest.ini](../pytest.ini)
under the `markers =` section. Pytest fails the run on an unregistered marker
when `--strict-markers` is enabled.

## Two ways to tag

### 1. In `.feature` files (BDD tags)

```gherkin
@smoke
Feature: Lead Conversion - Validation rules
    ...

    @critical @lead_conversion
    Scenario: Lead Conversion validation for Corporate Referral
        ...
```

Tags apply to the Feature **and** every Scenario beneath it, plus any extra
tags on the Scenario itself.

### 2. In Python tests / step modules

```python
import pytest

@pytest.mark.smoke
def test_something():
    ...
```

For BDD modules this is rarely needed — tag at the `.feature` level.

## Recommended core markers

The most useful markers for day-to-day work:

| Marker | Use for |
|---|---|
| `smoke` | Fast, must-pass set that runs on every commit |
| `regression` | Full suite — runs nightly / on release branches |
| `critical` | Highest-priority business flows |
| `high`, `medium`, `low` | Severity / priority tiers |
| `lead_conversion`, `validation`, `negative` | Area / behavior slices |
| `e2e`, `end_to_end` | True end-to-end scenarios |
| `performance`, `load_test` | Non-functional |
| `debug`, `quick_test` | Local / temporary filters (don't ship in CI) |

See [pytest.ini](../pytest.ini) for the full list of currently registered
markers.

## Filtering at run time

```powershell
# One marker
pytest -m smoke

# Boolean expressions
pytest -m "regression and not negative"
pytest -m "smoke or critical"

# Combine with name expression
pytest -m regression -k "conversion"
```

## Adding a new marker

1. Add a line under `markers =` in [pytest.ini](../pytest.ini):
   ```ini
   markers =
       my_new_marker: Short description
   ```
2. Apply it in your `.feature` (`@my_new_marker`) or Python test
   (`@pytest.mark.my_new_marker`).
3. If CI should run it, add a value to the `marker` parameter list in
   [azure-pipelines/salesforce.yml](../azure-pipelines/salesforce.yml).

## Guidelines

- Tag **every** scenario with at least one priority marker
  (`smoke` / `regression`) and at least one area marker.
- Keep marker names short and lowercase with underscores.
- Don't introduce a new marker for a one-off filter — use `-k` instead.
- Remove markers that no longer match any scenario to keep `pytest.ini` honest.
