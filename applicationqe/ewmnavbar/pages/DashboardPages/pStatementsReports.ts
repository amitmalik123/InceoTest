
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';
type Logger = (msg: string) => Promise<void>;

export class StatementsReportsPage {
    readonly page: Page;
    private logger: Logger;

    readonly smStatementsReportsHL: Locator;
    readonly secStatementsReports: Locator;

    readonly ddlType: Locator;
    readonly ddlYear: Locator;
    readonly ddlDocument: Locator;
    readonly ddlQuarter: Locator;
    readonly btnFind: Locator;

    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;
    readonly secLegacySiteCore: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.logger = logger;

        const iFrame = page.frameLocator('iframe[title="Documents"]');
        const site = ".grid-system.g982" 

        this.secIFrameContent = iFrame.locator('#sitecore-content');
        this.secSiteCore = iFrame.locator(site);
        this.secLegacySiteCore = page.locator(site);


        this.smStatementsReportsHL = page.locator('[class="active"][aria-current="page"]').filter({ hasText: 'Statements & Reports' });
        this.secStatementsReports = page.getByTitle('Documents');

        this.ddlType = iFrame.locator('#uniform-ddYear');
        this.ddlYear = iFrame.locator('#uniform-ddYear');
        this.ddlDocument = iFrame.locator('#uniform-ddDocument');
        this.ddlQuarter = iFrame.locator('#uniform-ddQtrMonth');
        this.btnFind = iFrame.locator('#btSearch');

    }


    async LoadsPage() {
        await elemVisible(this.smStatementsReportsHL, 'submenu Statements & Reports is Highlighted', this.logger, 10000);
        await expect(this.secStatementsReports).toHaveAttribute(
            'src',
            /Administration\/statements-and-correspondence\.aspx$/
        );
        console.log('Page loaded for Dashboard > Statements & Reports');
    }

    async ElementsExist() {
        await elemVisible(this.ddlType, 'Type Dropdown', this.logger, 1000);
        await elemVisible(this.smStatementsReportsHL, 'Statements & Reports', this.logger, 100);
        await elemVisible(this.ddlDocument, 'Document Dropdown', this.logger, 100);
        await elemVisible(this.ddlQuarter, 'Quarter Dropdown', this.logger, 100);
        await elemVisible(this.btnFind, 'Find Button', this.logger, 100);
        await this.logger('Page loaded for Dashboard > Statements & Reports');
    }
}