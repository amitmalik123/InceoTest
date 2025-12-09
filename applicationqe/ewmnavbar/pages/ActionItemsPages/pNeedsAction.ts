import { expect, type Locator, type Page } from "@playwright/test";
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
        await this.logger((await this.secNeedsAction.getAttribute('src')).toString());

        await expect(this.secNeedsAction).toHaveAttribute(
            'src',
            /AccountsAnalysis\/TrackingCenter\/TrackingCenter?status=open-Advisor$/
        );
        await expect(this.smNeedsActionHL).toBeVisible();
        await this.logger('Page loaded for Clients > Needs Action');
    }

    async getItemsCount() {
        await this.tblTable.first().waitFor({ state: 'visible' });
        const rowCount = await this.tblRows.count();
        if (rowCount === 0) {
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