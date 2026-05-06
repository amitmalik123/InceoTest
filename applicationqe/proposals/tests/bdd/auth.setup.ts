import { test as setup, expect } from '@playwright/test';
import { LoginPage } from '../../pages/LoginPageObjectModel';
import { SwitchIDPage } from '../../pages/SwitchIDPageObjectModel';
import { logger } from '../../utils/logger';

setup('Setup - Login to Environment', async ({ page }) => {
    logger.debug('\n=== Running BDD Setup: Logging in and saving auth state ===');
    const role1AuthFile = './authfiles/role1.json';
    const loginPage = new LoginPage(page);
    const switchIDPage = new SwitchIDPage(page);

    const env = process.env.ENVIRONMENT || process.env.Environment;
    // Login
    await loginPage.gotoLoginPage();
    await loginPage.signIn(process.env.USER, process.env.PASS);

    // Switch to correct ID if using admin account and not in prod
    
    if (process.env.userID && (env.toLowerCase() == 'test11' || env.toLowerCase() == 'test10')) {
        await switchIDPage.selectID(process.env.userID);
    }
    await page.goto(process.env.baseURL + '/en.aspx');
    await page.waitForLoadState();
    try {
        await expect(page.getByText(process.env.impersonationName)).toBeVisible();
    } catch (err) {
        logger.error('BDD setup: expected welcome text not visible', err);
        throw err;
    }
    // Save auth state
    await page.context().storageState({ path: role1AuthFile });
    logger.debug('\n===Setup Complete ===\n');
});
