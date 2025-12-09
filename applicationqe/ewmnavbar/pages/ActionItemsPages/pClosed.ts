import { expect, type Locator, type Page } from "@playwright/test";
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
        await this.logger((await this.secClosed.getAttribute('src')).toString());

        await expect(this.secClosed).toHaveAttribute(
            'src',
            /AccountsAnalysis\/TrackingCenter\/TrackingCenter?status=closed$/
        );
        await expect(this.smClosedHL).toBeVisible();
        await this.logger('Page loaded for Clients > Closed');
    }
}