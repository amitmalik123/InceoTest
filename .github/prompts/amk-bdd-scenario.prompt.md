---
name: 'amk-bdd-scenario'
description: 'Generate Cucumber feature file and pytest-bdd step definitions from a user story'
model: 'Claude Sonnet 4.6 (copilot)'
tools: ['search/codebase', 'read/readFile', 'edit/editFiles', 'execute/runInTerminal', 'execute/getTerminalOutput', 'search/fileSearch', 'search/listDirectory', 'search/searchResults', 'search/textSearch', 'search/usages', 'search/changes', 'read/problems', 'web/fetch', 'vscode/askQuestions', 'edit/createFile', 'edit/createDirectory', 'execute/testFailure', 'execute/createAndRunTask', 'execute/awaitTerminal', 'read/terminalLastCommand', 'agent']
---
# amk-bdd-scenario - BDD Scenario Generator

Generate a Gherkin `.feature` file and corresponding `pytest-bdd` Python step definitions from a user story or acceptance criteria. The output will be executable specifications following BDD best practices, including proper naming, tagging, and parameterization.

## Input Context

The user will provide a user story, a list of acceptance criteria, or a description of a specific behavior to be automated. This might include:
- **User Story**: "As a [role], I want to [action], so that [benefit]."
- **Acceptance Criteria (ACs)**: A list of specific conditions that define when the story is done.
- **Behavioral description**: A detailed explanation of a system behavior.
- **Examples of data**: Specific data sets to test different variations.

## Output Goal

Generate two files:
1.  A Gherkin `.feature` file (e.g., `features/account_management/create_account.feature`)
    -   `Feature` section with descriptive text.
    -   Optional `Background` for common setup steps.
    -   One or more `Scenario` or `Scenario Outline` sections.
    -   `Given`, `When`, `Then`, `And` steps using clear, declarative language.
    -   `Examples` tables for `Scenario Outline` with well-named columns.
    -   Relevant tags (e.g., `@smoke`, `@regression`, `@AC-XXX`, `@api`, `@ui`).
    -   Comments to link to acceptance criteria or clarify intent.

2.  A Python `.py` file for `pytest-bdd` step definitions (e.g., `features/step_defs/account_steps.py`)
    -   Imports from `pytest_bdd`, `allure`, `pytest`.
    -   `scenario()` decorator to link feature files.
    -   `@given`, `@when`, `@then` decorators for each Gherkin step.
    -   `parsers.parse()` or `parsers.re()` for capturing step parameters.
    -   Integration with pytest fixtures for setup/teardown.
    -   Assertions using Python's built-in `assert` statement.
    -   `allure.step()` for detailed reporting.
    -   Helper functions or Page Object Model (for UI steps).
    -   Environment variable usage via `python-dotenv`.

## Step-by-Step Generation Plan

### 1. Parse User Story / Acceptance Criteria

- **Identify Feature**: Extract the main domain/feature from the user story (e.g., "Account Management", "User Authentication"). This becomes the `Feature` title.
- **Extract Roles/Benefits**: Use these for the narrative in the `Feature` section.
- **Break Down into Scenarios**: Each distinct acceptance criterion or behavior should become a `Scenario`.
    -   If a behavior has multiple data variations, use `Scenario Outline` with `Examples`.
- **Determine Background**: Identify common preconditions that apply to all (or most) scenarios within the feature. These go into `Background`.

### 2. Create `.feature` File

- **File Path**: `features/<feature_area>/<feature_name>.feature` (e.g., `features/account_management/create_account.feature`).
- **Feature Block**: Start with `@<feature_area>` tag, `Feature: <Feature Name>`, and the user story narrative.
- **Background**: If identified, add `Background:` with `Given`/`And` steps.
- **Scenarios**: For each identified scenario:
    -   Add relevant tags (e.g., `@smoke`, `@AC1`, `@api`, `@ui`).
    -   Write `Scenario: <Scenario Name>` or `Scenario Outline: <Scenario Template Name>`.
    -   Compose `Given`/`When`/`Then`/`And`/`But` steps using declarative, business-readable language. Avoid technical implementation details.
    -   For `Scenario Outline`, add an `Examples:` table with descriptive column headers and data.
    -   For multi-line text (e.g., JSON request body), use `"""` doc strings.
- **Refer to `cucumber.instructions.md` for Gherkin best practices.**

### 3. Create Step Definitions File

- **File Path**: `features/step_defs/<feature_area>_steps.py` or `features/step_defs/common_steps.py` for reusable steps.
- **Imports**: `pytest_bdd`, `allure`, `pytest`, `os`, `dotenv`, `playwright.sync_api` (if UI).
- **Register Scenarios**: For each scenario in the `.feature` file, add `scenario('<path_to_feature_file>', '<Scenario Name>')` at the top of the step definitions file.
- **Implement Steps**: For each unique `Given`, `When`, `Then` step in the `.feature` file:
    -   Use the corresponding decorator: `@given(...)`, `@when(...)`, `@then(...)`.
    -   Use `parsers.parse()` or `parsers.re()` to extract parameters from the Gherkin step string. Ensure parameter names match Python function arguments.
    -   Implement the step logic. This might involve:
        -   Calling an API client (e.g., `api_client.post(...)`).
        -   Interacting with a UI Page Object (e.g., `accounts_page.fill_form(...)`).
        -   Setting up/tearing down test data (via fixtures or direct calls).
        -   Making assertions (e.g., `assert response.status_code == 200`, `expect(element).to_be_visible()`).
    -   Wrap logical blocks with `with allure.step('Description'):` for detailed reporting.
    -   Use `allure.attach()` for screenshots on UI failures or API request/response bodies.
- **Fixtures**: Utilize existing pytest fixtures (e.g., `page`, `api_client`, custom `auth_context`). Create new local fixtures if specific to these steps.
- **Environment Variables**: Access `os.getenv()` for sensitive data or configuration.
- **Refer to `pytest.instructions.md` and `bdd-engineer.agent.md` for Python/pytest/Allure best practices.**

### 4. Final Review

- **Completeness**: Are all scenarios covered? Are all steps defined?
- **Readability**: Are both files clear, concise, and easy to understand by technical and non-technical stakeholders?
- **Correctness**: Do the step definitions accurately implement the Gherkin steps?
- **Adherence to Rules**: Are single quotes used in frontmatter? Are model names correct? Are tools allowed? Does it pass frontmatter validation?
- **No hardcoded secrets**: All sensitive info from `os.getenv()`.

## Example Request

**User:** "I need BDD scenarios for client account creation. As a financial advisor, I want to create client accounts so I can manage client portfolios. Acceptance Criteria: AC1: Advisor can create a new account with valid details (name, type, owner). AC2: System prevents creation with duplicate account names. AC3: Validation errors are shown for empty account name."

**Response Generation Steps:**
1.  **Feature**: `Client Account Management`.
2.  **Narrative**: "As a financial advisor, I want to create client accounts so that I can manage client portfolios."
3.  **Scenarios**:
    -   `Scenario: Create account with valid details` (AC1)
    -   `Scenario: Prevent creation with duplicate account name` (AC2)
    -   `Scenario Outline: Display validation errors for empty account name` (AC3) with `Examples` for empty string.
4.  **File Paths**: `features/account_management/create_client_account.feature` and `features/step_defs/account_steps.py`.
5.  **Gherkin Steps**: Write `Given`/`When`/`Then` for each scenario.
    -   Consider a `Background` for authentication.
    -   Use data tables for AC1 if multiple details.
6.  **Step Definitions**: Implement Python functions for each Gherkin step.
    -   Use `api_client` or `accounts_page` (Page Object).
    -   Integrate with Allure steps.
    -   Handle environment variables for credentials.

This prompt guides the generation of well-structured Gherkin feature files and robust pytest-bdd step definitions.
---

> **Coverage Standard:** AssetMark requires ≥85% line and branch coverage. Any code or tests generated by this prompt must meet this threshold.
