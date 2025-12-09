import { expect, type Locator, type Page } from "@playwright/test";

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
        await expect(this.hHelpSupport).toBeVisible({ timeout: 1000000 });

        console.log('on Page Help and Support');
    }

    async goToPage(){
        await this.page.goto('/administration');
    }

    async SubMenusExist() {
        await expect(this.smKnowledgeBase).toBeVisible();
        await expect(this.smContactUs).toBeVisible();
        await expect(this.smTaxResources).toBeVisible();
        await expect(this.smFees).toBeVisible();
        await expect(this.smGlossary).toBeVisible();
        await expect(this.smCustodialServices).toBeVisible();
        await expect(this.smComplianceResources).toBeVisible();
        await expect(this.smMarketingResources).toBeVisible();
        await expect(this.smEvents).toBeVisible();
        await expect(this.smRMDResources).toBeVisible();
    }

}
