import { expect, type Locator, type Page } from "@playwright/test";

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
        await expect(this.hProductsServices).toBeVisible({ timeout: 1000000 });
        console.log('on Page Products and Services');
    }

    async SubMenusExist() {
        await expect(this.smBusinessConsulting).toBeVisible();
        await expect(this.smLending).toBeVisible();
        await expect(this.smFinancialPlanning).toBeVisible();
        await expect(this.smRetirementServices).toBeVisible();
        await expect(this.btnContactUs).toBeVisible();
    }

}
