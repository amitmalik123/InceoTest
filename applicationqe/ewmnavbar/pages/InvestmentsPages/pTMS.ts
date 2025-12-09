import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class TMSPage {
    readonly page: Page;
    private logger: Logger;

    readonly smTMSHL: Locator;
    readonly secTMS: Locator;
    readonly txtWhatTMS: Locator;
    readonly imgTAX: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;


    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="TMS"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smTMSHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'TMS' });
        this.secTMS = page.getByTitle('TMS');
        this.txtWhatTMS = page.getByText('AssetMark\'s Tax Management Services (TMS)');
        this.imgTAX = page.getByAltText('Tax Savings Report');
    }
    

   async LoadsPage() {
        await this.logger((await this.secTMS.getAttribute('src')).toString());

        await expect(this.secTMS).toHaveAttribute(
            'src',
            /Investments\/TMS\.aspx$/
        );
        await this.logger((await this.secTMS.getAttribute('src')).toString());
        await expect(this.smTMSHL).toBeVisible();
        await this.logger('Page loaded for Investments > TMS');
    }
}