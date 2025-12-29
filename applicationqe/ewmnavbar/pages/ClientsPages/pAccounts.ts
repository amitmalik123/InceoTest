import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class AccountsPage {
    readonly page: Page;
    private logger: Logger;

    readonly smAccountsHL: Locator;
    readonly secAccounts: Locator;
    readonly imgAccounts: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Accounts"]');
        const site = "#AccountList"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smAccountsHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Accounts' });
        this.secAccounts = page.getByTitle('Accounts');
        this.imgAccounts = iFrame.getByAltText('Accounts');

    }

    async LoadsPage() {
        await this.logger((await this.secAccounts.getAttribute('src')).toString());

        await expect(this.secAccounts).toHaveAttribute(
            'src',
            /AccountsAnalysis\/Clients\/AccountList$/
        );
        await elemVisible(this.smAccountsHL, 'submenu Accounts is Highlighted', this.logger);
        await this.logger('Page loaded for Clients > Accounts');
    }
}