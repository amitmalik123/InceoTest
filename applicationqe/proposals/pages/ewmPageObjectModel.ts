import { Page, Locator } from '@playwright/test';

export class EwmPage {
    readonly page: Page;
    
    // Navigation Links
    readonly logoutLink: Locator;
    
    // Login Page Elements
    readonly usernameTextbox: Locator;
    
    constructor(page: Page) {
        this.page = page;
        
        // Navigation Links
        this.logoutLink = page.getByRole('link', { name: 'Logout' });
        
        // Login Page Elements
        this.usernameTextbox = page.getByRole('textbox', { name: 'Username' });
    }

    /**
     * Performs logout operation and waits for redirect to login page
     */
    async logout(): Promise<void> {
        await this.logoutLink.click();
        await this.page.waitForLoadState('networkidle');
    }
}
