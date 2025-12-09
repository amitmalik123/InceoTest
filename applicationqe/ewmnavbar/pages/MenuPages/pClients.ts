import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class ClientsPage {
    readonly page: Page;
    private logger: Logger;

    readonly hClients: Locator;
    readonly smAllClients: Locator;
    readonly smAccounts: Locator;
    readonly smStrategists: Locator;
    readonly btnManageInvestorPortal: Locator;
    readonly btnManageAccounts: Locator;
    readonly btnAddAClient: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        this.hClients = page.locator('h1[class*="pageHeader"]:has-text("Clients")');
        this.smAllClients = page.getByRole('link', { name: 'All Clients' });
        this.smAccounts = page.getByRole('link', { name: 'Accounts' });
        this.smStrategists = page.getByRole('link', { name: 'Strategists' });
        this.btnManageInvestorPortal = page.locator('button', { hasText: 'View Investor Portal' });
        this.btnManageAccounts = page.locator('button', { hasText: 'Manage Accounts' });
        this.btnAddAClient = page.locator('button', { hasText: 'Add a Client' });
    }

    async goToPage() {
        await this.page.goto('/clients');
    }

    async LoadsPage() {
        await expect(this.hClients).toBeVisible({ timeout: 1000000 });
        console.log('on Page Clients');
    }

    async SubMenusExist() {
        await expect(this.smAllClients).toBeVisible();
        await expect(this.smAccounts).toBeVisible();
        await expect(this.smStrategists).toBeVisible();
        await expect(this.btnManageInvestorPortal).toBeVisible();
        await expect(this.btnManageAccounts).toBeVisible();
        await expect(this.btnAddAClient).toBeVisible();
    }

}
