import { type Locator, type Page } from '@playwright/test';

export class LoginPage {
    readonly page: Page;
    readonly usernameInput: Locator;
    readonly passwordInput: Locator;
    readonly signInButton: Locator;

    constructor(page: Page) {
    this.page = page;
    this.usernameInput = page.getByRole('textbox', { name: 'Username' });
    this.passwordInput = page.getByRole('textbox', { name: 'Password' });
    this.signInButton = page.getByRole('button', { name: 'SIGN IN' });
    }

    // Navigate to login page
    async gotoLoginPage() {
        await this.page.goto(process.env.loginURL);
        await this.page.waitForLoadState('networkidle');
    }

    //Sign in with given username and password
    async signIn(username: string, password: string) {
        if(await this.page.getByRole('button', { name: 'Confirm My Choices' }).isVisible()){
            await this.page.getByRole('button', { name: 'Confirm My Choices' }).click();
        }
        await this.usernameInput.fill(username);
        await this.passwordInput.fill(password);
        await this.signInButton.click();
        await this.page.waitForLoadState('networkidle');
    }

    //Select role after login with Admin account
    async selectRole(roleId: string) {
        if(await this.page.locator(`#radRoles_${roleId}`).isVisible()){
            await this.page.locator(`#radRoles_${roleId}`).check();
            await this.page.getByRole('button', { name: 'Continue' }).click();
        }
        await this.page.waitForLoadState('networkidle');
    }

    //Switch ID to advisor
    async selectID(advisorId: string, advisorName: string) {
        await this.page.getByRole('link', { name: 'Switch ID' }).click();
        await this.page.locator('#ctl00_cphContentArea_txtLookUp').click();
        await this.page.locator('#ctl00_cphContentArea_txtLookUp').fill(advisorId);
        await this.page.locator('#ctl00_cphContentArea_txtLookUp').press('Enter');
        await this.page.waitForLoadState('networkidle');
        await this.page.getByRole('link', { name: advisorName }).click();
        await this.page.waitForLoadState('networkidle');
        if(await this.page.locator('#radAgents').isVisible()){
            await this.page.locator('#radAgents').click();
            await this.page.getByRole('button', { name: 'Continue' }).click();
        }
        await this.page.waitForLoadState('networkidle');
    }
}