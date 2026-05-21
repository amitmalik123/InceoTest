# Debugging Guide

Tools and techniques for diagnosing failures in **salesforceqe**.

## 1. Run headed and slow

```powershell
pytest -k "Lead Conversion validation" --headed --slowmo 500
```

Add `--browser chromium --browser msedge` to reproduce browser-specific issues.

## 2. Playwright traces

Always record on failure:

```powershell
pytest -m smoke --tracing retain-on-failure
```

Open a trace:

```powershell
playwright show-trace test-results\<test>\trace.zip
```

The trace UI gives you the DOM snapshot, network log, console messages, and
the exact action timeline.

## 3. Videos & screenshots

```powershell
pytest -m smoke --video retain-on-failure --screenshot only-on-failure
```

Output lands in `test-results/<test-id>/`.

The [`utils/screenshot_helper.py`](../utils/screenshot_helper.py) module also
captures named screenshots from inside page objects and attaches them to
Allure via [`utils/allure_helpers.py`](../utils/allure_helpers.py).

## 4. Logs

[`utils/logger.py`](../utils/logger.py) emits structured logs. Bump verbosity
on the CLI:

```powershell
pytest -m smoke -o log_cli=true -o log_cli_level=DEBUG
```

## 5. Allure report

```powershell
pytest -m smoke --alluredir=reports\salesforce\allure-results
allure serve reports\salesforce\allure-results
```

Each scenario shows steps, attachments (screenshots, page HTML), the failure
trace, and environment metadata.

## 6. Interactive debugging

- **Playwright Inspector**: `PWDEBUG=1 pytest -k "<name>"` (pauses at every
  action, lets you step through and tweak selectors).
- **pdb**: insert `breakpoint()` in the failing step and run with `-s`:
  ```powershell
  pytest -k "<name>" -s
  ```
- **VS Code**: use the *Python: Debug Test* lens above any pytest function
  (works for `test_*_bdd.py` modules).

## 7. Common failure patterns

| Symptom | Likely cause | Fix |
|---|---|---|
| Timeout waiting for selector | Lightning re-renders changed the DOM | Replace generated id selectors with `getByRole` / `getByLabel` |
| Click intercepted by toast | Salesforce success toast still visible | `expect(toast).to_be_hidden()` before clicking next element |
| Stale element after navigation | Same page object re-used after URL change | Re-resolve the locator inside the action method |
| Login loops forever | MFA enabled on the test user | Use a non-MFA service user or saved `storage_state` |
| Random failures only in xdist | Test relies on data from another worker | Make data scenario-local; use `test_data` fixture |

## 8. CI failure triage

In Azure Pipelines, every run publishes:
- JUnit (`reports/junit.xml`) — test status and durations.
- Allure HTML — drilldown into each scenario.
- pytest-html (`report.html`) — quick overview.
- Playwright trace zips when `--tracing retain-on-failure` is enabled.

Start with the Allure trend, drill into the failing scenario, then open the
trace for the exact action that broke.
