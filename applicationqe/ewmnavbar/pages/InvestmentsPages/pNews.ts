import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class NewsPage {
    readonly page: Page;
    private logger: Logger;

    readonly smNewsHL: Locator;
    readonly secNews: Locator;
    readonly mHeader: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="News"]');
        const site = "#sitecore-content"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smNewsHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'News' });
        this.secNews = page.getByTitle('News');
        this.mHeader = page.locator('#header_0_content_3_divTertiaryWrapper');
    }

    async LoadsPage() {
        await this.logger((await this.secNews.getAttribute('src')).toString());

        await expect(this.secNews).toHaveAttribute(
            'src',
            /Investments\/Overview\/Whats-New\.aspx$/
        );
        await this.logger((await this.secNews.getAttribute('src')).toString());
        await expect(this.smNewsHL).toBeVisible();
        await this.logger('Page loaded for Investments > News');
    }
}