import { test as setup, expect } from '@playwright/test';
import { LoginPage } from '../../pages/LoginPageObjectModel';
import { SwitchIDPage } from '../../pages/SwitchIDPageObjectModel';

setup('Setup - Login to Environment', async ({ page }) => {
    console.log('\n=== Running BDD Setup: Logging in and saving auth state ===');
    const role1AuthFile = './authfiles/role1.json';
    const loginPage = new LoginPage(page);
    const switchIDPage = new SwitchIDPage(page);

    // Login
    await loginPage.gotoLoginPage();
    await loginPage.signIn(process.env.USER, process.env.PASS);

    // Switch to correct ID if using admin account
    if (process.env.userID) {
        await switchIDPage.selectID(process.env.userID);
    }

    await page.waitForLoadState();
    await expect(page.getByText('Welcome ' + process.env.advisorName)).toBeVisible();

    // Save auth state
    await page.context().storageState({ path: role1AuthFile });
    console.log('\n===Setup Complete ===\n');
});
