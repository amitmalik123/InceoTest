
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';

export class HelpSupportPage {
    readonly page: Page;
    readonly hHelpSupport: Locator;
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
    readonly btnChatWithUs: Locator;
    // readonly smOne: Locator;

    constructor(page: Page) {
        this.page = page;
        this.hHelpSupport = page.locator('h1[class*="pageHeader"]:has-text("Help & Support")');
        this.smKnowledgeBase = page.getByRole('link', { name: 'Knowledge Base' });
        this.smContactUs = page.getByRole('link', { name: 'Contact Us' });
        this.smTaxResources = page.getByRole('link', { name: 'Tax Resources' });
        this.smFees = page.getByRole('link', { name: 'Fees' });
        this.smGlossary = page.getByRole('link', { name: 'Glossary' });
        this.smCustodialServices = page.getByRole('link', { name: 'Custodial Services' });
        this.smComplianceResources = page.getByRole('link', { name: 'Compliance Resources' });
        this.smMarketingResources = page.getByRole('link', { name: 'Marketing Resources' });
        this.smEvents = page.getByRole('link', { name: 'Events' });
        this.smRMDResources = page.getByRole('link', { name: 'RMD Resources' });
        this.btnChatWithUs = page.locator('button', { hasText: 'Chat with Us' });

    }

    async LoadsPage() {
        await elemVisible(this.hHelpSupport, 'Help & Support Header', undefined, 1000000);
        console.log('on Page Help and Support');
    }

    async goToPage(){
        await this.page.goto('/administration');
    }

    async SubMenusExist() {
        await elemVisible(this.smKnowledgeBase, 'submenu Knowledge Base');
        await elemVisible(this.smContactUs, 'submenu Contact Us');
        await elemVisible(this.smTaxResources, 'submenu Tax Resources');
        await elemVisible(this.smFees, 'submenu Fees');
        await elemVisible(this.smGlossary, 'submenu Glossary');
        await elemVisible(this.smCustodialServices, 'submenu Custodial Services');
        await elemVisible(this.smComplianceResources, 'submenu Compliance Resources');
        await elemVisible(this.smMarketingResources, 'submenu Marketing Resources');
        await elemVisible(this.smEvents, 'submenu Events');
        await elemVisible(this.smRMDResources, 'submenu RMD Resources');
    }

}
