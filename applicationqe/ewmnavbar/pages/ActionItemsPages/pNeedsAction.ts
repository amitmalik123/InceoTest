import { expect, type Locator, type Page } from "@playwright/test";
import { getImage } from '../../helper/getImage';
import { elemVisible, clickButton, typeinField, textExists, elemHasAttribute } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class NeedsActionPage {
    readonly page: Page;
    private logger: Logger;

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
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Needs Action"]');
        const site = "#TrackingCenter"

        this.secIFrameContent = iFrame.locator(site);
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);

        this.smNeedsActionHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Needs Action' });
        this.secNeedsAction = page.getByTitle('Needs Action');
        this.imgNeedsAction = iFrame.getByAltText('Needs Action');

        this.tblTable = iFrame.locator('#TrackingCenterGrid');
        this.tblRows = iFrame.locator('.advisor-response-required');
        // ui-widget-content jqgrow ui-row-ltr advisor-response-required

    }

    async LoadsPage() {
        const src = await this.secNeedsAction.getAttribute('src');
        this.logger && await this.logger(src ? src.toString() : 'src attribute not found');

        await elemHasAttribute(
            this.secNeedsAction,
            'Needs Action iframe',
            'src',
            /.*\/AccountsAnalysis\/TrackingCenter\/TrackingCenter\?status=open-Advisor$/,
            this.logger
        );
        
        await elemVisible(this.smNeedsActionHL, 'Needs Action Highlight', this.logger);
        this.logger && await this.logger('Page loaded for Clients > Needs Action');
    }

    async getItemsCount() {
        await elemVisible(this.tblTable.first(), 'Needs Action Table', this.logger);
        const rowCount = await this.tblRows.count();
        if (rowCount === 0) {
            this.logger && await this.logger('❌ Table row count is 0. Check page navigation and selector stability.');
            throw new Error("Table row count is 0. Check page navigation and selector stability.");
        }
        return rowCount;
    }

    async getTableRowCount() {
        const rowCount = await this.tblRows.count();
        return rowCount;
    }

    async getTableRowCountAlternative() {
        const rowsArray = await this.tblRows.all();
        const rowCount = rowsArray.length;
        return rowCount;
    }
}