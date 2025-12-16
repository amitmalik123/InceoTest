import { test as setup, expect } from '@playwright/test';
import { LoginPage } from '@pages/LoginPageObjectModel';
import { SwitchIDPage } from '@pages/SwitchIDPageObjectModel';

setup('Login to Environment', async ({ page }) => {
    const role1AuthFile = './authfiles/role1.json';
    const loginPage = new LoginPage(page);
    const switchIDPage = new SwitchIDPage(page);
    //login
    await loginPage.gotoLoginPage();
    await loginPage.signIn(process.env.USERNAME, process.env.PASSWORD);
    await page.waitForLoadState();
    //Accept privacy policy if prompted or go into id selection
    await expect(loginPage.privacyPolicyButton.or(switchIDPage.switchIDLink)).toBeVisible({ timeout: 10_000 });
    if (await loginPage.privacyPolicyButton.isVisible()) {
        await loginPage.privacyPolicyButton.click();
    } else if (await switchIDPage.switchIDLink.isVisible()) {
        await switchIDPage.switchIDLink.click();
    }
    await page.waitForLoadState();
    //switch to correct id
    await switchIDPage.selectID(process.env.userID);
    await expect(page.getByText('Welcome ' + process.env.advisorName)).toBeVisible();
    //save auth state
    await page.context().storageState({ path: role1AuthFile });
});