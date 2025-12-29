import { test as setup, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPageObjectModel';
import { SwitchIDPage } from '../pages/SwitchIDPageObjectModel';

setup('Login to Environment', async ({ page }) => {
    const role1AuthFile = './authfiles/role1.json';
    const loginPage = new LoginPage(page);
    const switchIDPage = new SwitchIDPage(page);
    //login
    await loginPage.gotoLoginPage();
    await loginPage.signIn(process.env.USERNAME, process.env.PASSWORD);
    //switch to correct id if using admin account
    if (process.env.userID) {
        await switchIDPage.selectID(process.env.userID);

    }
    await page.waitForLoadState();
    await expect(page.getByText('Welcome ' + process.env.advisorName)).toBeVisible();
    //save auth state
    await page.context().storageState({ path: role1AuthFile });
});