import { type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class ClientsPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    // --- Header Elements ---
    readonly hClients: Locator;

    // --- Submenus ---
    readonly smAllClients: Locator;
    readonly smAccounts: Locator;
    readonly smStrategists: Locator;

    // --- Action Buttons ---
    readonly btnManageAccounts: Locator;
    readonly btnManageInvestorPortal: Locator;
    readonly btnAddAClient: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        this.hClients = page.locator('h1[class*="pageHeader"]:has-text("Clients")');

        this.smAllClients = page.getByRole('link', { name: 'All Clients' });
        this.smAccounts = page.getByRole('link', { name: 'Accounts', exact: true });
        this.smStrategists = page.getByRole('link', { name: 'Strategists' });

        this.btnManageAccounts = page.locator('button', { hasText: 'Manage Accounts' });
        this.btnManageInvestorPortal = page.locator('button', { hasText: 'View Investor Portal' });
        this.btnAddAClient = page.locator('button', { hasText: 'Add a Client' });
    }

    // ==========================================================
    // 🧭 Navigation
    // ==========================================================
    async goToPage() {
        await this.fBrowser.goToURL('/clients');
        await this.fElement.log('Navigating to Clients Page');
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.hClients, 'Clients Header');
        await this.fElement.log('✅ Landed on Page: Clients');
    }

    async SubMenusExist() {
        await this.fElement.elemVisible(this.smAllClients, 'submenu All Clients');
        await this.fElement.elemVisible(this.smAccounts, 'submenu Accounts');
        await this.fElement.elemVisible(this.smStrategists, 'submenu Strategists');
        await this.fElement.elemVisible(this.btnManageAccounts, 'button Manage Accounts');
    }
}