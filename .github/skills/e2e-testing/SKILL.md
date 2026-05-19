---
name: 'e2e-testing'
description: 'Playwright E2E testing patterns for AssetMark web applications — page object model, fixtures, test data management, and CI integration'
user-invokable: false
---

# E2E Testing with Playwright

This skill defines end-to-end testing patterns using Playwright for AssetMark web applications, including page object model, fixtures, test data management, accessibility testing, and CI/CD integration.

## Why Playwright?

Playwright is the preferred E2E testing framework for AssetMark applications because:
- **Multi-browser support** — Chromium, Firefox, WebKit (Safari)
- **Auto-wait capabilities** — Reduces flaky tests
- **Network interception** — Mock API responses
- **Parallel execution** — Fast test runs
- **Built-in screenshots/videos** — Debug failures easily
- **TypeScript first-class support** — Type-safe tests
- **Accessibility testing** — Built-in ARIA role selectors
- **MCP integration** — Copilot agents can drive Playwright directly for exploration and test iteration

## Explore-First Testing Approach

**Before writing E2E tests, explore the application** to understand real behavior:

### The Exploration Workflow

1. **Launch the application** — Open the target page in Playwright
2. **Navigate manually** — Click through the user flow you want to test
3. **Capture UI state** — Take screenshots, note element selectors
4. **Document real behavior**:
   - What elements exist? (buttons, inputs, forms)
   - What are the actual selectors? (`data-testid`, ARIA roles)
   - What states are visible? (loading, error, success)
   - What network calls are made? (API endpoints)
   - What redirects occur? (navigation flow)

5. **Identify test scenarios from reality**:
   - Happy path = what you just navigated successfully
   - Error paths = error messages you observed
   - Edge cases = boundary conditions in the UI
   - Missing states = loading/error states not yet handled

### Why Explore First?

**Traditional approach (assumptions-driven):**
```typescript
// ❌ Write tests based on requirements doc assumptions
test('should create account', async ({ page }) => {
  await page.goto('/accounts');
  await page.getByTestId('create-btn').click(); // Assumes this exists
  // ... may not match reality
});
```

**Explore-first approach (reality-driven):**
```typescript
// 1. First, navigate /accounts in Playwright and observe:
//    - Button is actually getByRole('button', { name: 'New Account' })
//    - No data-testid on button (needs to be added)
//    - Form has 3 fields, not 2 as in requirements
//    - Success shows toast, not redirect (different from spec)

// ✅ Write tests based on actual observed behavior
test('should create account', async ({ page }) => {
  await page.goto('/accounts');
  await page.getByRole('button', { name: 'New Account' }).click(); // Matches reality
  // ... tests now match actual implementation
});
```

**Benefits:**
- ✅ Tests match reality, not stale requirements
- ✅ Discover missing `data-testid` attributes early
- ✅ Find edge cases requirements didn't mention
- ✅ Generate robust selectors that won't break
- ✅ Reduce test flakiness from incorrect assumptions

### MCP-Driven Exploration

When using Copilot agents with Playwright MCP integration:

```
Agent workflow:
1. User: "Generate E2E tests for account creation"
2. Agent: Uses playwright tool to navigate /accounts/new
3. Agent: Takes snapshot, identifies elements
4. Agent: Documents actual selectors, states, flows
5. Agent: Generates page object matching reality
6. Agent: Writes tests based on observed behavior
7. Agent: Runs tests and iterates until passing
```

This exploration-driven approach is **built into our prompts and agents** — they explore before generating.

## Project Structure

Organize Playwright tests with clear separation of concerns:

```
my-app/
├── tests/
│   ├── e2e/
│   │   ├── auth/
│   │   │   ├── login.spec.ts
│   │   │   └── logout.spec.ts
│   │   ├── accounts/
│   │   │   ├── create-account.spec.ts
│   │   │   ├── edit-account.spec.ts
│   │   │   └── delete-account.spec.ts
│   │   └── dashboard/
│   │       └── dashboard.spec.ts
│   ├── pages/
│   │   ├── LoginPage.ts
│   │   ├── DashboardPage.ts
│   │   ├── AccountsPage.ts
│   │   └── BasePage.ts
│   ├── fixtures/
│   │   ├── auth.fixture.ts
│   │   ├── testData.fixture.ts
│   │   └── index.ts
│   └── helpers/
│       ├── apiHelpers.ts
│       └── dataGenerators.ts
├── playwright.config.ts
└── package.json
```

### Directory Organization

- **`tests/e2e/`** — Test spec files organized by feature/module
- **`tests/pages/`** — Page Object Model classes
- **`tests/fixtures/`** — Custom Playwright fixtures for auth, test data, etc.
- **`tests/helpers/`** — Utility functions for API calls, data generation
- **`playwright.config.ts`** — Playwright configuration

## Page Object Model (POM) Pattern

**Required:** All Playwright tests must use Page Object Model to:
- Reduce code duplication
- Improve maintainability
- Centralize locator management
- Make tests more readable

### Page Object Structure

```typescript
// tests/pages/LoginPage.ts
import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class LoginPage extends BasePage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    super(page);
    this.page = page;

    // Prefer data-testid for stable selectors
    this.emailInput = page.getByTestId('login-email');
    this.passwordInput = page.getByTestId('login-password');
    this.loginButton = page.getByRole('button', { name: 'Log In' });
    this.errorMessage = page.getByTestId('error-message');
  }

  async goto() {
    await this.page.goto('/login');
    await this.waitForPageLoad();
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async getErrorMessage() {
    return await this.errorMessage.textContent();
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('domcontentloaded');
    await this.emailInput.waitFor({ state: 'visible' });
  }
}
```

### Base Page Pattern

Create a `BasePage` class with common functionality:

```typescript
// tests/pages/BasePage.ts
import { Page } from '@playwright/test';

export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('domcontentloaded');
  }

  async waitForNetworkIdle() {
    await this.page.waitForLoadState('networkidle');
  }

  async takeScreenshot(name: string) {
    await this.page.screenshot({ path: `screenshots/${name}.png` });
  }

  async getPageTitle() {
    return await this.page.title();
  }

  async navigateTo(url: string) {
    await this.page.goto(url);
    await this.waitForPageLoad();
  }
}
```

### Page Object Best Practices

## Python Playwright Patterns

Playwright also supports Python for E2E testing, integrating seamlessly with pytest.

### Project Structure (Python)

```
my-app/
├── tests/
│   ├── e2e/
│   │   ├── auth/
│   │   │   ├── test_login.py
│   │   │   └── test_logout.py
│   │   ├── accounts/
│   │   │   ├── test_create_account.py
│   │   │   └── test_edit_account.py
│   │   └── dashboard/
│   │       └── test_dashboard.py
│   ├── pages/
│   │   ├── login_page.py
│   │   ├── dashboard_page.py
│   │   ├── accounts_page.py
│   │   └── base_page.py
│   ├── fixtures/
│   │   ├── auth_fixtures.py
│   │   └── test_data_fixtures.py
│   └── conftest.py             # pytest-playwright main config and fixtures
├── playwright.config.py        # Playwright test config (optional, can be in pytest.ini)
├── pytest.ini                  # Pytest config
└── requirements.txt
```

### Python Page Object Model

```python
# tests/pages/login_page.py
from playwright.sync_api import Page, Locator, expect
from .base_page import BasePage
import os
import allure

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{os.getenv('APP_BASE_URL')}/login"
        self._email_input = page.get_by_test_id('login-email')
        self._password_input = page.get_by_test_id('login-password')
        self._login_button = page.get_by_role('button', name='Log In')
        self._error_message = page.get_by_test_id('error-message')

    @allure.step('Navigate to login page')
    def navigate(self):
        self.page.goto(self.url)
        self.wait_for_page_load()

    @allure.step('Log in with username={username}, password=******')
    def login(self, username: str, password: str):
        self._email_input.fill(username)
        self._password_input.fill(password)
        self._login_button.click()

    @property
    def error_message(self) -> Locator:
        return self._error_message

    def get_error_message_text(self) -> str:
        expect(self._error_message).to_be_visible()
        return self._error_message.text_content()
```

### pytest-playwright Fixtures

`pytest-playwright` provides built-in fixtures like `page`, `context`, `browser`.

**Example `conftest.py` with custom fixture:**
```python
# tests/conftest.py
import pytest
import os
from dotenv import load_dotenv
from playwright.sync_api import Page, expect
from tests.pages.login_page import LoginPage # Assuming path

load_dotenv()

@pytest.fixture(scope='session')
def base_url():
    url = os.getenv('APP_BASE_URL', 'http://localhost:3000')
    print(f"Using base URL: {url}")
    return url

@pytest.fixture(scope='function')
def authenticated_page(page: Page, base_url):
    """Fixture providing an authenticated Playwright page."""
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(
        username=os.getenv('TEST_USER'),
        password=os.getenv('TEST_PASSWORD')
    )
    # Wait for successful navigation/dashboard load
    page.wait_for_url(f"{base_url}/dashboard");
    expect(page.get_by_text('Welcome to your Dashboard')).to_be_visible()
    yield page

# You can also extend browser context, e.g., for persistent login state
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, base_url):
    return {
        **browser_context_args,
        "base_url": base_url,
        # Potentially add storageState here for pre-authenticated context
    }
```

### Sync vs Async API

- **Sync API (default for pytest-playwright)**: Simpler to use, `page.click()`, `page.fill()`
- **Async API**: More performant for advanced scenarios, requires `async` and `await`.

Most AssetMark Python Playwright tests will use the default **sync API** for simplicity and directness within pytest test functions.

### Allure Integration (Python)

Ensure `allure-pytest` is installed. Use `allure.step()`, `allure.attach()` in your Python tests.

```python
import pytest
import allure
from playwright.sync_api import Page, expect
from tests.pages.login_page import LoginPage
import os

@allure.feature('Authentication')
@allure.story('User Login')
class TestLogin:

    @allure.title('Successful login with valid credentials')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_successful_login(self, page: Page, base_url):
        login_page = LoginPage(page)

        with allure.step('Navigate to login page'):
            login_page.navigate()

        with allure.step('Enter valid credentials and submit'):
            login_page.login(
                username=os.getenv('TEST_USER'),
                password=os.getenv('TEST_PASSWORD')
            )

        with allure.step('Verify redirection to dashboard'):
            expect(page).to_have_url(f"{base_url}/dashboard")
            expect(page.get_by_text('Welcome to your Dashboard')).to_be_visible()

        allure.attach(
            page.screenshot(),
            name='dashboard_screenshot',
            attachment_type=allure.attachment_type.PNG
        )

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(item, call):
        """Attach screenshot to Allure report on test failure."""
        outcome = yield
        rep = outcome.get_result()

        if rep.when == 'call' and rep.failed:
            if 'page' in item.funcargs:
                page = item.funcargs['page']
                allure.attach(
                    page.screenshot(),
                    name='failure_screenshot',
                    attachment_type=allure.attachment_type.PNG
                )
```

This hook is typically placed in `conftest.py` to apply to all tests.

### Page Object Best Practices

#### DO:
✅ **Use `data-testid` attributes** for stable selectors
✅ **Use `getByRole` for semantic elements** (buttons, links, headings)
✅ **Return page objects from actions** (method chaining)
✅ **Encapsulate wait logic** in page objects
✅ **Create reusable methods** for common actions
✅ **Use descriptive method names** (e.g., `fillLoginForm`, not `fill`)

#### DON'T:
❌ **Don't use CSS selectors or XPath** unless absolutely necessary
❌ **Don't include assertions in page objects** (assertions go in tests)
❌ **Don't duplicate locators** across multiple page objects
❌ **Don't hardcode test data** in page objects

## Custom Fixtures

Fixtures extend Playwright's capabilities for authentication, test data, and environment setup.

### Authentication Fixture

```typescript
// tests/fixtures/auth.fixture.ts
import { test as base } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

type AuthFixtures = {
  authenticatedPage: Page;
  adminPage: Page;
};

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page }, use) => {
    // Perform login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(
      process.env.TEST_USER_EMAIL!,
      process.env.TEST_USER_PASSWORD!
    );

    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard');

    // Provide authenticated page to test
    await use(page);
  },

  adminPage: async ({ page }, use) => {
    // Login as admin
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(
      process.env.ADMIN_EMAIL!,
      process.env.ADMIN_PASSWORD!
    );

    await page.waitForURL('/dashboard');
    await use(page);
  },
});
```

### Test Data Fixture

```typescript
// tests/fixtures/testData.fixture.ts
import { test as base } from '@playwright/test';
import { generateTestAccount, cleanupTestAccount } from '../helpers/dataGenerators';

type TestDataFixtures = {
  testAccount: { name: string; id: string };
};

export const test = base.extend<TestDataFixtures>({
  testAccount: async ({ page }, use) => {
    // Create test account before test
    const account = await generateTestAccount();

    // Provide account to test
    await use(account);

    // Cleanup after test
    await cleanupTestAccount(account.id);
  },
});
```

### Combining Fixtures

```typescript
// tests/fixtures/index.ts
import { test as authTest } from './auth.fixture';
import { test as dataTest } from './testData.fixture';
import { mergeTests } from '@playwright/test';

export const test = mergeTests(authTest, dataTest);
export { expect } from '@playwright/test';
```

### Using Fixtures in Tests

```typescript
import { test, expect } from './fixtures';

test('authenticated user can create account', async ({ authenticatedPage, testAccount }) => {
  // authenticatedPage is already logged in
  // testAccount is pre-created and will be cleaned up

  await authenticatedPage.goto('/accounts/new');
  // ... test logic
});
```

## Test Structure & Patterns

### Test File Organization

```typescript
// tests/e2e/accounts/create-account.spec.ts
import { test, expect } from '../../fixtures';
import { AccountsPage } from '../../pages/AccountsPage';

test.describe('Create Account', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    const accountsPage = new AccountsPage(authenticatedPage);
    await accountsPage.goto();
  });

  test('should create account with valid data', async ({ authenticatedPage }) => {
    const accountsPage = new AccountsPage(authenticatedPage);

    // Arrange
    const accountName = `Test Account ${Date.now()}`;

    // Act
    await accountsPage.clickNewAccountButton();
    await accountsPage.fillAccountForm({ name: accountName });
    await accountsPage.submitForm();

    // Assert
    await expect(accountsPage.successMessage).toBeVisible();
    await expect(accountsPage.getAccountByName(accountName)).toBeVisible();
  });

  test('should show validation error for empty name', async ({ authenticatedPage }) => {
    const accountsPage = new AccountsPage(authenticatedPage);

    await accountsPage.clickNewAccountButton();
    await accountsPage.submitForm(); // Submit without filling

    await expect(accountsPage.validationError).toBeVisible();
    await expect(accountsPage.validationError).toContainText('Name is required');
  });

  test('should handle API error gracefully', async ({ authenticatedPage }) => {
    const accountsPage = new AccountsPage(authenticatedPage);

    // Mock API failure
    await authenticatedPage.route('**/api/accounts', route => {
      route.fulfill({ status: 500, body: 'Internal Server Error' });
    });

    await accountsPage.clickNewAccountButton();
    await accountsPage.fillAccountForm({ name: 'Test' });
    await accountsPage.submitForm();

    await expect(accountsPage.errorMessage).toBeVisible();
    await expect(accountsPage.errorMessage).toContainText('Failed to create account');
  });
});
```

### Assertion Patterns

#### Use Playwright's Built-in Assertions

```typescript
// ✅ Good - Auto-wait built in
await expect(page.getByText('Success')).toBeVisible();
await expect(page.getByRole('button', { name: 'Submit' })).toBeEnabled();
await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveTitle('Dashboard');

// ❌ Bad - No auto-wait
const text = await page.getByText('Success').textContent();
expect(text).toBe('Success');
```

#### Common Assertions

```typescript
// Visibility
await expect(locator).toBeVisible();
await expect(locator).toBeHidden();

// Content
await expect(locator).toContainText('Expected');
await expect(locator).toHaveText('Exact text');
await expect(locator).toHaveValue('input value');

// State
await expect(locator).toBeEnabled();
await expect(locator).toBeDisabled();
await expect(locator).toBeChecked();

// Count
await expect(page.getByRole('listitem')).toHaveCount(5);

// URL & Title
await expect(page).toHaveURL(/dashboard/);
await expect(page).toHaveTitle('Dashboard');

// Custom timeout
await expect(locator).toBeVisible({ timeout: 10000 });
```

## Selector Strategy

### Selector Priority (Best to Worst)

1. **`data-testid`** — Preferred for stability
   ```typescript
   page.getByTestId('submit-button')
   ```

2. **`getByRole`** — Semantic, accessible
   ```typescript
   page.getByRole('button', { name: 'Submit' })
   page.getByRole('textbox', { name: 'Email' })
   page.getByRole('heading', { name: 'Welcome' })
   ```

3. **`getByLabel`** — For form inputs
   ```typescript
   page.getByLabel('Email Address')
   page.getByLabel('Password')
   ```

4. **`getByPlaceholder`** — For inputs with placeholders
   ```typescript
   page.getByPlaceholder('Enter your email')
   ```

5. **`getByText`** — For text content
   ```typescript
   page.getByText('Sign In')
   page.getByText(/Welcome .+/) // Regex
   ```

6. **CSS Selectors** — Last resort
   ```typescript
   page.locator('.submit-button')
   ```

### ❌ Avoid These Selectors

- **XPath** — Brittle and hard to maintain
- **Complex CSS** — `.parent > .child:nth-child(2)`
- **IDs** (unless `data-testid`) — Often auto-generated
- **Classes** — Can change with styling updates

## Waiting & Timing

### ✅ DO: Use Playwright's Auto-Wait

Playwright automatically waits for elements to be:
- **Attached** to DOM
- **Visible** on screen
- **Stable** (not animating)
- **Enabled** (if interacting)
- **Editable** (if typing)

```typescript
// These automatically wait for the element:
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByLabel('Email').fill('test@example.com');
await expect(page.getByText('Success')).toBeVisible();
```

### ❌ DON'T: Use Fixed Timeouts

```typescript
// ❌ Bad - Flaky and slow
await page.waitForTimeout(5000);

// ✅ Good - Wait for specific condition
await expect(page.getByText('Loading...')).toBeHidden();
await expect(page.getByText('Data loaded')).toBeVisible();
```

### Advanced Waiting

```typescript
// Wait for network request
await page.waitForResponse(response =>
  response.url().includes('/api/accounts') && response.status() === 200
);

// Wait for navigation
await page.waitForURL('/dashboard');

// Wait for load state
await page.waitForLoadState('networkidle');

// Wait for function
await page.waitForFunction(() => window.dataLoaded === true);
```

## Network Mocking & Interception

Mock API responses for reliable tests:

```typescript
test('should handle empty account list', async ({ page }) => {
  // Mock empty response
  await page.route('**/api/accounts', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    });
  });

  const accountsPage = new AccountsPage(page);
  await accountsPage.goto();

  await expect(page.getByText('No accounts found')).toBeVisible();
});

test('should retry on network error', async ({ page }) => {
  let requestCount = 0;

  await page.route('**/api/accounts', route => {
    requestCount++;
    if (requestCount < 3) {
      // Fail first 2 requests
      route.abort('failed');
    } else {
      // Succeed on 3rd request
      route.fulfill({
        status: 200,
        body: JSON.stringify([{ id: 1, name: 'Account 1' }]),
      });
    }
  });

  const accountsPage = new AccountsPage(page);
  await accountsPage.goto();

  await expect(accountsPage.getAccountByName('Account 1')).toBeVisible();
});
```

## Accessibility Testing

Playwright has built-in accessibility testing support:

### ARIA Role Selectors

```typescript
// Use semantic role queries
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('textbox', { name: 'Email' }).fill('test@example.com');
await page.getByRole('heading', { name: 'Welcome' }).isVisible();
```

### Keyboard Navigation Testing

```typescript
test('should be keyboard navigable', async ({ page }) => {
  await page.goto('/login');

  // Tab through form
  await page.keyboard.press('Tab'); // Focus email
  await expect(page.getByLabel('Email')).toBeFocused();

  await page.keyboard.press('Tab'); // Focus password
  await expect(page.getByLabel('Password')).toBeFocused();

  await page.keyboard.press('Tab'); // Focus submit button
  await expect(page.getByRole('button', { name: 'Submit' })).toBeFocused();

  // Submit with Enter
  await page.keyboard.press('Enter');
});
```

### Accessibility Snapshot Testing

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('should not have accessibility violations', async ({ page }) => {
  await page.goto('/dashboard');

  const accessibilityScanResults = await new AxeBuilder({ page }).analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});
```

## Visual Regression Testing

### Screenshot Comparison

```typescript
test('dashboard should match snapshot', async ({ page }) => {
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');

  // Compare against baseline
  await expect(page).toHaveScreenshot('dashboard.png', {
    fullPage: true,
    maxDiffPixels: 100, // Allow small differences
  });
});

// Update snapshots with:
// npx playwright test --update-snapshots
```

### Visual Testing Best Practices

- **Mask dynamic content** (timestamps, user names)
- **Set viewport size** consistently
- **Wait for animations** to complete
- **Use `maxDiffPixels`** to tolerate minor rendering differences

```typescript
await expect(page).toHaveScreenshot({
  mask: [page.getByTestId('timestamp')],
  animations: 'disabled',
});
```

## CI/CD Integration

### Azure Pipelines Configuration (AssetMark Standard)

For AssetMark applications, use Azure Pipelines:

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: NodeTool@0
    inputs:
      versionSpec: '18.x'
    displayName: 'Install Node.js'

  - script: npm ci
    displayName: 'Install dependencies'

  - script: npx playwright install --with-deps
    displayName: 'Install Playwright Browsers'

  - script: npx playwright test
    displayName: 'Run Playwright tests'
    env:
      TEST_USER_EMAIL: $(TEST_USER_EMAIL)
      TEST_USER_PASSWORD: $(TEST_USER_PASSWORD)

  - task: PublishTestResults@2
    condition: always()
    inputs:
      testResultsFormat: 'JUnit'
      testResultsFiles: '**/test-results/junit.xml'
      mergeTestResults: true
      failTaskOnFailedTests: true
    displayName: 'Publish test results'

  - task: PublishPipelineArtifact@1
    condition: always()
    inputs:
      targetPath: 'playwright-report'
      artifact: 'playwright-report'
      publishLocation: 'pipeline'
    displayName: 'Publish Playwright report'
```

### GitHub Actions (For This Workflow Repo Only)

This workflow repository uses GitHub Actions for its own CI:

```yaml
# .github/workflows/playwright.yml (for this repo only, not AssetMark apps)
name: Playwright Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright Browsers
        run: npx playwright install --with-deps

      - name: Run Playwright tests
        run: npx playwright test
        env:
          TEST_USER_EMAIL: ${{ secrets.TEST_USER_EMAIL }}
          TEST_USER_PASSWORD: ${{ secrets.TEST_USER_PASSWORD }}

      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

### Playwright Configuration for CI

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI ? 'blob' : 'html',

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

## Anti-Patterns to Avoid

### ❌ DON'T: Duplicate Locators

```typescript
// Bad
test('test 1', async ({ page }) => {
  await page.locator('[data-testid="submit"]').click();
});

test('test 2', async ({ page }) => {
  await page.locator('[data-testid="submit"]').click(); // Duplicated
});

// Good - Use Page Object
class MyPage {
  readonly submitButton = page.getByTestId('submit');
}
```

### ❌ DON'T: Test Implementation Details

```typescript
// Bad - Tests internal state
expect(component.state.isLoading).toBe(true);

// Good - Tests user-visible behavior
await expect(page.getByText('Loading...')).toBeVisible();
```

### ❌ DON'T: Create Interdependent Tests

```typescript
// Bad - Tests depend on each other
test('create account', async ({ page }) => {
  // Creates account with ID 123
});

test('edit account', async ({ page }) => {
  // Assumes account 123 exists from previous test
});

// Good - Each test is independent
test('edit account', async ({ page, testAccount }) => {
  // testAccount fixture creates and cleans up data
});
```

### ❌ DON'T: Use `page.waitForTimeout()`

```typescript
// Bad
await page.click('button');
await page.waitForTimeout(5000); // Flaky!

// Good
await page.click('button');
await expect(page.getByText('Success')).toBeVisible();
```

## Example: Complete E2E Test File

```typescript
// tests/e2e/accounts/manage-account.spec.ts
import { test, expect } from '../../fixtures';
import { AccountsPage } from '../../pages/AccountsPage';
import { AccountDetailsPage } from '../../pages/AccountDetailsPage';

test.describe('Account Management', () => {
  test.use({ storageState: 'auth.json' }); // Reuse auth state

  test('should create, edit, and delete account', async ({ page }) => {
    const accountsPage = new AccountsPage(page);
    const detailsPage = new AccountDetailsPage(page);

    const accountName = `E2E Test Account ${Date.now()}`;
    const updatedName = `${accountName} (Updated)`;

    // Create
    await accountsPage.goto();
    await accountsPage.createAccount(accountName);
    await expect(accountsPage.getAccountByName(accountName)).toBeVisible();

    // Edit
    await accountsPage.openAccount(accountName);
    await detailsPage.editName(updatedName);
    await detailsPage.save();
    await expect(detailsPage.successMessage).toBeVisible();

    // Delete
    await detailsPage.delete();
    await detailsPage.confirmDelete();
    await expect(page).toHaveURL('/accounts');
    await expect(accountsPage.getAccountByName(updatedName)).toBeHidden();
  });

  test('should validate required fields', async ({ page }) => {
    const accountsPage = new AccountsPage(page);

    await accountsPage.goto();
    await accountsPage.clickNewAccountButton();
    await accountsPage.submitForm();

    await expect(accountsPage.validationError).toContainText('Name is required');
  });

  test('should handle concurrent edits', async ({ page, context }) => {
    // Test scenario: Two users editing same account
    const page2 = await context.newPage();
    const accountsPage1 = new AccountsPage(page);
    const accountsPage2 = new AccountsPage(page2);

    // Both users open same account
    await accountsPage1.goto();
    const account = await accountsPage1.getFirstAccount();
    await accountsPage1.openAccount(account);

    await accountsPage2.goto();
    await accountsPage2.openAccount(account);

    // User 1 saves first
    await new AccountDetailsPage(page).editName('Updated by User 1');
    await new AccountDetailsPage(page).save();

    // User 2 tries to save
    await new AccountDetailsPage(page2).editName('Updated by User 2');
    await new AccountDetailsPage(page2).save();

    // Should show conflict error
    await expect(page2.getByText('Conflict')).toBeVisible();

    await page2.close();
  });
});
```

## Summary

- **Always use Page Object Model** for maintainability
- **Prefer `data-testid` and `getByRole`** for stable selectors
- **Use fixtures** for authentication and test data management
- **Let Playwright auto-wait** — avoid fixed timeouts
- **Mock network requests** for reliable tests
- **Test accessibility** with keyboard navigation and ARIA roles
- **Run in CI/CD** with proper configuration
- **Capture screenshots/videos** on failure for debugging
- **Keep tests independent** — no shared state between tests

This skill provides the foundation for reliable, maintainable E2E tests that catch regressions before they reach production.


## Coverage Standard

AssetMark mandates **85% unit test coverage** for all business logic. New code must meet this threshold before merge. Flag coverage gaps during review and use `amk-coverage-gap-testgen` to generate targeted tests for uncovered lines.
