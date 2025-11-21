require('dotenv').config({ path: './env/.env.test10' });

import {test as setup, expect} from '@playwright/test';
import { LoginPage } from '@pages/LoginPageObjectModel';

setup('Login to Environment', async ({ page }) => {
    const role1AuthFile= './authfiles/role1.json';
    console.log('loginURL:', process.env.loginURL);
    //login
    const loginPage = new LoginPage(page);
    await loginPage.gotoLoginPage();
    await loginPage.signIn(process.env.USERNAME, process.env.PASSWORD);
    //select role, if using admin account
    await loginPage.selectRole(process.env.userRole);
    //switch to correct id
    await loginPage.selectID(process.env.userID, process.env.advisorID);
    await expect(page.getByText('Welcome ' + process.env.advisorName)).toBeVisible();
    //save auth state
    await page.context().storageState({ path: role1AuthFile });
});