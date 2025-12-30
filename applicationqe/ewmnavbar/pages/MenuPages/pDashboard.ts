import { type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class DashboardPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    // --- Header & Submenus ---
    readonly hDashboard: Locator;
    readonly smOverview: Locator;
    readonly smInsights: Locator;
    readonly smAdvisorBenefits: Locator;
    readonly smStatementsReports: Locator;

    // --- Action Buttons & Content ---
    readonly btnManageAccounts: Locator;
    readonly btnTitleManager: Locator;
    readonly txtWelcome: Locator;
    readonly secFees: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        this.hDashboard = page.locator('h1[class*="pageHeader"]:has-text("Dashboard")');
        
        this.smOverview = page.getByRole('link', { name: 'Overview' });
        this.smInsights = page.getByRole('link', { name: 'Insights' });
        this.smAdvisorBenefits = page.getByRole('link', { name: 'Advisor Benefits' });
        this.smStatementsReports = page.getByRole('link', { name: 'Statements & Reports' });
        
        this.btnManageAccounts = page.locator('button.PRIMARY', { hasText: 'Manage Accounts' });
        this.btnTitleManager = page.getByTestId('button-actions-edit');
        this.txtWelcome = page.locator("h3:has-text('Your Desired Text')"); 
        
        this.secFees = page.locator('[class="react-grid-layout min-h-[calc(100vh-230px)] pt-6 pb-4 px-0"]');
    }

    // ==========================================================
    // 🧭 Navigation
    // ==========================================================
    async goToPage() {
        await this.fBrowser.goToURL('/dashboard');
        await this.fElement.log('Navigating to Dashboard Page');
        await this.fElement.waitForElemVisible(this.hDashboard, 'Dashboard Header');
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async LoadsPage() {
        await this.fElement.waitForElemVisible(this.hDashboard, 'Heading Dashboard');
        await this.fElement.log('✅ Landed on Page: Dashboard');
    }

    async SubMenusExist() {
        await this.fElement.elemVisible(this.smOverview, 'submenu Overview');
        await this.fElement.elemVisible(this.smInsights, 'submenu Insights');
        await this.fElement.elemVisible(this.smAdvisorBenefits, 'submenu Advisor Benefits');
        await this.fElement.elemVisible(this.smStatementsReports, 'submenu Statements & Reports');
        await this.fElement.elemVisible(this.btnManageAccounts, 'button Manage Accounts');
    }
}