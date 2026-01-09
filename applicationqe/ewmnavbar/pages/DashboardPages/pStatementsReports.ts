import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class StatementsReportsPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    // --- Navigation ---
    readonly smStatementsReportsHL: Locator;

    // --- iFrame & Comparison Locators ---
    readonly secStatementsReports: Locator; 
    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;       
    readonly secLegacySiteCore: Locator; 

    // --- Controls (Inside iFrame) ---
    readonly ddlType: Locator;
    readonly ddlYear: Locator;
    readonly ddlDocument: Locator;
    readonly ddlQuarter: Locator;
    readonly btnFind: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        // Definitions
        const iFrameSelector = 'iframe[title="Documents"]';
        const contentSelector = ".grid-system.g982";

        // Contexts
        const iFrameContext = page.frameLocator(iFrameSelector);

        // Navigation
        this.smStatementsReportsHL =page.locator('a.active',{ hasText: 'Statements & Reports' });
        
        // Main Sections
        this.secStatementsReports = page.getByTitle('Documents');
        this.secIFrameContent = iFrameContext.locator('#sitecore-content');
        this.secSiteCore = iFrameContext.locator(contentSelector);
        
        // Legacy
        this.secLegacySiteCore = page.locator(contentSelector);

        // Controls
        this.ddlType = iFrameContext.locator('#uniform-ddYear'); 
        this.ddlYear = iFrameContext.locator('#uniform-ddYear');
        this.ddlDocument = iFrameContext.locator('#uniform-ddDocument');
        this.ddlQuarter = iFrameContext.locator('#uniform-ddQtrMonth');
        this.btnFind = iFrameContext.locator('#btSearch');
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        // Wait for highlight first to confirm navigation
        await this.fElement.waitForElemVisible(this.smStatementsReportsHL, 'Statements & Reports Highlight');

        const src = await this.secStatementsReports.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secStatementsReports).toHaveAttribute(
            'src',
            /Administration\/statements-and-correspondence\.aspx$/
        );

        await this.fElement.log('✅ Landed on Page: Dashboard > Statements & Reports');
    }

    async ElementsExist() {
        await this.fElement.log('📢 Verifying Statements & Reports Controls...');
        await this.fElement.elemVisible(this.ddlType, 'Type Dropdown');
        await this.fElement.elemVisible(this.ddlDocument, 'Document Dropdown');
        await this.fElement.elemVisible(this.ddlQuarter, 'Quarter Dropdown');
        await this.fElement.elemVisible(this.btnFind, 'Find Button');
        
        await this.fElement.log('✅ All Statements & Reports controls are visible.');
    }
}