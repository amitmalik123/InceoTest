import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class MarketingResourcesPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smMarketingResourcesHL: Locator;
    readonly secMarketingResources: Locator;
    readonly imgMarketingResources: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="Marketing Resources"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smMarketingResourcesHL = page.locator('a.active',{ hasText: 'Marketing Resources' });
        this.secMarketingResources = page.getByTitle('Marketing Resources');
        this.imgMarketingResources = iFrameContext.getByAltText('Marketing Resources');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smMarketingResourcesHL, 'submenu Marketing Resources (Highlighted)');

        const src = await this.secMarketingResources.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secMarketingResources).toHaveAttribute(
            'src',
            /Marketing\/Marketing-Resource-Center\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Help & Support > Marketing Resources');
    }
}