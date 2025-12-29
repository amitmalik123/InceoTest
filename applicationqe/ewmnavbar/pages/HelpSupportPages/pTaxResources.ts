
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class TaxResourcesPage {
    readonly page: Page;
    private logger: Logger;

    readonly smTaxResourcesHL: Locator;
    readonly secTaxResources: Locator;
    readonly imgTaxResources: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Tax Resources"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smTaxResourcesHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Tax Resources' });
        this.secTaxResources = page.getByTitle('Tax Resources');
        this.imgTaxResources = iFrame.getByAltText('Tax Resources');

    }

    async LoadsPage() {
        await this.logger((await this.secTaxResources.getAttribute('src')).toString());

        await expect(this.secTaxResources).toHaveAttribute(
            'src',
            /Administration\/Tax-Resources\/tax_center\.aspx$/
        );
        await elemVisible(this.smTaxResourcesHL, 'submenu Tax Resources is Highlighted', this.logger);
        await this.logger('Page loaded for Help & Support > Tax Resources');
    }
}