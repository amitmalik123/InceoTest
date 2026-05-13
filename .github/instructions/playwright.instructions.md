---
description: 'Playwright E2E testing coding standards for AssetMark — required patterns, selector strategy, and anti-patterns to avoid'
applyTo: '**/*.spec.ts, **/*.spec.tsx, **/tests/e2e/**, **/playwright/**'
---

# Playwright E2E Testing Standards

Coding standards for writing Playwright end-to-end tests in AssetMark applications.

## Table of Contents

1. [Page Object Model (Required)](#1-page-object-model-required)
2. [Selector Strategy](#2-selector-strategy)
3. [Use Playwright Fixtures, Not `beforeAll`/`afterAll`](#3-use-playwright-fixtures-not-beforeallafterall)
4. [Use `expect` from `@playwright/test`, Not Jest](#4-use-expect-from-playwrighttest-not-jest)
5. [Async/Await Everywhere](#5-asyncawait-everywhere)
6. [Group Tests with `test.describe`](#6-group-tests-with-testdescribe)
7. [Test File Naming Convention](#7-test-file-naming-convention)
8. [No `page.waitForTimeout()` — Use Proper Waits](#8-no-pagewaitfortimeout--use-proper-waits)
9. [Network Mocking Patterns](#9-network-mocking-patterns)
10. [Screenshots on Failure (Configured in `playwright.config.ts`)](#10-screenshots-on-failure-configured-in-playwrightconfigts)
11. [Assertions Best Practices](#11-assertions-best-practices)
12. [Test Independence](#12-test-independence)
13. [Playwright Configuration Requirements](#13-playwright-configuration-requirements)
14. [Common Anti-Patterns](#14-common-anti-patterns)
- [Summary Checklist](#summary-checklist)
- [Resources](#resources)

## 1. Page Object Model (Required)

**All page interactions must use Page Object Model.**

### ✅ DO:

```typescript
// Page Object
export class LoginPage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(private page: Page) {
    this.emailInput = page.getByTestId('login-email');
    this.passwordInput = page.getByTestId('login-password');
    this.submitButton = page.getByRole('button', { name: 'Log In' });
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

// Test
test('user can login', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password');
  await expect(page).toHaveURL('/dashboard');
});
```

### ❌ DON'T:

```typescript
// Bad - Direct page interaction in test
test('user can login', async ({ page }) => {
  await page.goto('/login');
  await page.getByTestId('login-email').fill('user@example.com');
  await page.getByTestId('login-password').fill('password');
  await page.getByRole('button', { name: 'Log In' }).click();
});
```

## 2. Selector Strategy

### Priority Order (Best to Worst)

1. **`data-testid`** — Preferred for elements without semantic roles
2. **`getByRole`** — For semantic HTML (buttons, links, headings)
3. **`getByLabel`** — For form inputs with labels
4. **`getByPlaceholder`** — For inputs with placeholders
5. **`getByText`** — For text content
6. **CSS selectors** — Last resort only

### ✅ DO:

```typescript
// Best - data-testid
page.getByTestId('submit-button')

// Good - Semantic role
page.getByRole('button', { name: 'Submit' })
page.getByRole('textbox', { name: 'Email Address' })
page.getByRole('heading', { name: 'Welcome' })

// Good - Associated label
page.getByLabel('Email Address')
page.getByLabel('Remember me')

// Good - Text content
page.getByText('Sign In')
page.getByText(/Welcome .+/) // Regex
```

### ❌ DON'T:

```typescript
// Bad - CSS selectors
page.locator('.btn-primary')
page.locator('#submit-button')
page.locator('.container > .row:nth-child(2) .button')

// Bad - XPath
page.locator('//div[@class="container"]//button')

// Bad - Auto-generated IDs
page.locator('#button-1234567')
```

## 3. Use Playwright Fixtures, Not `beforeAll`/`afterAll`

### ✅ DO:

```typescript
// Custom fixture
import { test as base } from '@playwright/test';

export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    // Setup
    await page.goto('/login');
    await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL);
    await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD);
    await page.getByRole('button', { name: 'Log In' }).click();
    await page.waitForURL('/dashboard');

    // Use
    await use(page);

    // Teardown (if needed)
  },
});

// Test
test('can access dashboard', async ({ authenticatedPage }) => {
  await expect(authenticatedPage).toHaveURL('/dashboard');
});
```

### ❌ DON'T:

```typescript
// Bad - beforeAll/afterAll
let page: Page;

test.beforeAll(async ({ browser }) => {
  page = await browser.newPage();
  await page.goto('/login');
  // Login logic...
});

test.afterAll(async () => {
  await page.close();
});

test('test 1', async () => {
  // Uses shared page - tests are not independent!
});
```

## 4. Use `expect` from `@playwright/test`, Not Jest

### ✅ DO:

```typescript
import { test, expect } from '@playwright/test';

test('should display success message', async ({ page }) => {
  await expect(page.getByText('Success')).toBeVisible();
  await expect(page).toHaveURL('/dashboard');
  await expect(page).toHaveTitle('Dashboard');
});
```

### ❌ DON'T:

```typescript
import { expect } from '@jest/globals'; // Wrong import!

test('should display success message', async ({ page }) => {
  const text = await page.getByText('Success').textContent();
  expect(text).toBe('Success'); // No auto-wait!
});
```

## 5. Async/Await Everywhere

**All Playwright operations are async and must be awaited.**

### ✅ DO:

```typescript
await page.goto('/login');
await page.getByLabel('Email').fill('user@example.com');
await page.getByRole('button', { name: 'Submit' }).click();
await expect(page.getByText('Welcome')).toBeVisible();
```

### ❌ DON'T:

```typescript
page.goto('/login'); // Missing await!
page.getByLabel('Email').fill('user@example.com'); // Missing await!
page.getByRole('button', { name: 'Submit' }).click(); // Missing await!
```

## 6. Group Tests with `test.describe`

### ✅ DO:

```typescript
test.describe('Account Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/accounts');
  });

  test('should create account', async ({ page }) => {
    // Test logic
  });

  test('should edit account', async ({ page }) => {
    // Test logic
  });

  test('should delete account', async ({ page }) => {
    // Test logic
  });
});

test.describe('Account Validation', () => {
  test('should require account name', async ({ page }) => {
    // Test logic
  });

  test('should reject duplicate names', async ({ page }) => {
    // Test logic
  });
});
```

### ❌ DON'T:

```typescript
// Bad - No grouping, no shared setup
test('should create account', async ({ page }) => {
  await page.goto('/accounts');
  // Test logic
});

test('should edit account', async ({ page }) => {
  await page.goto('/accounts'); // Duplicated setup
  // Test logic
});
```

## 7. Test File Naming Convention

Use `kebab-case.spec.ts` format:

### ✅ DO:

```
tests/e2e/accounts/create-account.spec.ts
tests/e2e/accounts/edit-account.spec.ts
tests/e2e/auth/login.spec.ts
tests/e2e/dashboard/dashboard-overview.spec.ts
```

### ❌ DON'T:

```
tests/e2e/CreateAccount.test.ts
tests/e2e/accountsTest.ts
tests/e2e/test_accounts.ts
```

## 8. No `page.waitForTimeout()` — Use Proper Waits

Playwright automatically waits for elements to be ready. Use explicit waits for specific conditions, not fixed timeouts.

### ✅ DO:

```typescript
// Auto-wait (built into most actions)
await page.getByRole('button', { name: 'Submit' }).click();

// Wait for element visibility
await expect(page.getByText('Loading...')).toBeHidden();
await expect(page.getByText('Data loaded')).toBeVisible();

// Wait for URL change
await page.waitForURL('/dashboard');

// Wait for network response
await page.waitForResponse(res =>
  res.url().includes('/api/accounts') && res.status() === 200
);

// Wait for load state
await page.waitForLoadState('networkidle');

// Wait for custom condition
await page.waitForFunction(() => window.dataReady === true);
```

### ❌ DON'T:

```typescript
// Bad - Fixed timeout, flaky
await page.click('button');
await page.waitForTimeout(5000); // Don't do this!
await expect(page.getByText('Success')).toBeVisible();

// Bad - Arbitrary sleep
await new Promise(resolve => setTimeout(resolve, 3000));
```

**Exception:** `waitForTimeout` is acceptable ONLY for debugging or very specific timing scenarios (e.g., animation duration verification).

## 9. Network Mocking Patterns

Mock API responses for reliable, isolated tests:

### ✅ DO:

```typescript
test('should handle empty data', async ({ page }) => {
  // Mock empty response
  await page.route('**/api/accounts', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    });
  });

  await page.goto('/accounts');
  await expect(page.getByText('No accounts found')).toBeVisible();
});

test('should handle API error', async ({ page }) => {
  // Mock error response
  await page.route('**/api/accounts', route => {
    route.fulfill({
      status: 500,
      body: 'Internal Server Error',
    });
  });

  await page.goto('/accounts');
  await expect(page.getByText('Failed to load accounts')).toBeVisible();
});

test('should retry on network failure', async ({ page }) => {
  let attemptCount = 0;

  await page.route('**/api/accounts', route => {
    attemptCount++;
    if (attemptCount < 3) {
      route.abort('failed'); // Fail first 2 attempts
    } else {
      route.fulfill({ status: 200, body: '[]' }); // Succeed on 3rd
    }
  });

  await page.goto('/accounts');
  await expect(page.getByText('No accounts found')).toBeVisible();
  expect(attemptCount).toBe(3);
});
```

## 10. Screenshots on Failure (Configured in `playwright.config.ts`)

Configure screenshot capture in `playwright.config.ts`, not in individual tests:

### ✅ DO (playwright.config.ts):

```typescript
export default defineConfig({
  use: {
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'on-first-retry',
  },
});
```

### Manual Screenshots (when needed):

```typescript
test('visual regression test', async ({ page }) => {
  await page.goto('/dashboard');

  // Visual comparison
  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixels: 100,
    mask: [page.getByTestId('timestamp')], // Mask dynamic content
  });
});
```

## 11. Assertions Best Practices

### ✅ DO:

```typescript
// Use Playwright's auto-retry assertions
await expect(locator).toBeVisible();
await expect(locator).toBeHidden();
await expect(locator).toBeEnabled();
await expect(locator).toBeDisabled();
await expect(locator).toContainText('Expected');
await expect(locator).toHaveText('Exact text');
await expect(locator).toHaveValue('value');
await expect(locator).toHaveCount(5);
await expect(page).toHaveURL(/dashboard/);
await expect(page).toHaveTitle('Dashboard');

// Custom timeout when needed
await expect(locator).toBeVisible({ timeout: 10000 });

// Soft assertions (continue on failure)
await expect.soft(locator).toBeVisible();
await expect.soft(otherLocator).toContainText('text');
```

### ❌ DON'T:

```typescript
// Bad - No auto-retry, race conditions
const isVisible = await locator.isVisible();
expect(isVisible).toBe(true);

// Bad - Extracting value first
const text = await locator.textContent();
expect(text).toBe('Expected');
```

## 12. Test Independence

**Each test must be fully independent and self-contained.**

### ✅ DO:

```typescript
test('test 1', async ({ page }) => {
  // Create own test data
  const testAccount = await createTestAccount();

  // Test logic
  await page.goto(`/accounts/${testAccount.id}`);
  await expect(page.getByText(testAccount.name)).toBeVisible();

  // Clean up
  await deleteTestAccount(testAccount.id);
});

test('test 2', async ({ page }) => {
  // Independent test data
  const anotherAccount = await createTestAccount();

  // Test logic
  await page.goto(`/accounts/${anotherAccount.id}`);
  await expect(page.getByText(anotherAccount.name)).toBeVisible();

  // Clean up
  await deleteTestAccount(anotherAccount.id);
});
```

### ❌ DON'T:

```typescript
let sharedAccountId: number;

test('create account', async ({ page }) => {
  // Creates account
  sharedAccountId = 123; // Test 2 depends on this!
});

test('edit account', async ({ page }) => {
  // Depends on previous test
  await page.goto(`/accounts/${sharedAccountId}`); // Fragile!
});
```

## 13. Playwright Configuration Requirements

`playwright.config.ts` must include:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI, // Prevent .only in CI
  retries: process.env.CI ? 2 : 0, // Retry flaky tests in CI
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
    // Optional: Add Firefox, WebKit for cross-browser testing
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

## 14. Common Anti-Patterns

### ❌ Testing Implementation Details

```typescript
// Bad - Tests internal state
expect(component.state.count).toBe(5);

// Good - Tests user-visible behavior
await expect(page.getByText('Count: 5')).toBeVisible();
```

### ❌ Overly Specific Selectors

```typescript
// Bad - Brittle
page.locator('div.container > ul.list > li:nth-child(2) > a.link')

// Good - Semantic
page.getByRole('listitem').nth(1).getByRole('link')
```

### ❌ Long Test Methods

```typescript
// Bad - Too much in one test
test('complete user journey', async ({ page }) => {
  // 50 lines of code testing login, navigation, CRUD, logout...
});

// Good - Focused tests
test.describe('User Journey', () => {
  test('user can login', async ({ page }) => { /* ... */ });
  test('user can create account', async ({ page }) => { /* ... */ });
  test('user can edit account', async ({ page }) => { /* ... */ });
  test('user can logout', async ({ page }) => { /* ... */ });
});
```

## Summary Checklist

Before submitting a Playwright test:

- [ ] Uses Page Object Model for all page interactions
- [ ] Selectors prioritize `data-testid` and `getByRole`
- [ ] No CSS selectors or XPath (unless absolutely necessary)
- [ ] Uses Playwright fixtures, not `beforeAll`/`afterAll`
- [ ] Imports `expect` from `@playwright/test`, not Jest
- [ ] All Playwright calls are `await`ed
- [ ] Tests grouped with `test.describe`
- [ ] Test file named `feature-name.spec.ts`
- [ ] No `page.waitForTimeout()` (uses proper waits)
- [ ] Network mocking for reliable, isolated tests
- [ ] Screenshots/videos configured in `playwright.config.ts`
- [ ] Uses Playwright's auto-retry assertions
- [ ] Tests are independent (no shared state)
- [ ] Page Objects encapsulate locators and actions
- [ ] Assertions test user-visible behavior, not implementation

## Resources

- Playwright Documentation: https://playwright.dev/
- AssetMark E2E Testing Skill: `.github/skills/e2e-testing/SKILL.md`
- Example Tests: `tests/e2e/` directory


## Coverage Standard

AssetMark mandates **85% unit test coverage** for all business logic. New code must meet this threshold before merge. Flag coverage gaps during review and use `amk-coverage-gap-testgen` to generate targeted tests for uncovered lines.
