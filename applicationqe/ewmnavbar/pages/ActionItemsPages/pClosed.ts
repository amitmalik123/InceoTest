import { type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class ClosedPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smClosedHL: Locator;
    readonly secClosed: Locator;
    readonly imgClosed: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        // Frame and Site definitions
        const iFrame = page.frameLocator('iframe[title="Closed"]');
        const siteSelector = "#TrackingCenter";

        this.secIFrameContent = iFrame.locator(siteSelector);
        this.secSiteCore = iFrame.locator(siteSelector);
        this.secLegacySiteCore = page.locator(siteSelector);

        this.smClosedHL = page.locator('a.active', { hasText: 'Closed' });
        this.secClosed = page.getByTitle('Closed');
        this.imgClosed = iFrame.getByAltText('Closed');
    }

    async LoadsPage() {
        await this.fElement.elemHasAttribute(
            this.secClosed,
            'Closed iframe',
            'src',
            /.*\/AccountsAnalysis\/TrackingCenter\/TrackingCenter\?status=closed$/
        );

        await this.fElement.elemVisible(this.smClosedHL, 'Closed Highlight');
        await this.fElement.log('✅ Page loaded for Clients > Closed');
    }
}