import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class NewsPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smNewsHL: Locator;
    readonly secNews: Locator;
    readonly mHeader: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        const iFrameSelector = 'iframe[title="News"]';
        const contentSelector = "#sitecore-content";
        const iFrameContext = page.frameLocator(iFrameSelector);

        this.smNewsHL = page.locator('a.active',{ hasText: 'News' });
        this.secNews = page.getByTitle('News');
        this.mHeader = page.locator('#header_0_content_3_divTertiaryWrapper');

        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smNewsHL, 'submenu News (Highlighted)');

        const src = await this.secNews.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secNews).toHaveAttribute(
            'src',
            /Investments\/Overview\/Whats-New\.aspx$/
        );
        
        await this.fElement.log('✅ Landed on Page: Investments > News');
    }
}