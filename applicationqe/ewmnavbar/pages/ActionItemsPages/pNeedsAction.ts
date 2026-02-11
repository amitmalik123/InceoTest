import { type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class NeedsActionPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly smNeedsActionHL: Locator;
    readonly secNeedsAction: Locator;
    readonly imgNeedsAction: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    readonly tblTable: Locator;
    readonly tblRows: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        // Frame and Site definitions
        const iFrame = page.frameLocator('iframe[title="Needs Action"]');
        const siteSelector = "#TrackingCenter";

        this.secIFrameContent = iFrame.locator(siteSelector);
        this.secSiteCore = iFrame.locator(siteSelector);
        this.secLegacySiteCore = page.locator(siteSelector);

        // Header Elements
        this.smNeedsActionHL = page.locator('a.active', { hasText: 'Needs Action' }); 
        this.secNeedsAction = page.getByTitle('Needs Action');
        this.imgNeedsAction = iFrame.getByAltText('Needs Action');

        // Table Elements
        this.tblTable = iFrame.locator('#TrackingCenterGrid');
        this.tblRows = iFrame.locator('.advisor-response-required');
    }

    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smNeedsActionHL, 'submenu Needs Action Highlighted');
        await this.fElement.elemHasAttribute(
            this.secNeedsAction,
            'Needs Action iframe',
            'src',
            /.*\/AccountsAnalysis\/TrackingCenter\/TrackingCenter\?status=open-Advisor$/
        );

        await this.fElement.log('✅ Page loaded for Clients > Needs Action');
    }

    async getItemsCount() {
        await this.fElement.elemVisible(this.tblTable.first(), 'Needs Action Table');

        const rowCount = await this.tblRows.count();
        if (rowCount === 0) {
            const msg = '❌ Table row count is 0. Check page navigation and selector stability.';
            await this.fElement.log(msg);
            throw new Error(msg);
        }

        await this.fElement.log(`ℹ️ Found ${rowCount} items in Needs Action table`);
        return rowCount;
    }

    async getTableRowCount() {
        return await this.tblRows.count();
    }
}