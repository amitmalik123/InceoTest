import { defineConfig, devices } from '@playwright/test';
import { defineBddConfig } from 'playwright-bdd';
import { loadEnvironment } from './utils/env-loader';

/**
 * Read environment variables from file.
 * https://github.com/motdotla/dotenv
 */
loadEnvironment();

const testDir = defineBddConfig({
    paths: ['tests/bdd/features/**/*.feature'],
    require: ['fixtures/fixtures.ts', 'tests/bdd/steps/**/*.ts'],
});

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
    /* Configure individual test timeouts */
    timeout: 1_800_000,
    /*Set timeout for entire test suite*/
    globalTimeout: 3_600_000,
    /* Set timeout for each expect call*/
    expect: {
        timeout: 300_000,
    },
    /* Directory for test files */
    testDir,
    /* Run tests in files in parallel */
    fullyParallel: true,
    /* Fail the build on CI if you accidentally left test.only in the source code. */
    forbidOnly: !!process.env.CI,
    /* Retry # for CI : local */
    retries: process.env.CI ? 2 : 0,
    /* Opt out of parallel tests on CI. */
    workers: process.env.CI ? 1 : undefined,
    /* Reporter to use. See https://playwright.dev/docs/test-reporters */
    reporter: [
        ['allure-playwright', { outputFolder: 'reports/allure-results' }],
        ['html', { outputFolder: 'reports/playwright-report', open: 'never' }],
        ['junit', { outputFile: 'reports/test-results/junit-report.xml' }],
        ['list'], // Always show test results in console
    ],
    /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
    use: {
        /* Base URL to use in actions like `await page.goto('')`. */
        baseURL: process.env.base_URL + '/en.aspx',

        /* Ignore HTTPS errors for untrusted certificates */
        ignoreHTTPSErrors: true,

        trace: 'retain-on-failure',
        video: 'retain-on-failure',
        screenshot: 'only-on-failure',
        headless: true,
    },

    /* Configure projects for major browsers */
    projects: [
        {
            name: 'setup',
            testDir: './tests/bdd',
            testMatch: /auth\.setup\.ts/,
            teardown: 'teardown',
            use: {
                // Show setup logs in output
                video: 'off',
                screenshot: 'off',
            },
        },

        {
            name: 'chromium',
            dependencies: ['setup'],
            use: {
                ...devices['Desktop Chrome'],
                contextOptions: {
                    ignoreHTTPSErrors: true,
                },
            },
        },

        {
            name: 'teardown',
            testDir: './tests/bdd',
            testMatch: /cleanup\.teardown\.ts/,
            //dependencies: ['chromium'],
        },

        {
            name: 'firefox',
            dependencies: ['setup'],
            use: { ...devices['Desktop Firefox'] },
        },

        {
            name: 'webkit',
            dependencies: ['setup'],
            use: { ...devices['Desktop Safari'] },
        },

        /* Test against mobile viewports. */
        // {
        //   name: 'Mobile Chrome',
        //   use: { ...devices['Pixel 5'] },
        // },
        // {
        //   name: 'Mobile Safari',
        //   use: { ...devices['iPhone 12'] },
        // },

        /* Test against branded browsers. */
        // {
        //   name: 'Microsoft Edge',
        //   use: { ...devices['Desktop Edge'], channel: 'msedge' },
        // },
        // {
        //   name: 'Google Chrome',
        //   use: { ...devices['Desktop Chrome'], channel: 'chrome' },
        // },
    ],

    /* Run your local dev server before starting the tests */
    // webServer: {
    //   command: 'npm run start',
    //   url: 'http://localhost:3000',
    //   reuseExistingServer: !process.env.CI,
    // },
});
