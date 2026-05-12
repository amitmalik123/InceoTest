---
description: 'Cucumber/Gherkin BDD testing conventions for feature files'
applyTo: '**/*.feature'
---

# Cucumber/Gherkin BDD Conventions

This instruction file defines standards for writing Cucumber feature files using Gherkin syntax for Behavior-Driven Development (BDD) with pytest-bdd.

## Gherkin Syntax Basics

### Keywords

- **Feature**: High-level description of software feature
- **Background**: Common steps that run before each scenario
- **Scenario**: Single test case (concrete example)
- **Scenario Outline**: Template for multiple test cases with different data
- **Examples**: Data table for Scenario Outline
- **Given**: Preconditions (system state before action)
- **When**: Actions (what the user does)
- **Then**: Expected outcomes (what should happen)
- **And**: Additional steps (same type as previous)
- **But**: Negative steps (same type as previous)

### Feature File Structure

```gherkin
# File: features/account_management/create_account.feature

@tag1 @tag2
Feature: Feature Name
  Brief description of the feature

  Additional context or business value (optional)

  Background:
    Given common precondition
    And another common precondition

  @scenario-tag
  Scenario: Scenario name
    Given precondition
    When action
    Then expected outcome
    And additional outcome

  @scenario-outline-tag
  Scenario Outline: Scenario template name
    Given precondition with "<parameter>"
    When action with "<parameter>"
    Then expected outcome with "<result>"

    Examples:
      | parameter  | result         |
      | value1     | expected1      |
      | value2     | expected2      |
```

## Writing Declarative Scenarios

### Declarative (GOOD) - What, not How

Focus on WHAT the user wants to achieve, not HOW:

```gherkin
Scenario: User creates a new account
  Given I am logged in as a financial advisor
  When I create an account named "John Doe Retirement"
  Then the account should appear in my account list
  And the account should be persisted to the database
```

### Imperative (AVOID) - Too much detail

Avoid low-level UI interactions:

```gherkin
# BAD - Too much UI detail, brittle
Scenario: User creates a new account
  Given I am on the homepage
  And I click the "Accounts" menu
  And I click the "New Account" button
  And I type "John Doe Retirement" in the "Account Name" field
  And I click the "Account Type" dropdown
  And I select "Retirement" from the dropdown
  And I click the "Save" button
  Then I should see the text "Account created successfully"
  And I should see "John Doe Retirement" in the table
```

**Why declarative is better:**
- ✅ Focused on business behavior, not UI implementation
- ✅ Resistant to UI changes (button IDs, class names)
- ✅ Readable by non-technical stakeholders
- ✅ Reusable step definitions

## Scenario Best Practices

### One Behavior Per Scenario

Each scenario should test one specific behavior:

```gherkin
# GOOD - Single behavior
Scenario: Create account with valid data
  Given I am authenticated
  When I create an account with valid data
  Then the account should be created successfully

# GOOD - Different behavior
Scenario: Reject account with invalid name
  Given I am authenticated
  When I attempt to create an account with an empty name
  Then I should see a validation error

# BAD - Multiple unrelated behaviors
Scenario: Account management
  Given I am authenticated
  When I create an account
  Then the account is created
  When I edit the account
  Then the account is updated
  When I delete the account
  Then the account is deleted
```

### Descriptive Scenario Names

Use clear, business-focused names:

```gherkin
# GOOD
Scenario: Financial advisor creates retirement account for new client
Scenario: System rejects account creation when name exceeds character limit
Scenario: Account balance reflects transaction history after deposit

# BAD
Scenario: Test 1
Scenario: Account test
Scenario: Create
```

## Background Usage

Use `Background` for common setup steps:

```gherkin
Feature: Account Management

  Background:
    Given I am authenticated as a financial advisor
    And I have permission to manage accounts
    And I am on the accounts page

  Scenario: Create account
    When I create an account named "Test Account"
    Then the account should appear in the list

  Scenario: Edit account
    Given an account named "Existing Account" exists
    When I edit the account name to "Updated Account"
    Then the account name should be updated
```

**When to use Background:**
- ✅ Steps are common to ALL scenarios in the feature
- ✅ Setup is essential precondition for every test
- ✅ Reduces repetition across scenarios

**When NOT to use Background:**
- ❌ Only some scenarios need the setup
- ❌ Background becomes too long (>5 steps)
- ❌ Setup is scenario-specific

## Scenario Outline for Data Variations

Use `Scenario Outline` with `Examples` for data-driven tests:

```gherkin
Scenario Outline: Validate account name length
  Given I am authenticated
  When I attempt to create an account with name "<name>"
  Then I should see validation result "<result>"

  Examples: Valid names
    | name                  | result            |
    | ABC                   | Account created   |
    | Valid Account Name    | Account created   |
    | X                     | Account created   |

  Examples: Invalid names
    | name          | result                              |
    |               | Name is required                    |
    | AB            | Name must be at least 3 characters  |
    | <256 chars>   | Name must not exceed 255 characters |
```

**Benefits:**
- ✅ Test multiple inputs without duplicating scenarios
- ✅ Clear data coverage (valid vs invalid inputs)
- ✅ Easy to add new test cases

**Examples Table Best Practices:**
```gherkin
# GOOD - Descriptive column names
Examples:
  | account_name       | account_type | expected_status |
  | Retirement Fund    | retirement   | created         |
  | Savings Account    | savings      | created         |

# BAD - Vague column names
Examples:
  | input1         | input2     | output   |
  | Retirement Fund| retirement | created  |
```

## Tagging Strategies

### Organizational Tags

Use tags to categorize and filter scenarios:

```gherkin
@smoke @critical-path @account-management
Scenario: Create account with valid data

@regression @api @account-management
Scenario: Create account via API

@ui @slow @account-management
Scenario: Create account via UI

@wip @skip
Scenario: Future feature - account archiving
```

### Common Tag Conventions

**Test Type Tags:**
- `@smoke` - Critical smoke tests
- `@regression` - Regression test suite
- `@integration` - Integration tests
- `@unit` - Unit-level tests
- `@e2e` - End-to-end tests

**Interface Tags:**
- `@api` - API tests
- `@ui` - UI tests
- `@database` - Database tests

**Feature Area Tags:**
- `@account-management`
- `@authentication`
- `@reporting`
- `@user-management`

**Status Tags:**
- `@wip` - Work in progress
- `@skip` - Temporarily skip
- `@manual` - Manual test (not automated)
- `@blocked` - Blocked by dependency

**Priority Tags:**
- `@critical`
- `@high`
- `@medium`
- `@low`

**Environment Tags:**
- `@dev-only`
- `@staging-only`
- `@production-safe`

### Running Tests by Tag

```bash
# pytest-bdd with markers (tags)
pytest -m smoke
pytest -m "regression and api"
pytest -m "account-management and not slow"
```

## Data Tables

Use data tables for complex data structures:

```gherkin
Scenario: Create multiple accounts at once
  Given I am authenticated
  When I create the following accounts:
    | Account Name        | Type       | Initial Balance |
    | Retirement Fund     | retirement | 10000.00        |
    | Emergency Savings   | savings    | 5000.00         |
    | Investment Account  | investment | 25000.00        |
  Then all accounts should be created successfully
  And each account should have the specified balance
```

**Step Definition (pytest-bdd):**
```python
from pytest_bdd import when, parsers

@when('I create the following accounts:')
def create_multiple_accounts(accounts_page, datatable):
    """Create multiple accounts from data table."""
    for row in datatable:
        accounts_page.create_account(
            name=row['Account Name'],
            account_type=row['Type'],
            initial_balance=row['Initial Balance']
        )
```

## Doc Strings (Multi-line Text)

Use doc strings for longer text content:

```gherkin
Scenario: Send API request with JSON payload
  Given I am authenticated with a valid API token
  When I send a POST request to "/api/accounts" with body:
    """
    {
      "account": {
        "name": "Test Account",
        "type": "checking",
        "balance": 1000.00,
        "owner": {
          "id": "12345",
          "name": "John Doe"
        }
      }
    }
    """
  Then the response status should be 201
  And the response should contain the account ID
```

**Step Definition:**
```python
from pytest_bdd import when, parsers

@when(parsers.parse('I send a POST request to "{endpoint}" with body:'))
def send_post_request(api_client, endpoint, docstring):
    """Send POST request with JSON body from doc string."""
    import json
    response = api_client.post(endpoint, json=json.loads(docstring))
    # Store response for later assertions
```

## Feature Organization

### Feature File Naming

```
features/
├── account_management/
│   ├── create_account.feature
│   ├── edit_account.feature
│   ├── delete_account.feature
│   └── view_accounts.feature
├── authentication/
│   ├── login.feature
│   ├── logout.feature
│   └── password_reset.feature
└── reporting/
    ├── generate_report.feature
    └── export_data.feature
```

### Feature Scope

Keep features focused on a single area:

```gherkin
# GOOD - Focused feature
Feature: Account Creation
  As a financial advisor
  I want to create client accounts
  So that I can manage client portfolios

  Scenario: Create account with valid data
  Scenario: Reject invalid account data
  Scenario: Duplicate account name prevention

# BAD - Too broad
Feature: Account Management
  Scenario: Create account
  Scenario: Edit account
  Scenario: Delete account
  Scenario: View accounts
  Scenario: Archive accounts
  Scenario: Search accounts
  # Too many responsibilities in one feature
```

## Step Definition Patterns

### Reusable Steps

Write steps that can be reused across scenarios:

```gherkin
# Reusable step
Given I am authenticated

# Used in multiple scenarios
Scenario: Create account
  Given I am authenticated
  When I create an account
  Then the account is created

Scenario: Edit account
  Given I am authenticated
  And an account exists
  When I edit the account
  Then the account is updated
```

### Step Patterns with Parameters

Use parameters for flexible steps:

```gherkin
# Pattern: When I create an account named "<name>"
When I create an account named "Retirement Fund"
When I create an account named "Savings Account"

# Pattern: Then I should see "<message>"
Then I should see "Account created successfully"
Then I should see "Validation error: Name is required"
```

**pytest-bdd Step Definition:**
```python
from pytest_bdd import when, then, parsers

@when(parsers.parse('I create an account named "{name}"'))
def create_account_by_name(accounts_page, name):
    """Create account with specified name."""
    accounts_page.create_account(name)

@then(parsers.parse('I should see "{message}"'))
def verify_message(page, message):
    """Verify message appears on page."""
    assert page.get_by_text(message).is_visible()
```

## Acceptance Criteria Mapping

Link scenarios to acceptance criteria:

```gherkin
Feature: Account Creation
  User Story: As a financial advisor, I want to create client accounts

  @AC1
  Scenario: Create account with valid name
    # Implements AC-1: User can create account with valid name
    Given I am authenticated
    When I create an account with name "Test Account"
    Then the account should be created successfully

  @AC2
  Scenario Outline: Validate account name length
    # Implements AC-2: Account name must be 3-255 characters
    Given I am authenticated
    When I attempt to create an account with name "<name>"
    Then I should see result "<result>"

    Examples:
      | name       | result                              |
      | AB         | Name must be at least 3 characters  |
      | ABC        | Account created                     |
      | <256 char> | Name must not exceed 255 characters |

  @AC3
  Scenario: Reject duplicate account name
    # Implements AC-3: Duplicate account names are rejected
    Given I am authenticated
    And an account named "Existing" exists
    When I attempt to create an account with name "Existing"
    Then I should see error "Account name already exists"
```

**Benefits:**
- ✅ Clear traceability from AC → Scenario → Step Definition
- ✅ Easy to verify all ACs are covered
- ✅ Tags enable AC-focused test runs: `pytest -m AC1`

## Comments and Documentation

Use comments to clarify intent:

```gherkin
Feature: Account Management

  # This feature covers basic CRUD operations for financial advisor accounts.
  # Note: Account deletion requires manager approval (tested separately).

  Background:
    # Standard authentication setup for all scenarios
    Given I am authenticated as a financial advisor

  @smoke
  Scenario: Create account with valid data
    # Happy path - most common success case
    When I create an account with valid data
    Then the account should appear in the account list

  # Note: Special characters in account names are handled by AC-5 (see separate feature)
```

## Anti-Patterns to Avoid

### ❌ Don't Mix Abstraction Levels

```gherkin
# BAD - Mixing high-level and low-level steps
Scenario: Create account
  Given I am logged in
  When I click the "New Account" button  # Too detailed
  And I create an account                # Too vague
  Then the account exists
```

### ❌ Don't Depend on Scenario Order

```gherkin
# BAD - Scenarios depend on execution order
Scenario: Create account
  When I create account "Test Account"
  # Creates account in system

Scenario: Edit account
  # Assumes "Test Account" exists from previous scenario
  When I edit account "Test Account"
  # FRAGILE - breaks if run independently
```

### ❌ Don't Embed Test Data

```gherkin
# BAD - Hardcoded test IDs
Scenario: Edit account
  Given account with ID "12345" exists
  # Brittle - ID may not exist in different environments

# GOOD - Descriptive data
Scenario: Edit account
  Given an account named "Test Account" exists
  # Flexible - can be created in any environment
```

### ❌ Don't Write Scenario-Specific Steps

```gherkin
# BAD - Step only useful in one scenario
When I create account "John Doe Retirement" with type "Retirement" and balance 10000.00
# Too specific, not reusable

# GOOD - Reusable step with parameters
When I create an account with the following details:
  | name               | type       | balance   |
  | John Doe Retirement| Retirement | 10000.00  |
# Flexible, reusable across scenarios
```

## Integration with pytest-bdd

### Scenario Registration

```python
# features/step_defs/account_steps.py
from pytest_bdd import scenario

# Register scenario from feature file
scenario('../account_management/create_account.feature', 'Create account with valid data')
```

### Step Definitions

```python
from pytest_bdd import given, when, then, parsers

@given('I am authenticated')
def authenticated_user(auth_context):
    auth_context.login()

@when(parsers.parse('I create an account named "{name}"'))
def create_account(accounts_page, name):
    accounts_page.create_account(name)

@then(parsers.parse('the account "{name}" should appear in the list'))
def verify_account_in_list(accounts_page, name):
    assert accounts_page.is_account_visible(name)
```

## AssetMark-Specific Requirements

### Security Considerations

❌ **Don't include sensitive data in features:**
```gherkin
# BAD - Credentials in feature file
Given I log in with username "admin@assetmark.com" and password "P@ssw0rd123"
```

✅ **Use generic placeholders:**
```gherkin
# GOOD - Generic authentication
Given I am authenticated as a financial advisor

# Step definition loads credentials from environment
@given('I am authenticated as a financial advisor')
def authenticate(auth_context):
    import os
    auth_context.login(
        username=os.getenv('TEST_USER'),
        password=os.getenv('TEST_PASSWORD')
    )
```

### Tagging Conventions

Use AssetMark-specific tags:

```gherkin
@assetmark @account-management @smoke
Scenario: Create client account

@assetmark @reporting @regression
Scenario: Generate quarterly report

@assetmark @compliance @critical
Scenario: Verify regulatory compliance
```

## Running BDD Tests

```bash
# Run all feature tests
pytest features/

# Run specific feature
pytest features/account_management/create_account.feature

# Run by tag
pytest -m smoke
pytest -m "regression and not slow"

# Verbose output (show Gherkin steps)
pytest features/ -v

# Generate Allure report
pytest features/ --alluredir=./allure-results
allure serve ./allure-results
```

## Best Practices Summary

### DO:
✅ Write declarative scenarios (WHAT, not HOW)
✅ Keep scenarios focused (one behavior per scenario)
✅ Use Background for common setup
✅ Use Scenario Outline for data variations
✅ Use descriptive scenario names
✅ Tag scenarios for organization
✅ Link scenarios to acceptance criteria
✅ Write reusable step definitions
✅ Use business language (domain terminology)
✅ Keep features focused on single area

### DON'T:
❌ Write imperative scenarios (detailed UI clicks)
❌ Mix multiple behaviors in one scenario
❌ Depend on scenario execution order
❌ Embed test data (use parameters)
❌ Include sensitive data in features
❌ Write scenario-specific steps
❌ Mix abstraction levels
❌ Use vague scenario names
❌ Create overly broad features

## Summary

Follow Cucumber/Gherkin conventions for:
- **Declarative scenarios** - Focus on behavior, not implementation
- **Clear structure** - Feature → Background → Scenarios → Steps
- **Data-driven testing** - Scenario Outline + Examples
- **Tagging** - Organize and filter scenarios
- **Traceability** - Link to acceptance criteria
- **Reusability** - Write flexible step definitions
- **Security** - Never commit sensitive data

These conventions ensure maintainable, readable, and executable specifications that serve as living documentation.

## Coverage Note

AssetMark enforces a **85% minimum line and branch coverage** standard across all code. Ensure any code changes maintain this threshold. Run coverage before submitting PRs and verify CI gates pass.
