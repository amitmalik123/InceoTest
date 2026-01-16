# Proposal Automation Testing

Automated end-to-end testing suite for the Proposal system using Playwright with BDD (Behavior-Driven Development).

## Project Structure

```
├── config/              # Environment configurations (.env files)
├── data/                # Test data (proposal variations)
├── fixtures/            # Playwright fixtures and BDD setup
├── framework/           # Framework-level utilities (reporters)
├── helperfunctions/     # Navigation and UI helper functions
├── pages/               # Page Object Models
├── reports/             # Test execution reports and artifacts
│   ├── allure-results/
│   ├── playwright-report/
│   └── test-results/
├── scripts/             # Build and maintenance scripts
├── tests/
│   ├── bdd/             # BDD tests (Gherkin features & step definitions)
│   │   ├── features/
│   │   └── steps/
│   └── ui/              # Traditional UI tests
└── utils/               # Shared utilities (env loader, etc.)
```

## Getting Started

### Prerequisites

- Node.js 22.x or higher
- npm or yarn package manager

### Installation

```bash
# Install dependencies
npm ci

# Install Playwright browsers
npx playwright install chromium
```

### Environment Setup

Configure your test environment in `config/.env.<environment>`:
- `.env.test11` - Test11 environment
- `.env.test10` - Test10 environment  
- `.env.silo` - Silo environment

Set the `ENVIRONMENT` variable or it defaults to `test11`.

## Running Tests

### BDD Tests

```bash
# Run all BDD tests
npm run test:bdd

# Run specific tagged tests
npm run test:e2e          # End-to-end tests
npm run test:widgets      # Widget tests
npm run test:smoke        # Smoke tests

# Generate BDD tests from features only
npm run bddgen
```

### UI Tests

```bash
# Run all tests
npm test

# Run with UI mode
npm run test:ui

# Run and show report
npm run test:report
```

### Environment-Specific Runs

```bash
# Windows PowerShell
$env:ENVIRONMENT='silo'; npm run test:bdd

# Linux/Mac
ENVIRONMENT=silo npm run test:bdd
```

## Writing Tests

### BDD Tests (Gherkin)

1. Create a `.feature` file in `tests/bdd/features/`
2. Write scenarios using Given/When/Then syntax
3. Implement step definitions in `tests/bdd/steps/`
4. Run `npm run bddgen` to generate test files
5. Execute with `npm run test:bdd`

Example feature:
```gherkin
@e2e
Feature: Portfolio Creation
  
  Scenario: Create a new portfolio with strategies
    Given I am logged into the application
    And I am on the Portfolio Engine page
    When I create a portfolio with strategies
    Then the portfolio should be saved successfully
```

### Page Object Models

Place reusable page interactions in `pages/`:
- Use selectors and actions only (no assertions)
- Keep pages focused on a single UI area
- Export methods for common workflows

## Configuration

### Playwright Config

Main configuration in `playwright.config.ts`:
- Test timeout: 30 minutes (for long-running E2E tests)
- Expect timeout: 5 minutes
- Projects: setup → chromium → teardown

### Setup & Teardown

- **Setup** (`tests/bdd/auth.setup.ts`): Authenticates once and saves session
- **Teardown** (`tests/bdd/cleanup.teardown.ts`): Cleans up test data after all tests

## Reports

Reports are generated in the `reports/` directory:

- **Allure**: `reports/allure-results/` - View with `npx allure serve reports/allure-results`
- **Playwright HTML**: `reports/playwright-report/` - View with `npx playwright show-report reports/playwright-report`
- **JUnit XML**: `reports/test-results/junit-report.xml` - For CI integration

## CI/CD

Pipeline configuration: `azurePipeline.yaml`

### Manual Runs
- Select environment (test11, test10, silo)
- Specify tags to run
- Configure thread count

### Scheduled Runs
- **3:30 PM EST**: Silo environment
- **3:45 PM EST**: Test11 environment
- Runs: `@regression`, `@smokeTest`, `@e2e` tests

## Development

### Code Style

- EditorConfig enforced (`.editorconfig`)
- TypeScript for type safety
- 4-space indentation for code
- 2-space indentation for configs

### Best Practices

1. Use environment variables for configuration
2. Centralize selectors in Page Objects
3. Write descriptive test names
4. Tag tests appropriately (`@smoke`, `@regression`, `@e2e`)
5. Keep step definitions simple and reusable

## Dependencies

Key packages:
- `@playwright/test` - Test framework
- `playwright-bdd` - BDD support for Playwright
- `allure-playwright` - Allure reporting
- `dotenv` - Environment variable management

## Troubleshooting

### Tests fail to authenticate
- Verify credentials in `config/.env.<environment>`
- Check if setup project ran: look for `authfiles/role1.json`
- Run setup manually: `npx playwright test --project=setup`

### Tests can't find elements
- Increase timeout in `playwright.config.ts`
- Check selectors in Page Object Models
- Verify test environment is responsive

### BDD tests not updating
- Run `npm run bddgen` after changing feature files or step definitions
- Check `.features-gen/` for generated test files

