import { LoginPage } from '@pages/LoginPageObjectModel';
import {test as baseTest, expect} from '@playwright/test';

type MyPages = {
    loginPage: LoginPage;
};

export const test = baseTest.extend<MyPages>({
    loginPage: async ({ page }, use) => {
        await use(new LoginPage(page));
    },
});



export { expect };