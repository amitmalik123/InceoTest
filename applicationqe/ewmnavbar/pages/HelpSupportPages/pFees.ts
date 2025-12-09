import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class FeesPage {
    readonly page: Page;
    private logger: Logger;

    readonly smFeesHL: Locator;
    readonly secFees: Locator;
    readonly imgFees: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Fees"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smFeesHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Fees' });
        this.secFees = page.getByTitle('Fees');
        this.imgFees = iFrame.getByAltText('Fees');

    }

    async LoadsPage() {
        await this.logger((await this.secFees.getAttribute('src')).toString());

        await expect(this.secFees).toHaveAttribute(
            'src',
            /Administration\/advisor-fee-payments\.aspx$/
        );
        await expect(this.smFeesHL).toBeVisible();
        await this.logger('Page loaded for Help & Support > Fees');
    }
}