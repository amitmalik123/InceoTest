import { Page, Locator } from '@playwright/test';

export class EwmPage {
    readonly page: Page;

    // Navigation Links
    readonly logoutLink: Locator;
    readonly accountWizardLink: Locator;
    readonly clientsLink: Locator;
    readonly createNewClient: Locator;

    // Login Page Elements
    readonly usernameTextbox: Locator;

    constructor(page: Page) {
        this.page = page;

        // Navigation Links
        this.logoutLink = page.getByRole('link', { name: 'Logout' });
        this.accountWizardLink = page.getByRole('link', { name: 'Account Wizard' });
        this.clientsLink = page.getByRole('link', { name: 'Clients' });

        // Login Page Elements
        this.usernameTextbox = page.getByRole('textbox', { name: 'Username' });

        //Client Page Elements
        this.createNewClient = page.getByRole('button', { name: 'Go' }).first();
    }

    /**
     * Performs logout operation and waits for redirect to login page
     */
    async logout(): Promise<void> {
        await this.logoutLink.click();
        await this.usernameTextbox.waitFor({ state: 'visible' });
    }

    /**
     * Clicks the Account Wizard navigation link
     */
    async openAccountWizard(): Promise<void> {
        await this.accountWizardLink.click();
    }
}
