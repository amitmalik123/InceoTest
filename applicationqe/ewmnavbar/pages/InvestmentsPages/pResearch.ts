
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class ResearchPage {
    readonly page: Page;
    private logger: Logger;

    readonly smResearch: Locator;
    readonly secResearch: Locator;
    readonly ddlFilter: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;
        this.smResearch = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Research' });
        this.secResearch = page.getByTitle('Research');
        this.ddlFilter = page.locator('.filter-search-searchbox');

        const iFrame = page.frameLocator('iframe[title="Research"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);
    }

    async LoadsPage() {
        await expect(this.secResearch).toHaveAttribute(
            'src',
            /Investments\/Research\.aspx$/
        );
        await this.logger((await this.secResearch.getAttribute('src')).toString());
        await elemVisible(this.smResearch, 'submenu Research is Highlighted', this.logger);
        await this.logger('Page loaded for Investments > Research');
    }
}