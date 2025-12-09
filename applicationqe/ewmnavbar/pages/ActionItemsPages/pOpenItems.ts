import { expect, type Locator, type Page } from "@playwright/test";
type Logger = (msg: string) => Promise<void>;

export class OpenItemsPage {
    readonly page: Page;
    private logger: Logger;

    readonly smOpenItemsHL: Locator;
    readonly secOpenItems: Locator;
    readonly imgOpenItems: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Open Items"]');
        const site = "#TrackingCenter"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smOpenItemsHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Open Items' });
        this.secOpenItems = page.getByTitle('Open Items');
        this.imgOpenItems = iFrame.getByAltText('Open Items');

    }

    async LoadsPage() {
        await this.logger((await this.secOpenItems.getAttribute('src')).toString());

        await expect(this.secOpenItems).toHaveAttribute(
            'src',
            /AccountsAnalysis\/TrackingCenter\/TrackingCenter?status=open$/
        );
        await expect(this.smOpenItemsHL).toBeVisible();
        await this.logger('Page loaded for Clients > Open Items');
    }
}