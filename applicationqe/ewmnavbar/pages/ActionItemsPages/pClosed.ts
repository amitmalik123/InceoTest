import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible, elemHasAttribute } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class ClosedPage {
    readonly page: Page;
    private logger: Logger;

    readonly smClosedHL: Locator;
    readonly secClosed: Locator;
    readonly imgClosed: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Closed"]');
        const site = "#TrackingCenter"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smClosedHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Closed' });
        this.secClosed = page.getByTitle('Closed');
        this.imgClosed = iFrame.getByAltText('Closed');

    }

    async LoadsPage() {
        const src = await this.secClosed.getAttribute('src');
        this.logger && await this.logger(src ? src.toString() : 'src attribute not found');

        await elemHasAttribute(
            this.secClosed,
            'Closed iframe',
            'src',
            /.*\/AccountsAnalysis\/TrackingCenter\/TrackingCenter\?status=closed$/,
            this.logger
        );

        await elemVisible(this.smClosedHL, 'Closed Highlight', this.logger);
        this.logger && await this.logger('Page loaded for Clients > Closed');
    }
}