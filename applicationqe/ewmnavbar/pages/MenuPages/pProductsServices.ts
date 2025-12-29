
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';

export class ProductsServicesPage {
    readonly page: Page;
    readonly hProductsServices: Locator;
    readonly smBusinessConsulting: Locator;
    readonly smLending: Locator;
    readonly smFinancialPlanning: Locator;
    readonly smRetirementServices: Locator;
    readonly btnContactUs: Locator;
    // readonly smOne: Locator;

    constructor(page: Page) {
        this.page = page;
        this.hProductsServices = page.locator('h1[class*="pageHeader"]:has-text("Products & Services")');
        this.smBusinessConsulting = page.getByRole('link', { name: 'Business Consulting' });
        this.smLending = page.getByRole('link', { name: 'Lending' });
        this.smFinancialPlanning = page.getByRole('link', { name: 'Financial Planning' });
        this.smRetirementServices = page.getByRole('link', { name: 'Retirement Services' });
        this.btnContactUs = page.locator('button', { hasText: 'Contact Us' });
    }

    async goToPage(){
        await this.page.goto('/practice-management');
    }

    async LoadsPage() {
        await elemVisible(this.hProductsServices, 'Products & Services Header', undefined, 1000000);
        console.log('on Page Products and Services');
    }

    async SubMenusExist() {
        await elemVisible(this.smBusinessConsulting, 'submenu Business Consulting');
        await elemVisible(this.smLending, 'submenu Lending');
        await elemVisible(this.smFinancialPlanning, 'submenu Financial Planning');
        await elemVisible(this.smRetirementServices, 'submenu Retirement Services');
        // await elemVisible(this.btnContactUs, 'button Contact Us');
    }

}
