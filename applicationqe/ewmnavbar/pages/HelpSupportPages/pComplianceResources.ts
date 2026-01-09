import { expect, type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class ComplianceResourcesPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    // --- Navigation ---
    readonly smComplianceResourcesHL: Locator;

    // --- iFrame & Content ---
    readonly secComplianceResources: Locator; 
    readonly imgComplianceResources: Locator; 

    // --- Comparison Locators ---
    readonly secIFrameContent: Locator;
    readonly secSiteCore: Locator;       
    readonly secLegacySiteCore: Locator; 

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        // Definitions
        const iFrameSelector = 'iframe[title="Compliance Resources"]';
        const contentSelector = "#sitecore-content";

        // Contexts
        const iFrameContext = page.frameLocator(iFrameSelector);

        // Navigation
        this.smComplianceResourcesHL = page.locator('a.active',{ hasText: 'Compliance Resources' });
        
        // Main Sections
        this.secComplianceResources = page.getByTitle('Compliance Resources');
        this.imgComplianceResources = iFrameContext.getByAltText('Compliance Resources');

        // Content
        this.secIFrameContent = iFrameContext.locator(contentSelector);
        this.secSiteCore = iFrameContext.locator(contentSelector);
        
        // Legacy
        this.secLegacySiteCore = page.locator(contentSelector);
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.smComplianceResourcesHL, 'submenu Compliance Resources (Highlighted)');

        const src = await this.secComplianceResources.getAttribute('src');
        await this.fElement.log(`ℹ️ iFrame Source: ${src}`);

        await expect(this.secComplianceResources).toHaveAttribute(
            'src',
            /Administration\/compliance-resources\/compliance-resources\.aspx$/
        );

        await this.fElement.elemVisible(this.smComplianceResourcesHL, 'submenu Compliance Resources (Highlighted)');
        await this.fElement.log('✅ Landed on Page: Help & Support > Compliance Resources');
    }
}