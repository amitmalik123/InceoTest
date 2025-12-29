
import { expect, type Locator, type Page } from "@playwright/test";
import { elemVisible } from '../../functions/fElementHelper';

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
    readonly secFees: Locator;
    constructor(page: Page) {
        this.page = page;

        this.hDashboard = page.locator('h1[class*="pageHeader"]:has-text("Dashboard")');
        this.smOverview = page.getByRole('link', { name: 'Overview' });
        this.smInsights = page.getByRole('link', { name: 'Insights' });
        this.smAdvisorBenefits = page.getByRole('link', { name: 'Advisor Benefits' });
        this.smStatementsReports = page.getByRole('link', { name: 'Statements & Reports' });
        // this.btnManageAccounts = page.locator('button', { hasText: 'Manage Accounts' });
        this.btnManageAccounts = page.locator('button.PRIMARY', { hasText: 'Manage Accounts' });
        this.txtWelcome = page.locator("h3:has-text('Your Desired Text')")
        this.btnTitleManager = page.getByTestId('button-actions-edit');
        this.secFees = page.locator('[class="react-grid-layout min-h-[calc(100vh-230px)] pt-6 pb-4 px-0"]');

    }

    async goToPage(){
        await this.page.goto('/dashboard');
    }

    async LoadsPage() {
        await elemVisible(this.hDashboard, 'Heading Dashboard', undefined, 1000000);
        console.log('on Landing Page Dashboard');
    }

    async SubMenusExist() {
        await elemVisible(this.smInsights, 'submenu Insights');
        await elemVisible(this.smAdvisorBenefits, 'submenu Advisor Benefits');
        await elemVisible(this.smStatementsReports, 'submenu Statements & Reports');
        await elemVisible(this.btnManageAccounts, 'button Manage Accounts');
    }
}
