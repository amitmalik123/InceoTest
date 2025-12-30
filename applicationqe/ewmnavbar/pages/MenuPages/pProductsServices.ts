import { type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class ProductsServicesPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    readonly hProductsServices: Locator;
    
    // --- Sub Menus ---
    readonly smBusinessConsulting: Locator;
    readonly smLending: Locator;
    readonly smFinancialPlanning: Locator;
    readonly smRetirementServices: Locator;
    
    // --- Buttons ---
    readonly btnContactUs: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        this.hProductsServices = page.locator('h1[class*="pageHeader"]:has-text("Products & Services")');
        
        // Navigation Links
        this.smBusinessConsulting = page.getByRole('link', { name: 'Business Consulting', exact: true });
        this.smLending = page.getByRole('link', { name: 'Lending', exact: true });
        this.smFinancialPlanning = page.getByRole('link', { name: 'Financial Planning', exact: true });
        this.smRetirementServices = page.getByRole('link', { name: 'Retirement Services', exact: true });
        
        this.btnContactUs = page.locator('button', { hasText: 'Contact Us' });
    }

    // ==========================================================
    // 🧭 Navigation
    // ==========================================================
    async goToPage() {
        await this.fBrowser.goToURL('/practice-management');
        await this.fElement.log('Navigating to Products & Services Page');
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.hProductsServices, 'Products & Services Header');
        await this.fElement.log('✅ Landed on Page: Products & Services');
    }

    async SubMenusExist() {
        await this.fElement.log('📢 Verifying Products & Services Submenus...');

        await this.fElement.elemVisible(this.smBusinessConsulting, 'submenu Business Consulting');
        await this.fElement.elemVisible(this.smLending, 'submenu Lending');
        await this.fElement.elemVisible(this.smFinancialPlanning, 'submenu Financial Planning');
        await this.fElement.elemVisible(this.smRetirementServices, 'submenu Retirement Services');
        
        // Optional/Future items
        // await this.fElement.elemVisible(this.btnContactUs, 'button Contact Us');

        await this.fElement.log('✅ All Products & Services submenus are visible.');
    }
}