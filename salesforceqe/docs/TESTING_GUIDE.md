# Testing Guide

How to run the **salesforceqe** test suite locally and interpret the output.

## Test types

| Type | Location | Entry point |
|---|---|---|
| BDD scenarios | `tests/features/salesforce/*.feature` | `tests/steps/salesforce/test_*_bdd.py` |

All tests are pytest-bdd scenarios. The step modules call `scenarios(...)` to
bind a `.feature` file to a step module.

## Running tests

From the `salesforceqe/` folder (with the venv activated):

```powershell
# Everything tagged @smoke
pytest -m smoke

# Everything tagged @regression
pytest -m regression

# A specific feature via its step module
pytest tests/steps/salesforce/test_lead_conversion_bdd.py

# A single scenario by name
pytest -k "Lead Conversion validation"
```

## Common pytest options

| Option | Effect |
|---|---|
| `-m <marker>` | Filter by marker (see [TAG_USAGE_GUIDE.md](TAG_USAGE_GUIDE.md)) |
| `-k "<expr>"` | Filter by name expression |
| `-n <N>` / `-n auto` | Run in parallel (pytest-xdist) |
| `--headed` | Show browser UI (pytest-playwright) |
| `--browser chromium\|msedge\|firefox\|webkit` | Pick browser |
| `--slowmo 250` | Slow each action down (ms) for debugging |
| `--tracing on` | Always record Playwright traces |
| `--video on` | Record video for every test |
| `--screenshot only-on-failure` | Capture screenshots on failures |
| `-x` | Stop on first failure |
| `--lf` | Re-run only the last failed tests |
| `-vv` | Verbose output |

## Parallel execution

```powershell
pytest -m regression -n auto
```

Notes:
- Most page-object fixtures are **session-scoped**, so each xdist worker gets
  its own browser session.
- Test data (`test_data` fixture) is randomized per session — each worker
  generates its own Lead names, so there are no cross-worker collisions.

## Cross-browser

```powershell
pytest -m smoke --browser chromium --browser msedge
```

`pytest-playwright` will run each test once per browser listed.

## Reports

| Report | Location |
|---|---|
| HTML (pytest-html) | `reports/salesforce/pytest-report.html` |
| JUnit XML | `reports/salesforce/junit/junit-report.xml` |
| Allure results | `reports/salesforce/allure-results` |
| Allure HTML | `reports/salesforce/allure-report/` (run `allure generate`) |
| Playwright traces | `test-results/.../trace.zip` |

Generate / serve Allure:

```powershell
allure serve reports\salesforce\allure-results
allure generate reports\salesforce\allure-results -o reports\salesforce\allure-report --clean
```

## Selecting an environment

The framework reads the target sandbox from `credentials.json` plus the
`TEST_ENV` environment variable used by the pipeline.

```powershell
$env:TEST_ENV = "monarchqa"
pytest -m smoke
```

See [ENVIRONMENT_GUIDE.md](ENVIRONMENT_GUIDE.md) for the full list.
