import { type Locator, type Page } from "@playwright/test";
import { BrowserActions } from '../../functions/fBrowser';
import { ElementHelper } from '../../functions/fElement';

type Logger = (msg: string) => Promise<void>;

export class OverviewPage {
    readonly page: Page;
    private fBrowser: BrowserActions;
    private fElement: ElementHelper;

    // --- Page Sections & Controls ---
    readonly secDashboardPage: Locator;
    readonly ddlAdvisorID: Locator;
    readonly secRotator: Locator;

    constructor(page: Page, logger: Logger) {
        this.page = page;
        this.fBrowser = new BrowserActions(page, logger);
        this.fElement = new ElementHelper(logger);

        this.secDashboardPage = page.locator('.dashboard-page');
        this.ddlAdvisorID = page.locator('button[role="combobox"] label[title="All"]');
        this.secRotator = page.locator('.max-w-screen-2xl.m-auto.px-4.mt-2');
    }

    // ==========================================================
    // 🔍 Validation Checks
    // ==========================================================
    async ElementsExist() {
        await this.fElement.log('📢 Verifying Overview page elements...');
        await this.fElement.elemVisible(this.secRotator, 'Rotator Section', 30000);
        await this.fElement.elemVisible(this.secDashboardPage, 'Dashboard Page Section');
        await this.fElement.log('✅ Landed on Page: Dashboard > Overview');
    }
}