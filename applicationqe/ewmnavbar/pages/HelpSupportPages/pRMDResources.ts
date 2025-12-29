
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class RMDResourcesPage {
    readonly page: Page;
    private logger: Logger;

    readonly smRMDResourcesHL: Locator;
    readonly secRMDResources: Locator;
    readonly imgRMDResources: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="RMD Resources"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smRMDResourcesHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'RMD Resources' });
        this.secRMDResources = page.getByTitle('RMD Resources');
        this.imgRMDResources = iFrame.getByAltText('RMD Resources');

    }

    async LoadsPage() {
        await this.logger((await this.secRMDResources.getAttribute('src')).toString());

        await expect(this.secRMDResources).toHaveAttribute(
            'src',
            /Administration\/Tax-Resources\/rmd_center\.aspx$/
        );
        await elemVisible(this.smRMDResourcesHL, 'submenu RMD Resources is Highlighted', this.logger);
        await this.logger('Page loaded for Help & Support > RMD Resources');
    }
}