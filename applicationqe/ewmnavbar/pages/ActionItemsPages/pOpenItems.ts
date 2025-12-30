import { type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class OpenItemsPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smOpenItemsHL: Locator;
    readonly secOpenItems: Locator;
    readonly imgOpenItems: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        // Frame and Site definitions
        const iFrame = page.frameLocator('iframe[title="Open Items"]');
        const siteSelector = "#TrackingCenter";

        this.secIFrameContent = iFrame.locator(siteSelector);
        this.secSiteCore = iFrame.locator(siteSelector);
        this.secLegacySiteCore = page.locator(siteSelector);

        // Page Elements
        this.smOpenItemsHL = page.locator('a.active', { hasText: 'Open Items' });
        this.secOpenItems = page.getByTitle('Open Items');
        this.imgOpenItems = iFrame.getByAltText('Open Items');
    }

    async LoadsPage() {
        await this.fElement.elemHasAttribute(
            this.secOpenItems,
            'Open Items iframe',
            'src',
            /.*\/AccountsAnalysis\/TrackingCenter\/TrackingCenter\?status=open$/
        );

        await this.fElement.elemVisible(this.smOpenItemsHL, 'Open Items Highlight');
        await this.fElement.log('✅ Page loaded for Clients > Open Items');
    }
}