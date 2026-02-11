import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class AccountsPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    // --- Navigation ---
    readonly smAccountsHL: Locator;

    // --- iFrame & Content ---
    readonly secAccounts: Locator;
    readonly imgAccounts: Locator;

    // --- Comparison Locators ---
    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        // Definitions
        const iFrameSelector = 'iframe[title="Accounts"]';
        const contentSelector = "#AccountList";

        // Contexts
        const iFrameContext = page.frameLocator(iFrameSelector);

        // Locators
        this.smAccountsHL = page.locator('a.active', { hasText: 'Accounts' });

        this.secAccounts = page.getByTitle('Accounts');
        this.imgAccounts = iFrameContext.getByAltText('Accounts');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        const src = await this.secAccounts.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secAccounts).toHaveAttribute(
            'src',
            /AccountsAnalysis\/Clients\/AccountList$/
        );

        await this.fElement.elemVisible(this.smAccountsHL, 'submenu Accounts (Highlighted)');
        await this.fElement.log('✅ Landed on Page: Clients > Accounts');
    }
}