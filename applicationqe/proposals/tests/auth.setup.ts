import { test as setup, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPageObjectModel';
import { SwitchIDPage } from '../pages/SwitchIDPageObjectModel';
import { logger } from '../utils/logger';

setup('Login to Environment', async ({ page }) => {
    logger.debug('\n=== Running Setup: Logging in and saving auth state ===');
    const role1AuthFile = './authfiles/role1.json';
    const loginPage = new LoginPage(page);
    const switchIDPage = new SwitchIDPage(page);
    //login
    await loginPage.gotoLoginPage();
    await loginPage.signIn(process.env.USER, process.env.PASS);
    //switch to correct id if using admin account
    if (process.env.userID && (process.env.ENVIRONMENT || process.env.Environment).toLowerCase() !== 'prod') {
        await switchIDPage.selectID(process.env.userID);
    }
    await page.waitForLoadState();
    try {
        await expect(page.getByText('Welcome ' + process.env.advisorName)).toBeVisible();
    } catch (err) {
        logger.error('Login setup: expected welcome text not visible', err);
        throw err;
    }
    //save auth state
    await page.context().storageState({ path: role1AuthFile });
});
