
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible, waitForElem } from '../../functions/fElementHelper';
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
        this.btnManageAccounts = page.locator('button', { hasText: 'Manage Accounts' });

        // this.btnManageInvestorPortal = page.locator('button', { hasText: 'View Investor Portal' });
        // this.btnAddAClient = page.locator('button', { hasText: 'Add a Client' });
    }

    async goToPage() {
        await this.page.goto('/clients');
    }

    async LoadsPage() {
        await waitForElem(this.hClients, 'Clients Header', this.logger);
        console.log('on Page Clients');
    }

    async SubMenusExist() {
        await waitForElem(this.smAllClients, 'submenu All Clients', this.logger);
        // await elemVisible(this.smAccounts, 'submenu Accounts', this.logger);
        await elemVisible(this.smStrategists, 'submenu Strategists', this.logger);
        await elemVisible(this.btnManageAccounts, 'button Manage Accounts', this.logger);
        // await elemVisible(this.btnManageInvestorPortal, 'button Manage Investor Portal', this.logger);
        // await elemVisible(this.btnAddAClient, 'button Add a Client', this.logger);
    }

}
