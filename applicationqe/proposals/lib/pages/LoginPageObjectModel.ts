import { type Locator, type Page } from '@playwright/test';

export class LoginPage {
    readonly page: Page;
    readonly usernameInput: Locator;
    readonly passwordInput: Locator;
    readonly signInButton: Locator;
    readonly cookieAcceptButton: Locator;
    readonly privacyPolicyButton: Locator;

    constructor(page: Page) {
        this.page = page;
        this.usernameInput = page.getByRole('textbox', { name: 'Username' });
        this.passwordInput = page.getByRole('textbox', { name: 'Password' });
        this.signInButton = page.getByRole('button', { name: 'SIGN IN' });
        this.cookieAcceptButton = page.getByRole('button', { name: 'Confirm My Choices' });
        this.privacyPolicyButton = page.getByRole('button', { name: 'I Agree' });
    }

    // Navigate to login page
    async gotoLoginPage() {
        await this.page.goto(process.env.loginURL);
        await this.page.waitForLoadState('networkidle');
    }

    //Sign in with given username and password
    async signIn(username: string, password: string) {
        if (await this.cookieAcceptButton.isVisible()) {
            await this.cookieAcceptButton.click();
        }
        await this.usernameInput.fill(username);
        await this.passwordInput.fill(password);
        await this.signInButton.click();
        await this.page.waitForLoadState('networkidle');
    }


}