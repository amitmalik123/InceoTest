import { expect, type Locator, type Page } from "@playwright/test";

export class DashboardPage {
    readonly page: Page;
    readonly hDashboard: Locator;
    readonly smOverview: Locator;
    readonly smInsights: Locator;
    readonly smAdvisorBenefits: Locator;
    readonly smStatementsReports: Locator;
    readonly btnManageAccounts: Locator;
    readonly txtWelcome: Locator;
    readonly btnTitleManager: Locator;
    constructor(page: Page) {
        this.page = page;

        this.hDashboard = page.locator('h1[class*="pageHeader"]:has-text("Dashboard")');
        this.smOverview = page.getByRole('link', { name: 'Overview' });
        this.smInsights = page.getByRole('link', { name: 'Insights' });
        this.smAdvisorBenefits = page.getByRole('link', { name: 'Advisor Benefits' });
        this.smStatementsReports = page.getByRole('link', { name: 'Statements & Reports' });
        this.btnManageAccounts = page.locator('button', { hasText: 'Manage Accounts' });
        this.txtWelcome = page.locator("h3:has-text('Your Desired Text')")
        this.btnTitleManager = page.getByTestId('button-actions-edit');

    }

    async goToPage(){
        await this.page.goto('/dashboard');
    }

    async LoadsPage() {
        await expect(this.hDashboard).toBeVisible({ timeout: 1000000 });
        console.log('on Landing Page Dashboard');
    }

    async SubMenusExist() {
        await expect(this.smInsights).toBeVisible();
        await expect(this.smAdvisorBenefits).toBeVisible();
        await expect(this.smStatementsReports).toBeVisible();
        await expect(this.btnManageAccounts).toBeVisible();
    }
}
