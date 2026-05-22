# BDD Guide (pytest-bdd)

How to author Gherkin features and step definitions in **salesforceqe**.

## Layout

```text
tests/
├── features/salesforce/
│   ├── Lead_Conversion.feature
│   └── Lead_Page_Validation.feature
└── steps/salesforce/
    ├── common_steps.py
    ├── test_lead_conversion_bdd.py
    └── test_lead_page_validation_bdd.py
```

Each `test_*_bdd.py` module binds one `.feature` file via `scenarios(...)`:

```python
from pytest_bdd import scenarios

scenarios("../../features/salesforce/Lead_Conversion.feature")
```

`common_steps.py` collects Given/When/Then implementations used across multiple
feature files (login, app switch, navigate to Leads tab, etc.).

## Feature file conventions

- **One Feature per file**, named after the user-visible behavior.
- Tag the Feature **and** each Scenario with at least one
  [marker](TAG_USAGE_GUIDE.md), e.g. `@smoke`, `@regression`,
  `@lead_conversion`.
- Use a `Background:` for setup steps that apply to every scenario.
- Keep step text business-readable — push UI details into page objects.

Example (from `Lead_Conversion.feature`):

```gherkin
@smoke
Feature: Lead Conversion - Validation rules
    As a Salesforce user
    I want to convert a Lead in the Monarch Console app
    So that I can verify the Lead Conversion validation rules

    Background:
        Given I am logged in to Salesforce as the configured user
        And I have switched to the "Monarch Console" app
        And I have opened the Leads tab

    Scenario: Lead Conversion validation for Corporate Referral
        Given I have created a Lead with valid data
        When I attempt to convert the Lead with missing Broker Dealer Account and CRD Advisor
        Then a Lead Conversion validation error should be displayed
```

## Step definitions

- Live in `tests/steps/salesforce/` next to the binding `test_*_bdd.py`.
- Use `@given`, `@when`, `@then` from `pytest_bdd`.
- **Never** drive the browser directly inside a step — call methods on the
  page-object fixtures (`login_page`, `home_page`, `lead_happy_path`, …).
- For data passed between steps, use the `session_state` fixture rather than
  module-level globals.

```python
from pytest_bdd import given, when, then

@given("I am logged in to Salesforce as the configured user")
def _login(login_page, session_state):
    if not session_state["logged_in"]:
        login_page.login()
        session_state["logged_in"] = True
```

## Fixtures available in steps

All defined in [`fixtures/salesforce/salesforce_fixtures.py`](../fixtures/salesforce/salesforce_fixtures.py):

| Fixture | Scope | Purpose |
|---|---|---|
| `page` | session | Playwright `Page` (alias of `open_browser`) |
| `login_page` | session | `LoginPage` |
| `home_page` | session | `Homepage` (app launcher, tabs) |
| `setup_page` | session | `Setup` page |
| `lead_fields` | session | `LeadsPage_Fields` |
| `lead_picklists` | session | `LeadsPage_PicklistValues` |
| `lead_validation` | session | `LeadsPage_ValidationErrors` |
| `lead_happy_path` | session | `LeadsPage_HappyPath` |
| `test_data` | session | Random Lead data shared across the session |
| `session_state` | session | Background-step idempotency flags |

> The root [conftest.py](../conftest.py) registers
> `fixtures.salesforce.salesforce_fixtures` as a pytest plugin so these
> fixtures are discoverable from every test file.

## Adding a new feature

1. Create `tests/features/salesforce/<Area>.feature` with appropriate tags.
2. Create `tests/steps/salesforce/test_<area>_bdd.py` and call
   `scenarios("../../features/salesforce/<Area>.feature")`.
3. Reuse steps from `common_steps.py` where possible; add new ones beside the
   `scenarios(...)` call.
4. If a new page is involved, add the page object under
   `pages/salesforce/` and expose a fixture in `salesforce_fixtures.py`.
5. Register any new marker in [pytest.ini](../pytest.ini).
