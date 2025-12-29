
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class MarketingResourcesPage {
    readonly page: Page;
    private logger: Logger;

    readonly smMarketingResourcesHL: Locator;
    readonly secMarketingResources: Locator;
    readonly imgMarketingResources: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Marketing Resources"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smMarketingResourcesHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Marketing Resources' });
        this.secMarketingResources = page.getByTitle('Marketing Resources');
        this.imgMarketingResources = iFrame.getByAltText('Marketing Resources');

    }

    async LoadsPage() {
        await this.logger((await this.secMarketingResources.getAttribute('src')).toString());

        await expect(this.secMarketingResources).toHaveAttribute(
            'src',
            /Marketing\/Marketing-Resource-Center\.aspx$/
        );
        await elemVisible(this.smMarketingResourcesHL, 'submenu Marketing Resources is Highlighted', this.logger);
        await this.logger('Page loaded for Help & Support > Marketing Resources');
    }
}
