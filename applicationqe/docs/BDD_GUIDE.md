# BDD Testing with pytest-bdd

This project now includes Behavior-Driven Development (BDD) testing using pytest-bdd and Gherkin syntax.

## Structure

```
src/
├── features/
│   └── roth_conversion.feature              # Gherkin feature files
├── step_definitions/
│   ├── conftest.py                          # Fixtures for page objects and test data
│   ├── common_steps.py                      # Common/shared step definitions
│   ├── login_steps.py                       # Login-related steps
│   ├── navigation_steps.py                  # Navigation steps
│   ├── account_steps.py                     # Account selection steps
│   ├── account_wizard_steps.py              # Account wizard steps
│   ├── roth_conversion_steps.py             # Roth conversion steps
│   └── tracking_center_steps.py             # Tracking center steps
└── testScript/
    ├── test_roth_conversion_flow.py         # Original pytest test
    ├── test_roth_conversion_bdd.py          # BDD with inline steps (deprecated)
    └── test_roth_conversion_cucumber.py     # BDD test runner (modular steps)
```

## Two BDD Approaches

### 1. Modular Step Definitions (Recommended)
**File**: `test_roth_conversion_cucumber.py`
- Step definitions organized in separate files by feature area
- More maintainable and reusable
- Follows standard Cucumber/BDD practices
- Easier to navigate and extend

### 2. Inline Step Definitions
**File**: `test_roth_conversion_bdd.py`
- All steps in one file
- Good for simple tests or getting started
- Easier to see everything in one place

## Feature File

The feature file ([src/features/roth_conversion.feature](src/features/roth_conversion.feature)) uses Gherkin syntax with:
- **Feature**: High-level description
- **Background**: Common steps executed before each scenario
- **Scenario**: Test case with Given-When-Then steps

## Running BDD Tests

### Run the modular BDD test (recommended):
```powershell
pytest src/testScript/test_roth_conversion_cucumber.py -v
```

### Run the inline BDD test:
```powershell
pytest src/testScript/test_roth_conversion_bdd.py -v
```

### Run all tests (including BDD):
```powershell
pytest
```

### Run with Allure reporting:
```powershell
pytest src/testScript/test_roth_conversion_cucumber.py --alluredir=reports/allure-results -v
```

### Run with verbose step output:
```powershell
pytest src/testScript/test_roth_conversion_cucumber.py -v --gherkin-terminal-reporter
```

## Benefits of BDD

1. **Readable Specifications**: Feature files are human-readable and can be understood by non-technical stakeholders
2. **Reusable Steps**: Step definitions can be reused across multiple scenarios
3. **Living Documentation**: Feature files serve as up-to-date documentation
4. **Collaboration**: Business analysts, QAs, and developers can collaborate on feature files
5. **Test Coverage**: Easy to add new scenarios by combining existing steps

## Adding New Scenarios

To add a new scenario to [roth_conversion.feature](src/features/roth_conversion.feature):

```gherkin
Scenario: Convert with different amount
  When I login with valid credentials
  And I navigate to the conversion page
  And I enter conversion amount "5000"
  Then the conversion should be processed
```

### If you need new steps with the modular approach:

1. Choose the appropriate step definition file (or create a new one)
2. Add the step definition:

Example in [src/step_definitions/roth_conversion_steps.py](src/step_definitions/roth_conversion_steps.py):
```python
@when(parsers.parse('I enter conversion amount "{amount}"'))
def enter_custom_conversion_amount(roth_conversion_page, amount):
    """Enter a custom conversion amount"""
    with allure.step(f"Enter conversion amount: {amount}"):
        logger.info(f"Entering custom amount: {amount}")
        roth_conversion_page.enter_amount(amount)
```

### Step Definition Organization

- **common_steps.py** - Background, setup, teardown steps
- **login_steps.py** - Authentication steps
- **navigation_steps.py** - Menu navigation steps
- **account_steps.py** - Account search and selection
- **account_wizard_steps.py** - Account wizard flow
- **roth_conversion_steps.py** - Roth conversion form steps
- **tracking_center_steps.py** - Verification steps

## BDD vs Traditional Tests

- **Traditional** ([test_roth_conversion_flow.py](src/testScript/test_roth_conversion_flow.py)): Procedural Python code with inline logic
- **BDD Inline** ([test_roth_conversion_bdd.py](src/testScript/test_roth_conversion_bdd.py)): Gherkin scenarios with all steps in one file
- **BDD Modular** ([test_roth_conversion_cucumber.py](src/testScript/test_roth_conversion_cucumber.py)): Gherkin scenarios with organized step definitions

All approaches work with the same page objects and produce the same Allure reports.

## Benefits of Modular Step Definitions

1. **Reusability**: Steps can be shared across multiple feature files
2. **Maintainability**: Each file focuses on one area of the application
3. **Collaboration**: Multiple team members can work on different step files
4. **Discoverability**: Easy to find where a step is defined
5. **Testing**: Step definitions can be unit tested independently

## pytest-bdd Features Used

- `scenarios()`: Loads all scenarios from a feature file
- `@given`, `@when`, `@then`: Decorators for step definitions
- `@parsers.parse()`: Extract parameters from steps
- Fixtures: Share page objects and context across steps
