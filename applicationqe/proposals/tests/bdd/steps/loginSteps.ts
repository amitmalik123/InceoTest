import { Given, When, Then } from '../../../fixtures/fixtures';
import { expect } from '@playwright/test';
import * as fs from 'fs';
import { loadEnvironment } from '../../../utils/env-loader';
import { logger } from '../../../utils/logger';

// Load environment variables
loadEnvironment();

// Helper function to get auth file path based on role/user
function getAuthFilePath(role: string = 'role1'): string {
    return `./authfiles/${role}.json`;
}

Given('I am logged into the application', async ({ page, context, loginPage, switchIDPage }) => {
    const authFile = getAuthFilePath('role1');
    let authValid = false;

    // Try loading existing auth state
    if (fs.existsSync(authFile)) {
        try {
            const storageState = JSON.parse(fs.readFileSync(authFile, 'utf-8'));
            await context.addCookies(storageState.cookies);
            logger.debug('\nChecking validity of existing auth state');

            // Navigate to the app and verify we're still logged in
            await page.goto(process.env.baseURL + '/en.aspx');
            await page.waitForLoadState();

            // Check if advisor name is visible (indicates valid session)
            const advisorWelcome = page.getByText('Welcome ' + process.env.advisorName);
            await advisorWelcome.waitFor({ state: 'visible' });
            authValid = true;
            logger.debug('\nAuth state is valid, session active');
        } catch (error) {
            logger.debug('\nAuth state expired or invalid, performing fresh login');
            logger.error(error);
        }
    }

    // If auth not valid, perform fresh login
    if (!authValid) {
        await loginPage.gotoLoginPage();
        await loginPage.signIn(process.env.USER, process.env.PASS);

        const env = process.env.ENVIRONMENT || process.env.Environment;
        if (process.env.userID && env.toLowerCase() !== 'prod' && process.env.userID && env.toLowerCase() !== 'silo') {
            await switchIDPage.selectID(process.env.userID);
        }

        await page.goto(process.env.baseURL + '/en.aspx');
        await page.waitForLoadState();
        await expect(page.getByText('Welcome ' + process.env.advisorName)).toBeVisible();

        // Save auth state for future use
        await page.context().storageState({ path: authFile });
        logger.debug('\nFresh login completed, auth state saved');
    }
});

// Support for different roles/users
Given('I am logged in as {string}', async ({ page, context, loginPage, switchIDPage }, role: string) => {
    const authFile = getAuthFilePath(role);
    let authValid = false;

    if (fs.existsSync(authFile)) {
        try {
            await context.addCookies(JSON.parse(fs.readFileSync(authFile, 'utf-8')).cookies);
            await page.goto(process.env.baseURL + '/en.aspx');
            await page.waitForLoadState();

            // Validate auth is still valid
            const welcomeText = page.getByText('Welcome').or(page.getByText('Hello'));
            await welcomeText.waitFor({ state: 'visible' });
            authValid = true;
            logger.debug(`\nUsing cached auth state for ${role}`);
        } catch (error) {
            logger.debug(`\nCached auth state for ${role} expired or invalid, performing fresh login`);
            logger.error(error);
            fs.unlinkSync(authFile);
        }
    }

    if (!authValid) {
        // Perform login based on role-specific env vars
        await loginPage.gotoLoginPage();
        await loginPage.signIn(
            process.env[`USER_${role.toUpperCase()}`] || process.env.USER,
            process.env[`PASS_${role.toUpperCase()}`] || process.env.PASS
        );

        if (process.env[`userID_${role}`]) {
            await switchIDPage.selectID(process.env[`userID_${role}`]);
        }

        await page.waitForLoadState();
        await page.context().storageState({ path: authFile });
        logger.debug(`\nFresh login for ${role} completed, auth state saved`);
    }
});

Given('the user is on the login page', async ({ loginPage }) => {
    await loginPage.gotoLoginPage();
});

When('the user enters a valid username and password', async ({ switchIDPage, loginPage }) => {
    await loginPage.signIn(process.env.USER, process.env.PASS);

    // Switch to correct ID if using admin account
    const env = process.env.ENVIRONMENT || process.env.Environment;
    if (env.toLowerCase() !== 'prod' && env.toLowerCase() !== 'silo') {
        await switchIDPage.selectID(process.env.userID);
    }
});

Then('the user should be redirected to the dashboard', async ({ page }) => {
    await page.waitForLoadState();
    await expect(
        page.getByText('Welcome ' + process.env.advisorName).or(page.getByText('Hello, ' + process.env.advisorName))
    ).toBeVisible();
    //save auth state
    await page.context().storageState({ path: './authfiles/role1.json' });
});
