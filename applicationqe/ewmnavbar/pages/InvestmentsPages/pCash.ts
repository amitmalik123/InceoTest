
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class CashPage {
    readonly page: Page;
    private logger: Logger;

    readonly smCashHL: Locator;
    readonly secCash: Locator;
    readonly txtManagement: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Cash"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smCashHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Cash' });
        this.secCash = page.getByTitle('Cash');
        this.txtManagement = page.getByText('At AssetMark, we understand the importance of optimizing cash management for your clients.');
    }

  
    async LoadsPage() {
        await this.logger((await this.secCash.getAttribute('src')).toString());

        await expect(this.secCash).toHaveAttribute(
            'src',
            /Investments\/Cash-Solutions\.aspx$/
        );
        await this.logger((await this.secCash.getAttribute('src')).toString());
        await elemVisible(this.smCashHL, 'submenu Cash is Highlighted', this.logger);
        await this.logger('Page loaded for Investments > Cash');
    }
}