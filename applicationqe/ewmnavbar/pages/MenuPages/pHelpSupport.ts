import { type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class HelpSupportPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly hHelpSupport: Locator;
    
    // --- Sub Menus ---
    readonly smKnowledgeBase: Locator;
    readonly smContactUs: Locator;
    readonly smTaxResources: Locator;
    readonly smFees: Locator;
    readonly smGlossary: Locator;
    readonly smCustodialServices: Locator;
    readonly smComplianceResources: Locator;
    readonly smMarketingResources: Locator;
    readonly smEvents: Locator;
    readonly smRMDResources: Locator;
    
    // --- Buttons ---
    readonly btnChatWithUs: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        this.hHelpSupport = page.locator('h1[class*="pageHeader"]:has-text("Help & Support")');
        
        // Navigation Links
        // Note: If these become flaky, consider switching to 'href' selectors like we did in DashboardPage
        this.smKnowledgeBase = page.getByRole('link', { name: 'Knowledge Base', exact: true });
        this.smContactUs = page.getByRole('link', { name: 'Contact Us', exact: true });
        this.smTaxResources = page.getByRole('link', { name: 'Tax Resources', exact: true });
        this.smFees = page.getByRole('link', { name: 'Fees', exact: true });
        this.smGlossary = page.getByRole('link', { name: 'Glossary', exact: true });
        this.smCustodialServices = page.getByRole('link', { name: 'Custodial Services', exact: true });
        this.smComplianceResources = page.getByRole('link', { name: 'Compliance Resources', exact: true });
        this.smMarketingResources = page.getByRole('link', { name: 'Marketing Resources', exact: true });
        this.smEvents = page.getByRole('link', { name: 'Events', exact: true });
        this.smRMDResources = page.getByRole('link', { name: 'RMD Resources', exact: true });
        
        this.btnChatWithUs = page.locator('button', { hasText: 'Chat with Us' });
    }

    // ==========================================================
    // 🧭 Navigation
    // ==========================================================
    async goToPage() {
        await this.fBrowser.goToURL('/administration');
        await this.fElement.log('Navigating to Help & Support Page');
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.hHelpSupport, 'Help & Support Header');
        await this.fElement.log('✅ Landed on Page: Help & Support');
    }

    async SubMenusExist() {
        await this.fElement.log('📢 Verifying Help & Support Submenus...');
        
        await this.fElement.elemVisible(this.smKnowledgeBase, 'submenu Knowledge Base');
        await this.fElement.elemVisible(this.smContactUs, 'submenu Contact Us');
        await this.fElement.elemVisible(this.smTaxResources, 'submenu Tax Resources');
        await this.fElement.elemVisible(this.smFees, 'submenu Fees');
        await this.fElement.elemVisible(this.smGlossary, 'submenu Glossary');
        await this.fElement.elemVisible(this.smCustodialServices, 'submenu Custodial Services');
        await this.fElement.elemVisible(this.smComplianceResources, 'submenu Compliance Resources');
        await this.fElement.elemVisible(this.smMarketingResources, 'submenu Marketing Resources');
        await this.fElement.elemVisible(this.smEvents, 'submenu Events');
        await this.fElement.elemVisible(this.smRMDResources, 'submenu RMD Resources');
        
        await this.fElement.log('✅ All Help & Support submenus are visible.');
    }
}