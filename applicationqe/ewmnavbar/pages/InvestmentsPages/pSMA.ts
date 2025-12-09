import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class SMAPage {
    readonly page: Page;
    private logger: Logger;

    readonly smSMAHL: Locator;
    readonly secSMA: Locator;
    readonly txtManagement: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;


    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="SMA"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smSMAHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'SMA' });
        this.secSMA = page.getByTitle('SMA');
        this.txtManagement = page.getByText('Clients look to you to help reach their unique financial goals. Now you have access to a curated suite of professionally managed SMAs on the AssetMark platform, designed to help tailor clients');
    }

    async LoadsPage() {
        await this.logger((await this.secSMA.getAttribute('src')).toString());

        await expect(this.secSMA).toHaveAttribute(
            'src',
            /Investments\/SMA\.aspx$/
        );
        await this.logger((await this.secSMA.getAttribute('src')).toString());
        await expect(this.smSMAHL).toBeVisible();
        await this.logger('Page loaded for Investments > SMA');
    }
}